from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

def create_app():
    load_dotenv()
    app = Flask(__name__)
    CORS(app)

    # Register Blueprints (Routes)
    from .routes import surat, pengaduan, tracking
    app.register_blueprint(surat.bp, url_prefix='/surat')
    app.register_blueprint(pengaduan.bp, url_prefix='/pengaduan')
    app.register_blueprint(tracking.bp, url_prefix='/tracking')

    return app