from datetime import datetime
from models.database import db

class VerificationHistory(db.Model):
    __tablename__ = 'verification_history'

    id = db.Column(db.Integer, primary_key=True)
    certificate_id = db.Column(db.String(100), db.ForeignKey('certificates.certificate_id'), nullable=False, index=True)
    verification_time = db.Column(db.DateTime, default=datetime.utcnow)
    result = db.Column(db.String(30), nullable=False)  # 'VERIFIED', 'FAILED', 'NOT_FOUND'
    verification_method = db.Column(db.String(50), nullable=False, default='Certificate ID')  # 'Certificate ID', 'QR Code'

    def to_dict(self):
        return {
            'id': self.id,
            'certificate_id': self.certificate_id,
            'verification_time': self.verification_time.strftime('%Y-%m-%d %H:%M:%S') if self.verification_time else '',
            'result': self.result,
            'verification_method': self.verification_method
        }
