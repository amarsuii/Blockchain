import os
from flask import Flask, render_template
from flask_cors import CORS
from config import Config
from models.database import db

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize CORS
    CORS(app)

    # Database Initialization & Fallback Handler
    try:
        # Test connecting to MySQL or Fallback to SQLite
        from sqlalchemy import create_engine
        engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
        engine.connect()
        print(f"[+] Connected to Primary Database: {app.config['SQLALCHEMY_DATABASE_URI']}")
    except Exception as e:
        print(f"[!] Primary MySQL database connection notice ({e}). Switching to SQLite fallback...")
        os.makedirs(os.path.dirname(app.config['SQLITE_PATH']), exist_ok=True)
        app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLITE_URI']

    db.init_app(app)

    # Ensure Upload Directories Exist
    os.makedirs(app.config['CERTIFICATE_UPLOADS'], exist_ok=True)
    os.makedirs(app.config['QR_UPLOADS'], exist_ok=True)

    # Register Blueprints
    from routes.auth import auth_bp
    from routes.admin import admin_bp
    from routes.student import student_bp
    from routes.verification import verification_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(verification_bp)

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('verification/result.html', status='NOT_FOUND', cert_id='', message='Page or Certificate Not Found.'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('index.html'), 500

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
