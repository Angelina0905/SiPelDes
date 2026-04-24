from flask import Blueprint, request, jsonify
import pymysql
import os
import uuid
from ..utils.s3_helper import upload_to_s3

surat_bp = Blueprint('surat', __name__)

def get_db_connection():
    return pymysql.connect(
        host=os.getenv('DB_HOST'), user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'), database=os.getenv('DB_NAME'),
        cursorclass=pymysql.cursors.DictCursor
    )

@surat_bp.route('/submit', methods=['POST'])
def submit_surat():
    nama = request.form.get('nama')
    file = request.files.get('file_dokumen')

    if not nama or not file:
        return jsonify({"error": "Data tidak lengkap"}), 400

    file_url = upload_to_s3(file)
    if not file_url:
        return jsonify({"error": "Gagal upload ke S3"}), 500

    tiket = f"SRT-{uuid.uuid4().hex[:6].upper()}"
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = "INSERT INTO pengajuan_surat (nama, file_url, status, tiket) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (nama, file_url, "Menunggu Verifikasi", tiket))
        conn.commit()
    finally:
        conn.close()

    return jsonify({"message": "Berhasil", "tiket": tiket, "file_url": file_url})