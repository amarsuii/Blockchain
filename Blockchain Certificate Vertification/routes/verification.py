from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.database import db
from models.certificate import Certificate
from models.verification import VerificationHistory
from services.hashing import generate_certificate_hash, create_canonical_string
from services.blockchain import blockchain_service

verification_bp = Blueprint('verification', __name__)

@verification_bp.route('/verify', methods=['GET', 'POST'])
def verify_search():
    if request.method == 'POST':
        cert_id = request.form.get('certificate_id', '').strip()
        if not cert_id:
            flash('Please enter a valid Certificate ID.', 'warning')
            return render_template('verification/verify.html')

        return redirect(url_for('verification.verify_result', cert_id=cert_id))

    return render_template('verification/verify.html')

@verification_bp.route('/verify/<cert_id>')
def verify_result(cert_id):
    cert_id = cert_id.strip()
    method = request.args.get('method', 'Certificate ID')
    
    # 1. Fetch record from MySQL
    certificate = Certificate.query.filter_by(certificate_id=cert_id).first()

    if not certificate:
        # Record failed search in verification history
        history = VerificationHistory(
            certificate_id=cert_id,
            result='NOT_FOUND',
            verification_method=method
        )
        db.session.add(history)
        db.session.commit()

        return render_template(
            'verification/result.html',
            status='NOT_FOUND',
            cert_id=cert_id,
            message='Certificate record was not found in the official registry.'
        )

    # 2 & 3. Reconstruct canonical string and generate fresh SHA-256 hash
    recalculated_hash = generate_certificate_hash(
        certificate.student_id,
        certificate.certificate_id,
        certificate.course_name,
        certificate.issuer,
        certificate.completion_date
    )

    canonical_str = create_canonical_string(
        certificate.student_id,
        certificate.certificate_id,
        certificate.course_name,
        certificate.issuer,
        certificate.completion_date
    )

    # 4 & 5. Retrieve stored hash from blockchain and compare
    onchain_data = None
    onchain_hash = certificate.certificate_hash
    blockchain_connected = blockchain_service.is_connected()
    hash_matches = False
    blockchain_verified = False

    if blockchain_connected:
        try:
            onchain_data = blockchain_service.get_certificate_from_chain(cert_id)
            if onchain_data:
                onchain_hash = onchain_data['certificate_hash']
                blockchain_verified = blockchain_service.verify_certificate_on_chain(cert_id, recalculated_hash)
            else:
                blockchain_verified = False
        except Exception as e:
            print(f"[!] On-chain lookup failed: {e}")

    # Fallback hash check if blockchain is not connected in demo offline mode
    if not blockchain_connected:
        hash_matches = (recalculated_hash == certificate.certificate_hash)
    else:
        hash_matches = (recalculated_hash == onchain_hash and blockchain_verified)

    # Record verification attempt
    result_status = 'VERIFIED' if hash_matches else 'FAILED'
    history = VerificationHistory(
        certificate_id=cert_id,
        result=result_status,
        verification_method=method
    )
    db.session.add(history)
    db.session.commit()

    return render_template(
        'verification/result.html',
        status=result_status,
        certificate=certificate,
        recalculated_hash=recalculated_hash,
        onchain_hash=onchain_hash,
        canonical_str=canonical_str,
        blockchain_connected=blockchain_connected,
        blockchain_verified=blockchain_verified,
        onchain_data=onchain_data
    )
