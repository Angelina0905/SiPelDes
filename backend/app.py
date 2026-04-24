from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import pymysql
import os
import uuid
from upload_to_s3 import upload_to_s3

app = Flask(__name__)
CORS(app)

# =========================
# TEST ROUTE
# =========================
@app.route("/")
def home():
    return "Backend jalan 🚀"


# =========================
# FOLDER UPLOAD LOKAL
# =========================
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# =========================
# ROUTE AKSES FILE LOKAL
# =========================
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


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

    # 🔥 coba upload ke S3
    file_url = upload_to_s3(file)

    # 🔥 fallback ke lokal kalau gagal
    if not file_url:
        filename = str(uuid.uuid4()) + "_" + file.filename
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        file_url = f"http://54.66.170.224:5000/uploads/{filename}"

    # 🔥 tiket
    tiket = f"PGD-{uuid.uuid4().hex[:6].upper()}"

    # 🔥 simpan DB
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
# RUN
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)