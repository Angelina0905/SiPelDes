from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    CORS(app)

    import os
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'rahasia123')

    db.init_app(app)

    from app.routes.surat import surat_bp
    from app.routes.pengaduan import pengaduan_bp
    from app.routes.auth import auth_bp

    app.register_blueprint(surat_bp, url_prefix='/api/surat')
    app.register_blueprint(pengaduan_bp, url_prefix='/api/pengaduan')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    with app.app_context():
        db.create_all()

    return app