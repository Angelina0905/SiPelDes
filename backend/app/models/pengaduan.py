from app import db
from datetime import datetime
import uuid

class Pengaduan(db.Model):
    __tablename__ = 'pengaduan'

    id         = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tiket      = db.Column(db.String(30), unique=True, nullable=False)
    nama       = db.Column(db.String(100), nullable=False)
    no_hp      = db.Column(db.String(20))
    isi        = db.Column(db.Text, nullable=False)
    foto_url   = db.Column(db.String(500))
    status     = db.Column(db.String(50), default='Belum Ditangani')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)