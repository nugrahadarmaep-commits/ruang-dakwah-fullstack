"""
Modul Rute Beranda dan Notifikasi Pengguna.
Menyediakan data artikel informasi terkini dan riwayat notifikasi akun secara dinamis.
"""

from flask import Blueprint, jsonify
from routes.auth_routes import token_required
from models import Notifikasi

beranda_bp = Blueprint("beranda", __name__)


# ==============================================================================
# ENDPOINT INFORMASI / BERITA TERKINI (GET /beranda/berita)
# ==============================================================================
@beranda_bp.route("/berita", methods=["GET"])
def get_berita_terkini():
    """
    Mengembalikan daftar berita dan artikel terkini seputar kegiatan dakwah dan informasi kampus.
    """
    try:
        data_berita = [
            {
                "id": 1,
                "judul": "Muhammadiyah Rilis Panduan Fiqih Informasi, Wajib Dibaca Mahasiswa FST!",
                "tanggal": "Thu, 04 Jun 2026",
                "ikon": "bi-newspaper",
                "link": "https://muhammadiyah.or.id/"
            },
            {
                "id": 2,
                "judul": "Tim Robotik Lolos Pendanaan Nasional 2026, Hadirkan Solusi Dakwah Digital",
                "tanggal": "Thu, 04 Jun 2026",
                "ikon": "bi-award-fill",
                "link": "https://umsida.ac.id/"
            }
        ]
        return jsonify({
            "status": "sukses",
            "data": data_berita
        }), 200
    except Exception:
        return jsonify({
            "status": "gagal",
            "pesan": "Gagal memuat daftar berita terkini."
        }), 500


# ==============================================================================
# ENDPOINT DAFTAR NOTIFIKASI PENGGUNA (GET /beranda/notifikasi)
# ==============================================================================
@beranda_bp.route("/notifikasi", methods=["GET"])
@token_required
def get_notifikasi(current_user):
    """
    Mengambil seluruh notifikasi milik pengguna terautentikasi berdasarkan urutan terbaru.
    """
    try:
        daftar_notif = (
            Notifikasi.query.filter_by(user_id=current_user.id)
            .order_by(Notifikasi.tgl_notif.desc())
            .all()
        )

        hasil = []
        for item in daftar_notif:
            waktu_format = (
                item.tgl_notif.strftime("%d %b %Y, %H:%M")
                if item.tgl_notif and hasattr(item.tgl_notif, "strftime")
                else "Baru saja"
            )
            hasil.append({
                "id": item.id,
                "tipe": item.tipe,
                "judul": item.judul,
                "pesan": item.pesan,
                "waktu": waktu_format,
                "is_read": item.is_read
            })

        return jsonify({
            "status": "sukses",
            "data": hasil
        }), 200

    except Exception as e:
        return jsonify({
            "status": "gagal",
            "pesan": f"Terjadi kesalahan saat memuat notifikasi: {str(e)}"
        }), 500