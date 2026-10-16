import os
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
from models.database import db
from models.student import Student
from models.certificate import Certificate
from models.verification import VerificationHistory
from models.user import User
from routes.auth import admin_required
from services.hashing import generate_certificate_hash, create_canonical_string
from services.blockchain import blockchain_service
from services.qr_code import generate_qr_code

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf', 'png', 'jpg', 'jpeg'}

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    total_certificates = Certificate.query.count()
    verified_certificates = Certificate.query.filter_by(blockchain_status='CONFIRMED').count()
    total_students = Student.query.count()
    total_verifications = VerificationHistory.query.count()
    failed_verifications = VerificationHistory.query.filter(VerificationHistory.result != 'VERIFIED').count()

    recent_certificates = Certificate.query.order_by(Certificate.created_at.desc()).limit(5).all()
    recent_verifications = VerificationHistory.query.order_by(VerificationHistory.verification_time.desc()).limit(5).all()

    return render_template(
        'admin/dashboard.html',
        total_certificates=total_certificates,
        verified_certificates=verified_certificates,
        total_students=total_students,
        total_verifications=total_verifications,
        failed_verifications=failed_verifications,
        recent_certificates=recent_certificates,
        recent_verifications=recent_verifications
    )

@admin_bp.route('/certificates')
@admin_required
def certificates():
    search_query = request.args.get('q', '').strip()
    if search_query:
        cert_list = Certificate.query.filter(
            (Certificate.certificate_id.like(f"%{search_query}%")) |
            (Certificate.student_id.like(f"%{search_query}%")) |
            (Certificate.course_name.like(f"%{search_query}%"))
        ).order_by(Certificate.created_at.desc()).all()
    else:
        cert_list = Certificate.query.order_by(Certificate.created_at.desc()).all()

    return render_template('admin/certificates.html', certificates=cert_list, search_query=search_query)

@admin_bp.route('/certificates/register', methods=['GET', 'POST'])
@admin_required
def register_certificate():
    if request.method == 'POST':
        student_name = request.form.get('student_name', '').strip()
        student_id = request.form.get('student_id', '').strip()
        student_email = request.form.get('student_email', '').strip()
        course_name = request.form.get('course_name', '').strip()
        certificate_id = request.form.get('certificate_id', '').strip()
        issuer = request.form.get('issuer', 'Infosys Springboard').strip()
        completion_date = request.form.get('completion_date', '').strip()

        # Validation
        if not all([student_name, student_id, student_email, course_name, certificate_id, completion_date]):
            flash('All mandatory fields must be filled out.', 'danger')
            return render_template('admin/register_certificate.html', form_data=request.form)

        # Check duplicate Certificate ID
        existing_cert = Certificate.query.filter_by(certificate_id=certificate_id).first()
        if existing_cert:
            flash(f'Certificate ID "{certificate_id}" already exists in the system.', 'warning')
            return render_template('admin/register_certificate.html', form_data=request.form)

        # File Upload Handling
        file_path = None
        if 'certificate_file' in request.files:
            file = request.files['certificate_file']
            if file and file.filename != '':
                if allowed_file(file.filename):
                    filename = secure_filename(f"{certificate_id}_{file.filename}")
                    upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'certificates')
                    os.makedirs(upload_dir, exist_ok=True)
                    full_path = os.path.join(upload_dir, filename)
                    file.save(full_path)
                    file_path = f"uploads/certificates/{filename}"
                else:
                    flash('Invalid file type. Allowed formats: PDF, PNG, JPG, JPEG.', 'danger')
                    return render_template('admin/register_certificate.html', form_data=request.form)

        # Step 1 & 2: Generate SHA-256 Hash from Canonical String
        cert_hash = generate_certificate_hash(student_id, certificate_id, course_name, issuer, completion_date)

        # Step 3: Check/Create Student in DB
        student = Student.query.filter_by(student_id=student_id).first()
        if not student:
            student = Student(student_id=student_id, name=student_name, email=student_email)
            db.session.add(student)

            # Check if student login user exists
            user_exists = User.query.filter_by(email=student_email).first()
            if not user_exists:
                student_user = User(
                    name=student_name,
                    email=student_email,
                    role='student'
                )
                student_user.set_password('student123')  # Default password for student demo
                db.session.add(student_user)
        else:
            # Update student details if changed
            student.name = student_name
            student.email = student_email

        db.session.commit()

        # Step 4: Write Certificate Record to DB
        new_cert = Certificate(
            certificate_id=certificate_id,
            student_id=student_id,
            course_name=course_name,
            issuer=issuer,
            completion_date=completion_date,
            certificate_hash=cert_hash,
            file_path=file_path,
            blockchain_status='PENDING'
        )
        db.session.add(new_cert)
        db.session.commit()

        # Step 5: Send Blockchain Transaction to Ganache Smart Contract
        tx_hash = None
        blockchain_status = 'PENDING'
        try:
            timestamp_epoch = int(datetime.strptime(completion_date, '%Y-%m-%d').timestamp()) if '-' in completion_date else int(datetime.utcnow().timestamp())
            tx_hash = blockchain_service.register_certificate_on_chain(
                certificate_id=certificate_id,
                certificate_hash=cert_hash,
                issuer=issuer,
                timestamp=timestamp_epoch
            )
            blockchain_status = 'CONFIRMED'
            flash(f'Certificate successfully stored on Ethereum Blockchain! Tx: {tx_hash}', 'success')
        except Exception as e:
            flash(f'Certificate registered in MySQL, but Blockchain registration warning: {e}', 'warning')

        new_cert.blockchain_tx_hash = tx_hash
        new_cert.blockchain_status = blockchain_status

        # Step 6: Generate QR Code pointing to verification URL
        base_url = request.host_url
        qr_path = generate_qr_code(certificate_id, base_url=base_url)
        new_cert.qr_code_path = qr_path

        db.session.commit()

        return redirect(url_for('admin.certificate_detail', cert_id=certificate_id))

    return render_template('admin/register_certificate.html')

@admin_bp.route('/certificates/<cert_id>')
@admin_required
def certificate_detail(cert_id):
    certificate = Certificate.query.filter_by(certificate_id=cert_id).first_or_404()
    canonical_str = create_canonical_string(
        certificate.student_id,
        certificate.certificate_id,
        certificate.course_name,
        certificate.issuer,
        certificate.completion_date
    )

    # Fetch directly from blockchain for live audit comparison
    onchain_data = None
    if blockchain_service.is_connected():
        onchain_data = blockchain_service.get_certificate_from_chain(certificate.certificate_id)

    return render_template(
        'admin/certificate_detail.html',
        certificate=certificate,
        canonical_str=canonical_str,
        onchain_data=onchain_data
    )

@admin_bp.route('/students')
@admin_required
def students():
    student_list = Student.query.order_by(Student.created_at.desc()).all()
    return render_template('admin/students.html', students=student_list)

@admin_bp.route('/verifications')
@admin_required
def verifications():
    history_list = VerificationHistory.query.order_by(VerificationHistory.verification_time.desc()).all()
    return render_template('admin/verifications.html', verifications=history_list)
