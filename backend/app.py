from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import uuid
import pymysql
import boto3
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

# =========================
# KONEKSI RDS
# =========================
def get_db():
    return pymysql.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        cursorclass=pymysql.cursors.DictCursor
    )

# =========================
# BUAT TABEL (auto saat start)
# =========================
def init_db():
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS pengaduan (
                id INT AUTO_INCREMENT PRIMARY KEY,
                tiket VARCHAR(20) UNIQUE NOT NULL,
                laporan TEXT NOT NULL,
                foto_url VARCHAR(500),
                status VARCHAR(50) DEFAULT 'Sedang Diproses',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS surat (
                id INT AUTO_INCREMENT PRIMARY KEY,
                tiket VARCHAR(20) UNIQUE NOT NULL,
                nama VARCHAR(100) NOT NULL,
                nik VARCHAR(20) NOT NULL,
                no_hp VARCHAR(20),
                jenis VARCHAR(100) NOT NULL,
                keperluan TEXT,
                file_url VARCHAR(500),
                status VARCHAR(50) DEFAULT 'Diterima',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    conn.commit()
    conn.close()

# =========================
# UPLOAD KE S3
# =========================
def upload_to_s3(file_obj, folder='uploads'):
    s3 = boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_REGION', 'ap-southeast-1')
    )
    bucket = os.getenv('S3_BUCKET')
    filename = f"{folder}/{uuid.uuid4()}_{secure_filename(file_obj.filename)}"
    s3.upload_fileobj(
        file_obj, bucket, filename,
        ExtraArgs={'ContentType': file_obj.content_type}
    )
    region = os.getenv('AWS_REGION', 'ap-southeast-1')
    return f"https://{bucket}.s3.{region}.amazonaws.com/{filename}"

# =========================
# ROOT
# =========================
@app.route("/")
def home():
    return "Backend SiPelDes jalan dengan RDS + S3 🚀"

# =========================
# SUBMIT PENGADUAN
# =========================
@app.route('/submit', methods=['POST'])
def submit_pengaduan():
    laporan = request.form.get('laporan')
    file    = request.files.get('foto_bukti')

    if not laporan or not file:
        return jsonify({"error": "Data tidak lengkap"}), 400

    # Upload foto ke S3
    foto_url = upload_to_s3(file, folder='pengaduan')
    tiket    = f"PGD-{uuid.uuid4().hex[:6].upper()}"

    # Simpan ke RDS
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO pengaduan (tiket, laporan, foto_url) VALUES (%s, %s, %s)",
            (tiket, laporan, foto_url)
        )
    conn.commit()
    conn.close()

    return jsonify({
        "message": "Berhasil",
        "tiket": tiket,
        "foto_url": foto_url
    })

# =========================
# GET SEMUA LAPORAN
# =========================
@app.route('/laporan', methods=['GET'])
def get_all():
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM pengaduan ORDER BY created_at DESC")
        data = cur.fetchall()
    conn.close()
    return jsonify(data)

# =========================
# GET BY TIKET
# =========================
@app.route('/laporan/<tiket>', methods=['GET'])
def get_by_tiket(tiket):
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM pengaduan WHERE tiket = %s", (tiket,))
        item = cur.fetchone()
    conn.close()
    if not item:
        return jsonify({"error": "Tiket tidak ditemukan"}), 404
    return jsonify(item)

# =========================
# UPDATE STATUS
# =========================
@app.route('/laporan/<int:id>', methods=['PUT'])
def update_data(id):
    body   = request.json
    status = body.get("status")
    conn   = get_db()
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE pengaduan SET status = %s WHERE id = %s",
            (status, id)
        )
        affected = cur.rowcount
    conn.commit()
    conn.close()
    if affected == 0:
        return jsonify({"error": "Data tidak ditemukan"}), 404
    return jsonify({"message": "Berhasil diupdate"})

# =========================
# DELETE
# =========================
@app.route('/laporan/<int:id>', methods=['DELETE'])
def delete_data(id):
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute("DELETE FROM pengaduan WHERE id = %s", (id,))
        affected = cur.rowcount
    conn.commit()
    conn.close()
    if affected == 0:
        return jsonify({"error": "Data tidak ditemukan"}), 404
    return jsonify({"message": "Berhasil dihapus"})

# =========================
# RUN
# =========================
with app.app_context():
    init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)