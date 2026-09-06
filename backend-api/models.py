"""
Model Basis Data Aplikasi Ruang Dakwah.
Mendefinisikan skema tabel basis data relasional menggunakan SQLAlchemy ORM.
"""

from datetime import datetime
from extensions import db


class User(db.Model):
    """
    Model Entitas Pengguna (User).
    Menyimpan data kredensial, identitas diri, dan relasi data pengguna.
    """
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    nama_lengkap = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    no_hp = db.Column(db.String(20), nullable=True)
    foto_profil = db.Column(db.String(255), nullable=True)
    tgl_daftar = db.Column(db.DateTime, default=datetime.utcnow)

    # Relasi one-to-many ke Tiket dan Riwayat Tanya Jawab
    tiket_saya = db.relationship("Tiket", backref="peserta", lazy=True)
    pertanyaan_saya = db.relationship("TanyaJawab", backref="penanya", lazy=True)

    def __repr__(self):
        return f"<User {self.email}>"


class Kajian(db.Model):
    """
    Model Entitas Jadwal Kajian.
    Menyimpan informasi rincian kegiatan kajian, pemateri, kuota, dan waktu pelaksanaan.
    """
    __tablename__ = "kajian"

    id = db.Column(db.Integer, primary_key=True)
    judul = db.Column(db.String(200), nullable=False)
    ustadz = db.Column(db.String(100), nullable=False)
    tanggal = db.Column(db.String(50), nullable=False)
    waktu = db.Column(db.String(50), nullable=False)
    lokasi = db.Column(db.String(200), nullable=False)
    kategori = db.Column(db.String(50), nullable=False)
    deskripsi = db.Column(db.Text, nullable=False)
    kuota = db.Column(db.Integer, default=100)

    # Relasi one-to-many ke Tiket pendaftaran
    pendaftar = db.relationship("Tiket", backref="detail_kajian", lazy=True)

    def __repr__(self):
        return f"<Kajian {self.judul}>"


class Tiket(db.Model):
    """
    Model Entitas Tiket Pendaftaran Kajian.
    Menghubungkan akun pengguna dengan kajian yang didaftarkan.
    """
    __tablename__ = "tiket"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    kajian_id = db.Column(db.Integer, db.ForeignKey("kajian.id"), nullable=False)
    tgl_booking = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default="aktif")  # 'aktif' atau 'dibatalkan'

    def __repr__(self):
        return f"<Tiket ID={self.id} User={self.user_id} Kajian={self.kajian_id}>"


class TanyaJawab(db.Model):
    """
    Model Entitas Forum Tanya Jawab (Chatbot AI).
    Merekam riwayat pertanyaan pengguna beserta respon yang dihasilkan AI.
    """
    __tablename__ = "tanya_jawab"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    pertanyaan = db.Column(db.Text, nullable=False)
    jawaban = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default="dijawab")  # 'menunggu' atau 'dijawab'
    tgl_tanya = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<TanyaJawab ID={self.id} User={self.user_id}>"


class Tersimpan(db.Model):
    """
    Model Entitas Bookmark / Item Tersimpan.
    Menyimpan referensi konten kajian atau berita yang di-bookmark oleh pengguna.
    """
    __tablename__ = "tersimpan"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    tipe_item = db.Column(db.String(50), nullable=False)  # 'kajian' atau 'berita'
    item_id = db.Column(db.String(200), nullable=True)
    data_ekstra = db.Column(db.Text, nullable=True)
    tgl_simpan = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Tersimpan ID={self.id} Tipe={self.tipe_item}>"


class Notifikasi(db.Model):
    """
    Model Entitas Notifikasi Pengguna.
    Menyimpan pesan notifikasi sistem bagi setiap akun pengguna.
    """
    __tablename__ = "notifikasi"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    tipe = db.Column(db.String(50), nullable=False)  # 'tiket', 'berita', 'ai'
    judul = db.Column(db.String(200), nullable=False)
    pesan = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)  # Status telah dibaca
    tgl_notif = db.Column(db.DateTime, default=datetime.utcnow)

    # Relasi ke pengguna
    user = db.relationship("User", backref="notifikasi_saya", lazy=True)

    def __repr__(self):
        return f"<Notifikasi ID={self.id} User={self.user_id} Status={'Sudah dibaca' if self.is_read else 'Belum dibaca'}>"
