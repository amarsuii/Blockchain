from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.user import User
from models.student import Student

auth_bp = Blueprint('auth', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in as an administrator.', 'warning')
            return redirect(url_for('auth.login'))
        if session.get('role') != 'admin':
            flash('Access restricted to administrators only.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def student_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in as a student.', 'warning')
            return redirect(url_for('auth.login'))
        if session.get('role') != 'student':
            flash('Access restricted to student accounts.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('student.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        if not email or not password:
            flash('Email and Password are required.', 'danger')
            return render_template('login.html', email=email)

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['user_email'] = user.email
            session['role'] = user.role

            # If user is a student, store student_id in session
            if user.role == 'student':
                student_record = Student.query.filter_by(email=user.email).first()
                if student_record:
                    session['student_id'] = student_record.student_id

            flash(f'Welcome back, {user.name}!', 'success')
            if user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('student.dashboard'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')
            return render_template('login.html', email=email)

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been successfully logged out.', 'info')
    return redirect(url_for('auth.login'))
