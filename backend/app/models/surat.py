from app import db
from datetime import datetime
import uuid

class Surat(db.Model):
    __tablename__ = 'surat'

    id         = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tiket      = db.Column(db.String(30), unique=True, nullable=False)
    nama       = db.Column(db.String(100), nullable=False)
    nik        = db.Column(db.String(20), nullable=False)
    no_hp      = db.Column(db.String(20))
    jenis      = db.Column(db.String(100), nullable=False)
    keperluan  = db.Column(db.Text)
    file_url   = db.Column(db.String(500))
    status     = db.Column(db.String(50), default='Diterima')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)