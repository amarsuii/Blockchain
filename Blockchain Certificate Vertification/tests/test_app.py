import os
import pytest
from app import create_app
from models.database import db
from models.user import User
from models.student import Student
from models.certificate import Certificate
from services.hashing import generate_certificate_hash, create_canonical_string
from services.qr_code import generate_qr_code

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
    app.config['WTF_CSRF_ENABLED'] = False

    with app.test_client() as client:
        with app.app_context():
            db.session.remove()
            db.drop_all()
            db.create_all()

            # Seed Admin
            admin = User(name='Test Admin', email='admin@test.com', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)

            # Seed Student
            student = Student(student_id='STU001', name='Demo Student', email='student@test.com')
            db.session.add(student)

            student_user = User(name='Demo Student', email='student@test.com', role='student')
            student_user.set_password('student123')
            db.session.add(student_user)

            db.session.commit()
        yield client
        with app.app_context():
            db.session.remove()
            db.drop_all()

def test_hashing_constancy():
    """Verify that same certificate data always produces identical SHA-256 hash."""
    hash1 = generate_certificate_hash('STU001', 'CERT001', 'Python', 'Infosys Springboard', '2026-08-10')
    hash2 = generate_certificate_hash('STU001', 'CERT001', 'Python', 'Infosys Springboard', '2026-08-10')
    assert hash1 == hash2
    assert len(hash1) == 64

def test_tampered_hashing():
    """Verify that modifying any field produces a completely different hash."""
    original_hash = generate_certificate_hash('STU001', 'CERT001', 'Python', 'Infosys Springboard', '2026-08-10')
    tampered_hash = generate_certificate_hash('STU001', 'CERT001', 'Java', 'Infosys Springboard', '2026-08-10')
    assert original_hash != tampered_hash

def test_login_success(client):
    """Test valid admin login."""
    response = client.post('/login', data={'email': 'admin@test.com', 'password': 'admin123'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Administrator Dashboard' in response.data or b'Welcome back' in response.data

def test_login_invalid(client):
    """Test invalid credentials."""
    response = client.post('/login', data={'email': 'admin@test.com', 'password': 'wrongpassword'}, follow_redirects=True)
    assert b'Invalid email or password' in response.data

def test_unauthorized_access(client):
    """Test unauthorized page redirection."""
    response = client.get('/admin/dashboard', follow_redirects=True)
    assert b'Please log in' in response.data

def test_certificate_registration_and_verification(client):
    """Test end-to-end certificate registration and public verification flow."""
    # Login as admin
    client.post('/login', data={'email': 'admin@test.com', 'password': 'admin123'})

    # Register new certificate
    cert_data = {
        'student_name': 'Demo Student',
        'student_id': 'STU001',
        'student_email': 'student@test.com',
        'course_name': 'Machine Learning',
        'certificate_id': 'CERT999',
        'issuer': 'Infosys Springboard',
        'completion_date': '2026-08-10'
    }
    res = client.post('/admin/certificates/register', data=cert_data, follow_redirects=True)
    assert res.status_code == 200

    # Public Verification check
    verify_res = client.get('/verify/CERT999')
    assert verify_res.status_code == 200
    assert b'CERTIFICATE VERIFIED' in verify_res.data or b'CERT999' in verify_res.data

def test_non_existing_verification(client):
    """Test public verification for non-existent certificate."""
    verify_res = client.get('/verify/INVALID_ID_999')
    assert b'RECORD NOT FOUND' in verify_res.data or b'not found' in verify_res.data

def test_qr_code_generation():
    """Test QR Code generator outputs image file."""
    qr_rel_path = generate_qr_code('TEST_QR_001')
    assert 'uploads/qrcodes/qr_TEST_QR_001.png' in qr_rel_path
