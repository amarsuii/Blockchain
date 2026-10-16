import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    BASE_DIR = BASE_DIR
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key_cert_verify')
    
    # Upload directories
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    CERTIFICATE_UPLOADS = os.path.join(UPLOAD_FOLDER, 'certificates')
    QR_UPLOADS = os.path.join(UPLOAD_FOLDER, 'qrcodes')
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB Max

    # MySQL Configuration
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '3306')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'root')
    DB_NAME = os.getenv('DB_NAME', 'cert_verification_db')

    # Primary Database URI (MySQL)
    MYSQL_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    # Fallback Database URI (SQLite for zero-config demo when MySQL server is not active)
    SQLITE_PATH = os.path.join(BASE_DIR, 'instance', 'cert_verification.db')
    SQLITE_URI = f"sqlite:///{SQLITE_PATH}"

    # Default to MySQL, fallback logic handled in application factory
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', MYSQL_URI)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Blockchain (Ganache) Configuration
    BLOCKCHAIN_RPC_URL = os.getenv('BLOCKCHAIN_RPC_URL', 'http://127.0.0.1:7545')
    CONTRACT_ADDRESS = os.getenv('CONTRACT_ADDRESS', '')
    BLOCKCHAIN_PRIVATE_KEY = os.getenv('BLOCKCHAIN_PRIVATE_KEY', '0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d')
    ADMIN_ACCOUNT_ADDRESS = os.getenv('ADMIN_ACCOUNT_ADDRESS', '0x90F8bf6A479f320ead074411a4B0e5744ea61115')
