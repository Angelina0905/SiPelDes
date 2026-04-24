from flask import Flask

def create_app():
    app = Flask(__name__)

    # register routes
    from app.routes.pengaduan import pengaduan_bp
    from app.routes.surat import surat_bp
    from app.routes.tracking import tracking_bp

    app.register_blueprint(pengaduan_bp)
    app.register_blueprint(surat_bp)
    app.register_blueprint(tracking_bp)

    return app