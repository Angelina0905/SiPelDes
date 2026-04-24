from flask import Flask, request, jsonify
import pymysql
import os
import uuid

app = Flask(__name__)

@app.route("/")
def home():
    return "Backend jalan 🚀"

def get_db_connection():
    return pymysql.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME'),
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route('/submit', methods=['POST'])
def submit_pengaduan():
    laporan = request.form.get('laporan')
    file = request.files.get('foto_bukti')

    if not laporan or not file:
        return jsonify({"error": "Data tidak lengkap"}), 400

    # sementara dummy dulu biar gak error
    file_url = "https://dummy-file-url.com"

    tiket = f"PGD-{uuid.uuid4().hex[:6].upper()}"

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = "INSERT INTO laporan_pengaduan (laporan, foto_url, status, tiket) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (laporan, file_url, "Sedang Diproses", tiket))
        conn.commit()
    finally:
        conn.close()

    return jsonify({
        "message": "Berhasil",
        "tiket": tiket,
        "foto_url": file_url
    })