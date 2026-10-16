import os
from datetime import datetime
from app import create_app
from models.database import db
from models.student import Student
from models.certificate import Certificate
from services.hashing import generate_certificate_hash
from services.blockchain import blockchain_service
from services.qr_code import generate_qr_code

def seed_demo_data():
    app = create_app()
    with app.app_context():
        print("[+] Seeding Demo Certificate Data...")

        student_id = "STU001"
        certificate_id = "CERT001"
        course_name = "Python Programming"
        issuer = "Infosys Springboard"
        completion_date = "2026-08-10"

        # Ensure student exists
        student = Student.query.filter_by(student_id=student_id).first()
        if not student:
            student = Student(student_id=student_id, name="Demo Student", email="student@certverify.org")
            db.session.add(student)
            db.session.commit()

        # Check existing certificate
        existing_cert = Certificate.query.filter_by(certificate_id=certificate_id).first()
        if existing_cert:
            print(f"[!] Demo Certificate {certificate_id} already exists in database.")
            return

        # 1. Generate SHA-256 Hash
        cert_hash = generate_certificate_hash(student_id, certificate_id, course_name, issuer, completion_date)
        print(f"[+] Canonical Hash for {certificate_id}: {cert_hash}")

        # 2. Blockchain Smart Contract Commitment
        tx_hash = None
        status = 'PENDING'
        try:
            if blockchain_service.is_connected():
                timestamp_epoch = int(datetime.strptime(completion_date, '%Y-%m-%d').timestamp())
                tx_hash = blockchain_service.register_certificate_on_chain(
                    certificate_id=certificate_id,
                    certificate_hash=cert_hash,
                    issuer=issuer,
                    timestamp=timestamp_epoch
                )
                status = 'CONFIRMED'
                print(f"[OK] On-Chain Blockchain Tx Hash: {tx_hash}")
            else:
                print("[!] Local Ganache node not connected. Storing certificate in DB with PENDING blockchain status.")
        except Exception as e:
            print(f"[!] Blockchain commitment notice: {e}")

        # 3. Generate QR Code
        qr_path = generate_qr_code(certificate_id, base_url="http://localhost:5000")

        # 4. Save Record in Database
        cert = Certificate(
            certificate_id=certificate_id,
            student_id=student_id,
            course_name=course_name,
            issuer=issuer,
            completion_date=completion_date,
            certificate_hash=cert_hash,
            blockchain_tx_hash=tx_hash,
            blockchain_status=status,
            qr_code_path=qr_path
        )

        db.session.add(cert)
        db.session.commit()
        print(f"[OK] Demo Certificate {certificate_id} successfully registered!")

if __name__ == '__main__':
    seed_demo_data()
