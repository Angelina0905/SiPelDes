from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql
import os
import uuid
from upload_to_s3 import upload_to_s3   # 🔥 import dari file tadi

app = Flask(__name__)
CORS(app)  # 🔥 biar frontend bisa akses

# =========================
# TEST ROUTE
# =========================
@app.route("/")
def home():
    return "Backend jalan 🚀"


# =========================
# DATABASE CONNECTION
# =========================
def get_db_connection():
    return pymysql.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME'),
        cursorclass=pymysql.cursors.DictCursor
    )


# =========================
# SUBMIT PENGADUAN
# =========================
@app.route('/submit', methods=['POST'])
def submit_pengaduan():
    laporan = request.form.get('laporan')
    file = request.files.get('foto_bukti')

    if not laporan or not file:
        return jsonify({"error": "Data tidak lengkap"}), 400

    # 🔥 upload ke S3
    file_url = upload_to_s3(file)
    if not file_url:
        return jsonify({"error": "Gagal upload ke S3"}), 500

    # 🔥 buat tiket
    tiket = f"PGD-{uuid.uuid4().hex[:6].upper()}"

    # 🔥 simpan ke database
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
            INSERT INTO laporan_pengaduan (laporan, foto_url, status, tiket)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql, (laporan, file_url, "Sedang Diproses", tiket))
        conn.commit()
    except Exception as e:
        print("ERROR DB:", e)
        return jsonify({"error": "Gagal simpan ke database"}), 500
    finally:
        conn.close()

    return jsonify({
        "message": "Berhasil",
        "tiket": tiket,
        "foto_url": file_url
    })


# =========================
# RUN (buat local / debug)
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)