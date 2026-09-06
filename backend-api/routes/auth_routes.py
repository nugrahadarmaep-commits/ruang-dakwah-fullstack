"""
Modul Rute Autentikasi dan Manajemen Profil Pengguna.
Menyediakan fungsionalitas registrasi akun, login dengan JWT, pembaruan profil, dan unggah foto.
"""

import os
import datetime
from functools import wraps
import jwt
from flask import Blueprint, jsonify, request, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from extensions import db
from models import User

auth_bp = Blueprint("auth", __name__)

# Mengambil Kunci Rahasia JWT dari konfigurasi lingkungan atau menggunakan nilai default
KUNCI_RAHASIA_JWT = os.getenv("JWT_SECRET_KEY", "rahasia_ruang_dakwah_2026")


# ==============================================================================
# MIDDLEWARE / DEKORATOR AUTENTIKASI TOKEN JWT
# ==============================================================================
def token_required(f):
    """
    Dekorator untuk melindungi endpoint yang membutuhkan otentikasi.
    Memeriksa keberadaan dan validitas token JWT pada header 'Authorization'.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        header_auth = request.headers.get("Authorization")
        if not header_auth:
            return jsonify({
                "status": "gagal",
                "pesan": "Akses ditolak. Token otorisasi tidak ditemukan."
            }), 401

        try:
            # Mengambil token setelah kata kunci 'Bearer '
            token = header_auth.split(" ")[1] if " " in header_auth else header_auth
            data = jwt.decode(token, KUNCI_RAHASIA_JWT, algorithms=["HS256"])
            current_user = User.query.get(data["user_id"])
            if not current_user:
                return jsonify({
                    "status": "gagal",
                    "pesan": "Pengguna yang terhubung dengan token tidak ditemukan."
                }), 401
        except jwt.ExpiredSignatureError:
            return jsonify({
                "status": "gagal",
                "pesan": "Sesi token telah kedaluwarsa. Silakan masuk kembali."
            }), 401
        except Exception:
            return jsonify({
                "status": "gagal",
                "pesan": "Token otorisasi tidak valid."
            }), 401

        return f(current_user, *args, **kwargs)

    return decorated


# ==============================================================================
# ENDPOINT REGISTRASI AKUN (POST /auth/register)
# ==============================================================================
@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Mendaftarkan pengguna baru ke sistem dengan melakukan hashing pada kata sandi.
    """
    data = request.get_json() or {}

    nama_lengkap = data.get("nama_lengkap", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "")
    no_hp = data.get("no_hp", "").strip()

    if not nama_lengkap or not email or not password:
        return jsonify({
            "status": "gagal",
            "pesan": "Nama lengkap, email, dan kata sandi wajib diisi."
        }), 400

    # Memeriksa apakah alamat email telah digunakan
    user_exist = User.query.filter_by(email=email).first()
    if user_exist:
        return jsonify({
            "status": "gagal",
            "pesan": "Alamat email sudah terdaftar. Silakan gunakan email lain."
        }), 400

    # Hashing kata sandi menggunakan pbkdf2:sha256 demi keamanan
    hashed_pw = generate_password_hash(password, method="pbkdf2:sha256")
    pengguna_baru = User(
        nama_lengkap=nama_lengkap,
        email=email,
        no_hp=no_hp,
        password=hashed_pw
    )

    db.session.add(pengguna_baru)
    db.session.commit()

    return jsonify({
        "status": "sukses",
        "pesan": "Pendaftaran akun berhasil. Silakan masuk."
    }), 201


# ==============================================================================
# ENDPOINT LOGIN DAN PENERBITAN TOKEN JWT (POST /auth/login)
# ==============================================================================
@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Memverifikasi kredensial pengguna dan mengembalikan token JWT untuk autentikasi sesi.
    """
    data = request.get_json() or {}
    email = data.get("email", "").strip()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({
            "status": "gagal",
            "pesan": "Email dan kata sandi wajib diisi."
        }), 400

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({
            "status": "gagal",
            "pesan": "Email atau kata sandi tidak cocok."
        }), 401

    # Membuat token JWT dengan masa berlaku 24 jam
    payload = {
        "user_id": user.id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }
    token = jwt.encode(payload, KUNCI_RAHASIA_JWT, algorithm="HS256")

    return jsonify({
        "status": "sukses",
        "pesan": "Proses masuk berhasil.",
        "token": token,
        "user": {
            "id": user.id,
            "nama": user.nama_lengkap,
            "email": user.email,
            "no_hp": user.no_hp,
            "foto_profil": user.foto_profil
        }
    }), 200


# ==============================================================================
# ENDPOINT PERBARUI PROFIL PENGGUNA (PUT /auth/update_profil)
# ==============================================================================
@auth_bp.route("/update_profil", methods=["PUT"])
@token_required
def update_profil(current_user):
    """
    Memperbarui informasi nama lengkap dan kontak pengguna yang sedang terautentikasi.
    """
    data = request.get_json() or {}
    nama_baru = data.get("nama_lengkap", "").strip()
    no_hp_baru = data.get("no_hp")

    if not nama_baru:
        return jsonify({
            "status": "gagal",
            "pesan": "Nama lengkap tidak boleh kosong."
        }), 400

    current_user.nama_lengkap = nama_baru
    if no_hp_baru is not None:
        current_user.no_hp = no_hp_baru.strip()

    db.session.commit()

    return jsonify({
        "status": "sukses",
        "pesan": "Profil berhasil diperbarui.",
        "user": {
            "id": current_user.id,
            "nama": current_user.nama_lengkap,
            "email": current_user.email,
            "no_hp": current_user.no_hp,
            "foto_profil": current_user.foto_profil
        }
    }), 200


# ==============================================================================
# ENDPOINT UNGGAH FOTO PROFIL (POST /auth/upload_foto)
# ==============================================================================
@auth_bp.route("/upload_foto", methods=["POST"])
@token_required
def upload_foto(current_user):
    """
    Menyimpan berkas foto profil pengguna ke direktori statis dan memperbarui URL pada basis data.
    """
    try:
        if "foto_profil" not in request.files:
            return jsonify({
                "status": "gagal",
                "pesan": "Berkas gambar tidak ditemukan pada permintaan."
            }), 400

        berkas = request.files["foto_profil"]
        if berkas.filename == "":
            return jsonify({
                "status": "gagal",
                "pesan": "Nama berkas tidak boleh kosong."
            }), 400

        nama_aman = secure_filename(berkas.filename)
        nama_unik = f"user_{current_user.id}_{nama_aman}"

        # Jalur penyimpanan berkas foto profil
        folder_simpan = os.path.join(current_app.root_path, "static", "uploads", "profil")
        os.makedirs(folder_simpan, exist_ok=True)

        jalur_lengkap = os.path.join(folder_simpan, nama_unik)
        berkas.save(jalur_lengkap)

        # Simpan URL relatif ke basis data
        url_foto = f"/static/uploads/profil/{nama_unik}"
        current_user.foto_profil = url_foto
        db.session.commit()

        return jsonify({
            "status": "sukses",
            "pesan": "Foto profil berhasil diperbarui.",
            "url_foto": url_foto
        }), 200

    except Exception as e:
        return jsonify({
            "status": "gagal",
            "pesan": f"Gagal menyimpan foto profil: {str(e)}"
        }), 500