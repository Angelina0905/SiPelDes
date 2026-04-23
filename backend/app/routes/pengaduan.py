from flask import Blueprint, request, jsonify
from app import db
from app.models.pengaduan import Pengaduan
from app.utils.s3_helper import upload_file
from datetime import datetime
import random, string

pengaduan_bp = Blueprint('pengaduan', __name__)

def generate_tiket():
    tahun = datetime.now().year
    kode = ''.join(random.choices(string.digits, k=5))
    return f"PDU-{tahun}-{kode}"

@pengaduan_bp.route('/', methods=['POST'])
def kirim_pengaduan():
    nama  = request.form.get('nama')
    no_hp = request.form.get('no_hp')
    isi   = request.form.get('isi')

    if not nama or not isi:
        return jsonify({'error': 'Nama dan isi wajib diisi'}), 400

    foto_url = None
    if 'foto' in request.files:
        f = request.files['foto']
        if f.filename:
            foto_url = upload_file(f, folder='pengaduan')

    pgd = Pengaduan(
        tiket=generate_tiket(),
        nama=nama, no_hp=no_hp,
        isi=isi, foto_url=foto_url
    )
    db.session.add(pgd)
    db.session.commit()

    return jsonify({'message': 'Pengaduan terkirim', 'tiket': pgd.tiket}), 201

@pengaduan_bp.route('/all', methods=['GET'])
def get_all():
    semua = Pengaduan.query.order_by(Pengaduan.created_at.desc()).all()
    return jsonify([{
        'tiket' : p.tiket,
        'nama'  : p.nama,
        'isi'   : p.isi[:80],
        'status': p.status,
        'tgl'   : p.created_at.strftime('%d %b %Y')
    } for p in semua])