"""
Aplikasi Utama Server Backend Ruang Dakwah (Flask).
Menyediakan RESTful API dan menyajikan antarmuka web statis secara terintegrasi.
"""

import os
from dotenv import load_dotenv
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

# Menentukan jalur absolut folder backend dan root proyek
DIREKTORI_BACKEND = os.path.dirname(os.path.abspath(__file__))
DIREKTORI_ROOT = os.path.dirname(DIREKTORI_BACKEND)

# Memuat konfigurasi variabel lingkungan (.env)
load_dotenv(os.path.join(DIREKTORI_BACKEND, ".env"))
load_dotenv(os.path.join(DIREKTORI_ROOT, ".env"))

from extensions import db
from routes.auth_routes import auth_bp
from routes.kajian_routes import kajian_bp
from routes.chat_routes import chat_bp
from routes.tiket_routes import tiket_pop
from routes.beranda_routes import beranda_bp

app = Flask(__name__)
CORS(app)

# Konfigurasi basis data dan kunci otentikasi JWT
JALUR_DB_DEFAULT = os.path.join(DIREKTORI_ROOT, "instance", "ruang_dakwah.db")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL", f"sqlite:///{JALUR_DB_DEFAULT}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = os.getenv(
    "JWT_SECRET_KEY", "rahasia_ruang_dakwah_2026"
)

# Hubungkan aplikasi dengan ekstensi SQLAlchemy
db.init_app(app)

# Registrasi Blueprint Rute API
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(kajian_bp, url_prefix="/kajian")
app.register_blueprint(chat_bp, url_prefix="/chat")
app.register_blueprint(tiket_pop, url_prefix="/tiket")
app.register_blueprint(beranda_bp, url_prefix="/beranda")


# ==========================================
# PENYAJIAN BERKAS STATIS (DIST & ASSETS)
# ==========================================
@app.route("/dist/<path:filename>")
def layani_dist(filename):
    """Menyajikan berkas CSS, JavaScript, dan library pendukung."""
    return send_from_directory(os.path.join(DIREKTORI_ROOT, "dist"), filename)


@app.route("/assets/<path:filename>")
def layani_assets(filename):
    """Menyajikan aset visual gambar dan favicon aplikasi."""
    return send_from_directory(os.path.join(DIREKTORI_ROOT, "assets"), filename)


# ==========================================
# RUTE NAVIGASI DAN STATUS SERVER
# ==========================================
@app.route("/", methods=["GET"])
def beranda_utama():
    """Mengarahkan pengguna ke halaman login saat pertama kali membuka root web."""
    return send_from_directory(os.path.join(DIREKTORI_ROOT, "ui struktur"), "login.html")


@app.route("/status", methods=["GET"])
def periksa_status():
    """Endpoint pemantauan kesehatan server backend."""
    return jsonify({
        "status": "sukses",
        "pesan": "Server Backend Ruang Dakwah beroperasi dengan normal."
    }), 200


@app.route("/<path:filename>", methods=["GET"])
def layani_ui(filename):
    """Menyajikan halaman HTML secara dinamis dari direktori antarmuka (ui struktur)."""
    if filename.endswith(".html"):
        return send_from_directory(os.path.join(DIREKTORI_ROOT, "ui struktur"), filename)

    return jsonify({
        "status": "gagal",
        "pesan": "Berkas atau endpoint yang diminta tidak ditemukan."
    }), 404


# Inisialisasi tabel dan jalankan server pada mode lokal
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)