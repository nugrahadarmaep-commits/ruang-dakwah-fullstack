import os
from flask import Blueprint, jsonify, request
from extensions import db
from models import TanyaJawab
from .auth_routes import token_required
import google.generativeai as genai

chat_bp = Blueprint("chat", __name__)

# Murni ambil dari file .env tanpa fallback string mentah
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Model Gemini untuk konsultasi teks
NAMA_MODEL_AI = "models/gemini-flash-lite-latest"
model_ai = genai.GenerativeModel(NAMA_MODEL_AI)


# ==============================================================================
# 1. MENGAMBIL RIWAYAT TANYA JAWAB (GET /chat/)
# ==============================================================================
@chat_bp.route("/", methods=["GET"])
@token_required
def get_riwayat_chat(current_user):
    try:
        daftar_chat = (
            TanyaJawab.query.filter_by(user_id=current_user.id)
            .order_by(TanyaJawab.tgl_tanya.asc())
            .all()
        )

        hasil = [
            {
                "id": c.id,
                "pertanyaan": c.pertanyaan,
                "jawaban": c.jawaban,
                "status": c.status,
                "waktu": (
                    c.tgl_tanya.strftime("%d %b %Y, %H:%M") if c.tgl_tanya else None
                ),
            }
            for c in daftar_chat
        ]

        return jsonify({"status": "sukses", "data": hasil}), 200

    except Exception as e:
        return (
            jsonify(
                {"status": "gagal", "pesan": f"Gagal memuat riwayat obrolan: {str(e)}"}
            ),
            500,
        )


# ==============================================================================
# 2. MENGIRIM PERTANYAAN KE AI & MENYIMPAN KE BASIS DATA (POST /chat/)
# ==============================================================================
@chat_bp.route("/", methods=["POST"])
@token_required
def kirim_pertanyaan(current_user):
    data = request.get_json() or {}
    pertanyaan_pengguna = data.get("pesan", "").strip()

    if not pertanyaan_pengguna:
        return (
            jsonify(
                {"status": "gagal", "pesan": "Pesan pertanyaan tidak boleh kosong."}
            ),
            400,
        )

    try:
        arahan_sistem = (
            "Kamu adalah asisten konsultan islami terpercaya di platform Ruang Dakwah. "
            "Berikan jawaban yang santun, ringkas, jelas, berlandaskan nilai-nilai Islam: "
        )

        respon_gemini = model_ai.generate_content(arahan_sistem + pertanyaan_pengguna)
        jawaban_ai = (
            respon_gemini.text
            if respon_gemini and respon_gemini.text
            else "Maaf, tidak ada respon yang dihasilkan."
        )

        chat_baru = TanyaJawab(
            user_id=current_user.id,
            pertanyaan=pertanyaan_pengguna,
            jawaban=jawaban_ai,
            status="dijawab",
        )
        db.session.add(chat_baru)
        db.session.commit()

        return (
            jsonify(
                {
                    "status": "sukses",
                    "id": chat_baru.id,
                    "pertanyaan": pertanyaan_pengguna,
                    "jawaban": jawaban_ai,
                }
            ),
            201,
        )

    except Exception as e:
        return (
            jsonify(
                {
                    "status": "gagal",
                    "pesan": f"Terjadi kendala saat menghubungkan ke layanan Gemini AI: {str(e)}",
                }
            ),
            500,
        )


# ==============================================================================
# 3. MENYUNTING PERTANYAAN & GENERATE ULANG (PUT /chat/<id>)
# ==============================================================================
@chat_bp.route("/<int:chat_id>", methods=["PUT"])
@token_required
def sunting_pertanyaan(current_user, chat_id):
    chat_target = db.session.get(TanyaJawab, chat_id)
    if not chat_target or chat_target.user_id != current_user.id:
        return (
            jsonify(
                {
                    "status": "gagal",
                    "pesan": "Obrolan tidak ditemukan atau Anda tidak memiliki hak akses.",
                }
            ),
            403,
        )

    data = request.get_json() or {}
    pertanyaan_baru = data.get("pesan", "").strip()

    if not pertanyaan_baru:
        return (
            jsonify(
                {"status": "gagal", "pesan": "Pertanyaan baru tidak boleh kosong."}
            ),
            400,
        )

    try:
        arahan_sistem = (
            "Kamu adalah asisten konsultan islami terpercaya di platform Ruang Dakwah. "
            "Berikan jawaban yang santun, ringkas, jelas, berlandaskan nilai-nilai Islam: "
        )

        respon_gemini = model_ai.generate_content(arahan_sistem + pertanyaan_baru)
        jawaban_baru = (
            respon_gemini.text if respon_gemini and respon_gemini.text else ""
        )

        chat_target.pertanyaan = pertanyaan_baru
        chat_target.jawaban = jawaban_baru
        db.session.commit()

        return (
            jsonify(
                {
                    "status": "sukses",
                    "pesan": "Pertanyaan berhasil diperbarui dan diproses ulang.",
                    "jawaban": jawaban_baru,
                }
            ),
            200,
        )

    except Exception as e:
        return (
            jsonify(
                {"status": "gagal", "pesan": f"Gagal memproses ulang jawaban: {str(e)}"}
            ),
            500,
        )


# ==============================================================================
# 4. MENGHAPUS RIWAYAT OBROLAN (DELETE /chat/<id>)
# ==============================================================================
@chat_bp.route("/<int:chat_id>", methods=["DELETE"])
@token_required
def hapus_obrolan(current_user, chat_id):
    chat_target = db.session.get(TanyaJawab, chat_id)
    if not chat_target or chat_target.user_id != current_user.id:
        return (
            jsonify(
                {
                    "status": "gagal",
                    "pesan": "Obrolan tidak ditemukan atau Anda tidak berwenang menghapusnya.",
                }
            ),
            403,
        )

    try:
        db.session.delete(chat_target)
        db.session.commit()
        return (
            jsonify({"status": "sukses", "pesan": "Riwayat obrolan berhasil dihapus."}),
            200,
        )
    except Exception as e:
        db.session.rollback()
        return (
            jsonify(
                {
                    "status": "gagal",
                    "pesan": f"Gagal menghapus riwayat obrolan: {str(e)}",
                }
            ),
            500,
        )
