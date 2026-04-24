from flask import Blueprint, request, jsonify
import pymysql
import os

tracking_bp = Blueprint('tracking', __name__)

def get_db_connection():
    return pymysql.connect(
        host=os.getenv('DB_HOST'), user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'), database=os.getenv('DB_NAME'),
        cursorclass=pymysql.cursors.DictCursor
    )

@tracking_bp.route('/cek', methods=['GET'])
def cek_status():
    tiket = request.args.get('tiket')
    if not tiket:
        return jsonify({"error": "Nomor tiket wajib diisi"}), 400

    conn = get_db_connection()
    data = None
    try:
        with conn.cursor() as cursor:
            # Cek di tabel surat
            if tiket.startswith("SRT-"):
                cursor.execute("SELECT * FROM pengajuan_surat WHERE tiket=%s", (tiket,))
                data = cursor.fetchone()
            # Cek di tabel pengaduan
            elif tiket.startswith("PGD-"):
                cursor.execute("SELECT * FROM laporan_pengaduan WHERE tiket=%s", (tiket,))
                data = cursor.fetchone()
    finally:
        conn.close()

    if data:
        return jsonify({"status": "Ditemukan", "data": data})
    return jsonify({"error": "Tiket tidak ditemukan"}), 404