from datetime import datetime
from models.database import db

class Certificate(db.Model):
    __tablename__ = 'certificates'

    id = db.Column(db.Integer, primary_key=True)
    certificate_id = db.Column(db.String(100), unique=True, nullable=False, index=True)
    student_id = db.Column(db.String(50), db.ForeignKey('students.student_id'), nullable=False)
    course_name = db.Column(db.String(150), nullable=False)
    issuer = db.Column(db.String(100), nullable=False, default='Infosys Springboard')
    completion_date = db.Column(db.String(20), nullable=False)
    certificate_hash = db.Column(db.String(64), nullable=False)
    blockchain_tx_hash = db.Column(db.String(66), nullable=True)
    blockchain_status = db.Column(db.String(20), nullable=False, default='PENDING')  # 'CONFIRMED', 'PENDING', 'FAILED'
    qr_code_path = db.Column(db.String(255), nullable=True)
    file_path = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship to verification history
    verifications = db.relationship('VerificationHistory', backref='certificate', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'certificate_id': self.certificate_id,
            'student_id': self.student_id,
            'student_name': self.student.name if self.student else 'Unknown',
            'course_name': self.course_name,
            'issuer': self.issuer,
            'completion_date': self.completion_date,
            'certificate_hash': self.certificate_hash,
            'blockchain_tx_hash': self.blockchain_tx_hash,
            'blockchain_status': self.blockchain_status,
            'qr_code_path': self.qr_code_path,
            'file_path': self.file_path,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else ''
        }
