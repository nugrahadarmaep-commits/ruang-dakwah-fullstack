"""
Modul Rute Manajemen Tiket dan Item Tersimpan (Bookmark).
Menangani alur pendaftaran kegiatan, validasi keamanan, pembatalan tiket, serta penyimpanan kajian/berita favorit.
"""

from flask import Blueprint, request, jsonify
from extensions import db
from models import Tiket, Kajian, Tersimpan
from routes.auth_routes import token_required
from werkzeug.security import check_password_hash

tiket_pop = Blueprint("tiket", __name__)


# ==============================================================================
# 1. ENDPOINT PENDAFTARAN KAJIAN / CETAK TIKET (POST /tiket/daftar)
# ==============================================================================
@tiket_pop.route("/daftar", methods=["POST"])
@token_required
def daftar_kajian(current_user):
    """
    Mendaftarkan pengguna ke kegiatan kajian dengan verifikasi kredensial tambahan demi keamanan.
    Mengurangi kuota yang tersedia dan menerbitkan tiket digital berstatus 'aktif'.
    """
    data = request.get_json() or {}
    id_kajian = data.get("kajian_id")
    email_input = data.get("email", "").strip()
    password_input = data.get("password", "")

    # Validasi kelengkapan data input
    if not id_kajian or not email_input or not password_input:
        return jsonify({
            "status": "gagal",
            "pesan": "ID kajian, alamat email, dan kata sandi wajib diisi."
        }), 400

    # Validasi kesesuaian email akun pengguna yang sedang login
    if current_user.email != email_input:
        return jsonify({
            "status": "gagal",
            "pesan": "Alamat email tidak sesuai dengan akun yang sedang aktif."
        }), 401

    # Verifikasi kata sandi pengguna
    if not check_password_hash(current_user.password, password_input):
        return jsonify({
            "status": "gagal",
            "pesan": "Kata sandi yang dimasukkan salah."
        }), 401

    # Validasi keberadaan data kajian
    target_kajian = Kajian.query.get(id_kajian)
    if not target_kajian:
        return jsonify({
            "status": "gagal",
            "pesan": "Kajian tidak ditemukan."
        }), 404

    # Validasi ketersediaan kuota
    if target_kajian.kuota <= 0:
        return jsonify({
            "status": "gagal",
            "pesan": "Mohon maaf, kuota pendaftaran untuk kajian ini telah habis."
        }), 400

    # Validasi apakah pengguna sudah memiliki tiket aktif untuk kajian yang sama
    tiket_aktif_ada = Tiket.query.filter_by(
        user_id=current_user.id,
        kajian_id=id_kajian,
        status="aktif"
    ).first()
    if tiket_aktif_ada:
        return jsonify({
            "status": "gagal",
            "pesan": "Anda sudah memiliki tiket aktif untuk kajian ini."
        }), 400

    try:
        # Mengurangi kuota kursi kajian
        target_kajian.kuota -= 1

        # Menerbitkan entitas tiket elektronik baru
        tiket_baru = Tiket(
            user_id=current_user.id,
            kajian_id=id_kajian,
            status="aktif"
        )
        db.session.add(tiket_baru)
        db.session.commit()

        return jsonify({
            "status": "sukses",
            "pesan": "Pendaftaran berhasil. Tiket elektronik telah diterbitkan.",
            "id_tiket": tiket_baru.id,
            "sisa_kuota": target_kajian.kuota
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "gagal",
            "pesan": f"Terjadi kesalahan pada server saat memproses pendaftaran: {str(e)}"
        }), 500


# ==============================================================================
# 2. ENDPOINT MENGAMBIL DAFTAR TIKET PENGGUNA (GET /tiket/saya)
# ==============================================================================
@tiket_pop.route("/saya", methods=["GET"])
@token_required
def get_tiket_saya(current_user):
    """
    Mengambil seluruh data tiket pendaftaran yang dimiliki oleh pengguna aktif.
    """
    try:
        daftar_tiket = Tiket.query.filter_by(user_id=current_user.id).order_by(Tiket.tgl_booking.desc()).all()
        hasil = []

        for t in daftar_tiket:
            detail = t.detail_kajian
            hasil.append({
                "id_tiket": t.id,
                "tgl_booking": t.tgl_booking.strftime("%d %b %Y, %H:%M") if t.tgl_booking else "-",
                "status_tiket": t.status,
                "kajian": {
                    "id": detail.id if detail else None,
                    "judul": detail.judul if detail else "Kajian Tidak Tersedia",
                    "ustadz": detail.ustadz if detail else "-",
                    "tanggal": detail.tanggal if detail else "-",
                    "waktu": detail.waktu if detail else "-",
                    "lokasi": detail.lokasi if detail else "-",
                    "kategori": detail.kategori if detail else "-"
                }
            })

        return jsonify({
            "status": "sukses",
            "data": hasil
        }), 200

    except Exception as e:
        return jsonify({
            "status": "gagal",
            "pesan": f"Gagal mengambil data riwayat tiket: {str(e)}"
        }), 500


# ==============================================================================
# 3. ENDPOINT PEMBATALAN TIKET & PENGEMBALIAN KUOTA (POST /tiket/batalkan)
# ==============================================================================
@tiket_pop.route("/batalkan", methods=["POST"])
@token_required
def batalkan_tiket(current_user):
    """
    Membatalkan tiket yang berstatus 'aktif' dan secara otomatis mengembalikan kuota kursi ke kajian.
    """
    data = request.get_json() or {}
    id_tiket = data.get("tiket_id")

    if not id_tiket:
        return jsonify({
            "status": "gagal",
            "pesan": "ID tiket wajib disertakan."
        }), 400

    target_tiket = Tiket.query.filter_by(id=id_tiket, user_id=current_user.id).first()
    if not target_tiket:
        return jsonify({
            "status": "gagal",
            "pesan": "Tiket tidak ditemukan atau Anda tidak memiliki akses terhadap tiket ini."
        }), 404

    if target_tiket.status == "dibatalkan":
        return jsonify({
            "status": "gagal",
            "pesan": "Tiket ini sudah dibatalkan sebelumnya."
        }), 400

    try:
        # Mengubah status tiket menjadi dibatalkan
        target_tiket.status = "dibatalkan"

        # Mengembalikan kuota kajian sebesar 1
        target_kajian = target_tiket.detail_kajian
        if target_kajian:
            target_kajian.kuota += 1

        db.session.commit()

        return jsonify({
            "status": "sukses",
            "pesan": "Pendaftaran berhasil dibatalkan. Kuota kajian telah dikembalikan."
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "gagal",
            "pesan": f"Terjadi kesalahan saat membatalkan pendaftaran: {str(e)}"
        }), 500


# ==============================================================================
# 4. ENDPOINT MENYIMPAN ITEM BOOKMARK (POST /tiket/simpan)
# ==============================================================================
@tiket_pop.route("/simpan", methods=["POST"])
@token_required
def simpan_item(current_user):
    """
    Menyimpan referensi kegiatan kajian atau informasi berita ke dalam daftar tersimpan pengguna.
    """
    data = request.get_json() or {}
    tipe = data.get("tipe_item")  # Nilai yang valid: 'kajian' atau 'berita'
    item_id = data.get("item_id")
    data_ekstra = data.get("data_ekstra")

    if not tipe or tipe not in ["kajian", "berita"]:
        return jsonify({
            "status": "gagal",
            "pesan": "Tipe item wajib diisi ('kajian' atau 'berita')."
        }), 400

    # Validasi duplikasi bookmark kajian
    if tipe == "kajian":
        sudah_ada = Tersimpan.query.filter_by(
            user_id=current_user.id,
            tipe_item="kajian",
            item_id=str(item_id)
        ).first()
        if sudah_ada:
            return jsonify({
                "status": "gagal",
                "pesan": "Kajian ini sudah tersimpan dalam daftar Anda."
            }), 400

    # Validasi duplikasi bookmark berita
    elif tipe == "berita":
        sudah_ada = Tersimpan.query.filter_by(
            user_id=current_user.id,
            tipe_item="berita",
            data_ekstra=data_ekstra
        ).first()
        if sudah_ada:
            return jsonify({
                "status": "gagal",
                "pesan": "Informasi berita ini sudah tersimpan sebelumnya."
            }), 400

    try:
        item_baru = Tersimpan(
            user_id=current_user.id,
            tipe_item=tipe,
            item_id=str(item_id) if item_id else None,
            data_ekstra=data_ekstra
        )
        db.session.add(item_baru)
        db.session.commit()

        return jsonify({
            "status": "sukses",
            "pesan": "Item berhasil disimpan ke daftar Tersimpan."
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "gagal",
            "pesan": f"Terjadi kesalahan saat menyimpan data: {str(e)}"
        }), 500


# ==============================================================================
# 5. ENDPOINT MENGAMBIL DAFTAR ITEM TERSIMPAN (GET /tiket/tersimpan)
# ==============================================================================
@tiket_pop.route("/tersimpan", methods=["GET"])
@token_required
def get_tersimpan(current_user):
    """
    Mengambil semua data bookmark pengguna, baik kategori kajian maupun berita.
    """
    try:
        daftar_simpanan = (
            Tersimpan.query.filter_by(user_id=current_user.id)
            .order_by(Tersimpan.tgl_simpan.desc())
            .all()
        )
        hasil = []

        for s in daftar_simpanan:
            tgl_format = s.tgl_simpan.strftime("%d %b %Y") if s.tgl_simpan else "-"

            if s.tipe_item == "kajian":
                kajian = Kajian.query.get(s.item_id)
                if kajian:
                    hasil.append({
                        "id_simpan": s.id,
                        "tipe": "kajian",
                        "tanggal_simpan": tgl_format,
                        "detail": {
                            "id_kajian": kajian.id,
                            "judul": kajian.judul,
                            "ustadz": kajian.ustadz,
                            "tanggal": kajian.tanggal,
                            "waktu": kajian.waktu,
                            "lokasi": kajian.lokasi
                        }
                    })
            elif s.tipe_item == "berita":
                hasil.append({
                    "id_simpan": s.id,
                    "tipe": "berita",
                    "tanggal_simpan": tgl_format,
                    "detail": s.data_ekstra
                })

        return jsonify({
            "status": "sukses",
            "data": hasil
        }), 200

    except Exception as e:
        return jsonify({
            "status": "gagal",
            "pesan": f"Gagal memuat data tersimpan: {str(e)}"
        }), 500


# ==============================================================================
# 6. ENDPOINT MENGHAPUS ITEM DARI TERSIMPAN (DELETE /tiket/hapus_simpanan/<id>)
# ==============================================================================
@tiket_pop.route("/hapus_simpanan/<int:id_simpan>", methods=["DELETE"])
@token_required
def hapus_simpanan(current_user, id_simpan):
    """
    Menghapus item tertentu dari daftar bookmark pengguna.
    """
    item = Tersimpan.query.filter_by(id=id_simpan, user_id=current_user.id).first()
    if not item:
        return jsonify({
            "status": "gagal",
            "pesan": "Item tersimpan tidak ditemukan atau bukan milik Anda."
        }), 404

    try:
        db.session.delete(item)
        db.session.commit()
        return jsonify({
            "status": "sukses",
            "pesan": "Item berhasil dihapus dari daftar Tersimpan."
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "gagal",
            "pesan": f"Terjadi kesalahan saat menghapus data: {str(e)}"
        }), 500