from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import uuid

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return "Backend jalan tanpa DB 🚀"

# 🔥 biar file bisa diakses dari browser
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/submit', methods=['POST'])
def submit_pengaduan():
    laporan = request.form.get('laporan')
    file = request.files.get('foto_bukti')

    if not laporan or not file:
        return jsonify({"error": "Data tidak lengkap"}), 400

    # simpan file lokal
    filename = str(uuid.uuid4()) + "_" + file.filename
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    # URL file (biar bisa diklik di frontend)
    file_url = f"http://54.66.170.224:5000/uploads/{filename}"

    # generate tiket
    tiket = f"PGD-{uuid.uuid4().hex[:6].upper()}"

    return jsonify({
        "message": "Berhasil",
        "tiket": tiket,
        "foto_url": file_url
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)