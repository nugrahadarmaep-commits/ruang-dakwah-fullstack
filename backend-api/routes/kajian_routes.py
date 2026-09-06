"""
Modul Rute Jadwal Kajian.
Menyediakan endpoint untuk menampilkan direktori kajian dan pengisian data awal (seeding).
"""

from flask import Blueprint, jsonify
from extensions import db
from models import Kajian

kajian_bp = Blueprint("kajian", __name__)


# ==============================================================================
# ENDPOINT MENGAMBIL DAFTAR JADWAL KAJIAN (GET /kajian/)
# ==============================================================================
@kajian_bp.route("/", methods=["GET"])
def get_kajian():
    """
    Mengambil seluruh data jadwal kajian yang tersedia dalam basis data.
    """
    try:
        daftar_kajian = Kajian.query.all()

        hasil = [
            {
                "id": k.id,
                "judul": k.judul,
                "ustadz": k.ustadz,
                "tanggal": k.tanggal,
                "waktu": k.waktu,
                "lokasi": k.lokasi,
                "kategori": k.kategori,
                "deskripsi": k.deskripsi,
                "kuota": k.kuota,
            }
            for k in daftar_kajian
        ]

        return jsonify({
            "status": "sukses",
            "total": len(hasil),
            "data": hasil
        }), 200

    except Exception as e:
        return jsonify({
            "status": "gagal",
            "pesan": f"Gagal memuat jadwal kajian: {str(e)}"
        }), 500


# ==============================================================================
# ENDPOINT PENGISIAN DATA AWAL KAJIAN (GET /kajian/seed)
# ==============================================================================
@kajian_bp.route("/seed", methods=["GET"])
def seed_kajian():
    """
    Mengisi data contoh kajian ke basis data untuk keperluan demonstrasi dan instalasi awal.
    """
    try:
        # Jika data kajian sudah ada, batalkan seeding
        if Kajian.query.first():
            return jsonify({
                "status": "sukses",
                "pesan": "Data kajian sudah tersedia di basis data."
            }), 200

        data_awal_kajian = [
            Kajian(
                judul="MEMAHAMI FIKIH MUAMALAH KONTEMPORER",
                ustadz="Ustadz Adi Hidayat, Lc., MA.",
                tanggal="Sabtu, 18 Mei",
                waktu="09:00 WIB",
                lokasi="Masjid Raya Sidoarjo",
                kategori="Fiqih",
                deskripsi=(
                    "Kajian ini membahas hukum-hukum muamalah di era modern, "
                    "termasuk transaksi digital, sistem paylater, pinjaman online, "
                    "dan investasi saham syariah bagi kaum muslimin."
                ),
                kuota=90,
            ),
            Kajian(
                judul="KAJIAN RUTIN: ADAB SEHARI-HARI",
                ustadz="Ustadz Abdul Somad, Ph.D.",
                tanggal="Minggu, 19 Mei",
                waktu="13:00 WIB",
                lokasi="Masjid At-Taqwa, Tulangan",
                kategori="Akidah",
                deskripsi=(
                    "Pemaparan kitab klasik mengenai adab menuntut ilmu, berbakti kepada kedua orang tua, "
                    "serta etika bermedia sosial bagi generasi muda muslim di era digital."
                ),
                kuota=50,
            ),
            Kajian(
                judul="KAJIAN TEMATIK: INTEGRASI SAINS DAN ISLAM",
                ustadz="Ustadz Dr. Subuhsita, M.Kom.",
                tanggal="Minggu, 20 Juni",
                waktu="18:00 WIB",
                lokasi="Masjid Al-Ikhlas, Kampus 2 UMSIDA",
                kategori="Sains & Teknologi",
                deskripsi=(
                    "Kajian komprehensif bagi mahasiswa sains dan teknologi dalam memahami ayat-ayat kauniyah "
                    "serta peran teknologi informasi dalam mendukung dakwah modern."
                ),
                kuota=40,
            ),
        ]

        db.session.add_all(data_awal_kajian)
        db.session.commit()

        return jsonify({
            "status": "sukses",
            "pesan": "Data kajian berhasil diisi ke dalam basis data."
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "gagal",
            "pesan": f"Gagal menambahkan data kajian: {str(e)}"
        }), 500