import os
import qrcode
from config import Config

def generate_qr_code(certificate_id: str, base_url: str = "http://localhost:5000") -> str:
    """
    Generates a QR code PNG pointing to the public certificate verification page.
    Returns relative image path string.
    """
    target_url = f"{base_url.rstrip('/')}/verify/{certificate_id}"
    
    # Ensure QR output directory exists
    qr_dir = Config.QR_UPLOADS
    os.makedirs(qr_dir, exist_ok=True)
    
    filename = f"qr_{certificate_id}.png"
    filepath = os.path.join(qr_dir, filename)

    # Configure QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(target_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="#0f172a", back_color="#ffffff")
    img.save(filepath)

    relative_path = f"uploads/qrcodes/{filename}"
    return relative_path
