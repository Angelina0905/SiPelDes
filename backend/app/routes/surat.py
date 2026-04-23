from flask import Blueprint, request, jsonify
from app.utils.s3_helper import upload_file

surat_bp = Blueprint("surat", __name__)

@surat_bp.route("/", methods=["POST"])
def create_surat():
    try:
        nama = request.form.get("nama")
        nik = request.form.get("nik")
        no_hp = request.form.get("no_hp")
        jenis = request.form.get("jenis")
        keperluan = request.form.get("keperluan")

        file = request.files.get("file")
        file_url = None

        if file:
            file_url = upload_file(file, folder="surat")

        tiket = "SPD-2026-001"

        return jsonify({
            "message": "Pengajuan berhasil",
            "tiket": tiket,
            "file_url": file_url
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500