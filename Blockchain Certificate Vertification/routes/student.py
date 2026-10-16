from flask import Blueprint, render_template, session, redirect, url_for, flash
from models.student import Student
from models.certificate import Certificate
from routes.auth import student_required

student_bp = Blueprint('student', __name__, url_prefix='/student')

@student_bp.route('/dashboard')
@student_required
def dashboard():
    student_email = session.get('user_email')
    student = Student.query.filter_by(email=student_email).first()

    if not student:
        flash('Student record not found.', 'danger')
        return redirect(url_for('auth.logout'))

    certificates = Certificate.query.filter_by(student_id=student.student_id).all()
    return render_template('student/dashboard.html', student=student, certificates=certificates)

@student_bp.route('/certificates')
@student_required
def certificates():
    student_email = session.get('user_email')
    student = Student.query.filter_by(email=student_email).first()
    
    if not student:
        flash('Student record not found.', 'danger')
        return redirect(url_for('auth.logout'))

    certificates = Certificate.query.filter_by(student_id=student.student_id).all()
    return render_template('student/certificates.html', student=student, certificates=certificates)
