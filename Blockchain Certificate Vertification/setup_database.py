import os
from app import create_app
from models.database import db
from models.user import User
from models.student import Student

def setup_database():
    app = create_app()
    with app.app_context():
        print("[+] Creating database tables...")
        db.create_all()

        # Seed Default Admin Account if missing
        admin_user = User.query.filter_by(email='admin@certverify.org').first()
        if not admin_user:
            print("[+] Seeding Default Admin Account (admin@certverify.org)...")
            admin_user = User(
                name='College Administrator',
                email='admin@certverify.org',
                role='admin'
            )
            admin_user.set_password('admin123')
            db.session.add(admin_user)

        # Seed Default Student Account if missing
        student_user = User.query.filter_by(email='student@certverify.org').first()
        if not student_user:
            print("[+] Seeding Default Student Account (student@certverify.org)...")
            student_user = User(
                name='Demo Student',
                email='student@certverify.org',
                role='student'
            )
            student_user.set_password('student123')
            db.session.add(student_user)

            student_record = Student(
                student_id='STU001',
                name='Demo Student',
                email='student@certverify.org'
            )
            db.session.add(student_record)

        db.session.commit()
        print("[OK] Database setup completed successfully!")

if __name__ == '__main__':
    setup_database()
