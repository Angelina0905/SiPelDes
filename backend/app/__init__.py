from flask import Flask
from app.routes.surat import surat_bp

def create_app():
    app = Flask(__name__)

    app.register_blueprint(surat_bp, url_prefix="/api/surat")

    return app