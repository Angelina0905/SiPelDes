from flask import Blueprint, request, jsonify
from app import db
from app.models.surat import Surat
from app.utils.s3_helper import upload_file
from datetime import datetime
import random, string

surat_bp = Blueprint('surat', __name__)

def generate_tiket():
    tahun = datetime.now().year
    kode = ''.join(random.choices(string.digits, k=5))
    return f"SPD-{tahun}-{kode}"

@surat_bp.route('/', methods=['POST'])
def ajukan_surat():
    nama      = request.form.get('nama')
    nik       = request.form.get('nik')
    no_hp     = request.form.get('no_hp')
    jenis     = request.form.get('jenis')
    keperluan = request.form.get('keperluan')

    if not nama or not nik or not jenis:
        return jsonify({'error': 'Nama, NIK, dan jenis wajib diisi'}), 400

    file_url = None
    if 'file' in request.files:
        f = request.files['file']
        if f.filename:
            file_url = upload_file(f, folder='surat')

    surat = Surat(
        tiket=generate_tiket(),
        nama=nama, nik=nik, no_hp=no_hp,
        jenis=jenis, keperluan=keperluan,
        file_url=file_url
    )
    db.session.add(surat)
    db.session.commit()

    return jsonify({'message': 'Pengajuan berhasil', 'tiket': surat.tiket}), 201

@surat_bp.route('/status/<tiket>', methods=['GET'])
def cek_status(tiket):
    surat = Surat.query.filter_by(tiket=tiket).first()
    if not surat:
        return jsonify({'error': 'Tiket tidak ditemukan'}), 404
    return jsonify({
        'tiket'  : surat.tiket,
        'nama'   : surat.nama,
        'jenis'  : surat.jenis,
        'status' : surat.status,
        'tgl'    : surat.created_at.strftime('%d %b %Y')
    })

@surat_bp.route('/all', methods=['GET'])
def get_all():
    semua = Surat.query.order_by(Surat.created_at.desc()).all()
    return jsonify([{
        'tiket' : s.tiket,
        'nama'  : s.nama,
        'jenis' : s.jenis,
        'status': s.status,
        'tgl'   : s.created_at.strftime('%d %b %Y')
    } for s in semua])

@surat_bp.route('/update/<tiket>', methods=['PUT'])
def update_status(tiket):
    surat = Surat.query.filter_by(tiket=tiket).first()
    if not surat:
        return jsonify({'error': 'Tidak ditemukan'}), 404
    surat.status = request.json.get('status', surat.status)
    db.session.commit()
    return jsonify({'message': 'Status diperbarui'})