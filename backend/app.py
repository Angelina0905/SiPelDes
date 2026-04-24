from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import uuid
import json

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
DATA_FILE = "data.json"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# =========================
# HELPER LOAD & SAVE DATA
# =========================
def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# =========================
# ROOT
# =========================
@app.route("/")
def home():
    return "Backend jalan tanpa DB 🚀"

# =========================
# AKSES FILE
# =========================
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# =========================
# CREATE
# =========================
@app.route('/submit', methods=['POST'])
def submit_pengaduan():
    laporan = request.form.get('laporan')
    file = request.files.get('foto_bukti')

    if not laporan or not file:
        return jsonify({"error": "Data tidak lengkap"}), 400

    # simpan file
    filename = str(uuid.uuid4()) + "_" + file.filename
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    file_url = f"http://54.66.170.224:5000/uploads/{filename}"
    tiket = f"PGD-{uuid.uuid4().hex[:6].upper()}"

    data = load_data()

    new_item = {
        "id": len(data) + 1,
        "tiket": tiket,
        "laporan": laporan,
        "foto_url": file_url,
        "status": "Sedang Diproses"
    }

    data.append(new_item)
    save_data(data)

    return jsonify({
        "message": "Berhasil",
        "tiket": tiket,
        "foto_url": file_url
    })

# =========================
# READ ALL
# =========================
@app.route('/laporan', methods=['GET'])
def get_all():
    data = load_data()
    return jsonify(data)

# =========================
# READ BY TIKET
# =========================
@app.route('/laporan/<tiket>', methods=['GET'])
def get_by_tiket(tiket):
    data = load_data()

    for item in data:
        if item["tiket"] == tiket:
            return jsonify(item)

    return jsonify({"error": "Tiket tidak ditemukan"}), 404

# UPDATE PENGAJUAN
@app.route('/laporan/<int:id>', methods=['PUT'])
def update_data(id):
    data = load_data()
    body = request.json

    for item in data:
        if item["id"] == id:

            # hanya boleh update jika belum selesai
            if item["status"] != "Sedang Diproses":
                return jsonify({"error": "Pengajuan tidak bisa diubah"}), 400

            # update isi laporan
            item["laporan"] = body.get("laporan", item["laporan"])

            save_data(data)

            return jsonify({
                "message": "Pengajuan berhasil diupdate",
                "data": item
            })

    return jsonify({"error": "Data tidak ditemukan"}), 404
# DELETE PENGAJUAN
@app.route('/laporan/<int:id>', methods=['DELETE'])
def delete_data(id):
    data = load_data()

    for item in data:
        if item["id"] == id:

            # hanya boleh hapus jika belum selesai
            if item["status"] != "Sedang Diproses":
                return jsonify({"error": "Pengajuan tidak bisa dihapus"}), 400

            data.remove(item)
            save_data(data)

            return jsonify({"message": "Pengajuan berhasil dihapus"})

    return jsonify({"error": "Data tidak ditemukan"}), 404
# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)