from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

# inisialisasi variabel db di sini! agar tidak terjadi circular import
db = SQLAlchemy()

# tabel pengguna (user)
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    nama_lengkap = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    tgl_daftar = db.Column(db.DateTime, default=datetime.utcnow)
    
    # relasi ke tiket dan tanya jawab
    tiket_saya = db.relationship('Tiket', backref='peserta', lazy=True)
    pertanyaan_saya = db.relationship('TanyaJawab', backref='penanya', lazy=True)

# tabel jadwal kajian
class Kajian(db.Model):
    __tablename__ = 'kajian'
    
    id = db.Column(db.Integer, primary_key=True)
    judul = db.Column(db.String(200), nullable=False)
    ustaz = db.Column(db.String(100), nullable=False)
    tanggal = db.Column(db.String(50), nullable=False) 
    waktu = db.Column(db.String(50), nullable=False)   
    lokasi = db.Column(db.String(200), nullable=False)
    kategori = db.Column(db.String(50), nullable=False)
    
    # relasi pendaftar
    pendaftar = db.relationship('Tiket', backref='detail_kajian', lazy=True)

# tabel tiket (pendaftaran kajian)
class Tiket(db.Model):
    __tablename__ = 'tiket'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    kajian_id = db.Column(db.Integer, db.ForeignKey('kajian.id'), nullable=False)
    tgl_booking = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='aktif') # aktif / batal

# tabel forum tanya jawab
class TanyaJawab(db.Model):
    __tablename__ = 'tanya_jawab'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    pertanyaan = db.Column(db.Text, nullable=False)
    jawaban = db.Column(db.Text, nullable=True) # kosong jika belum dijawab
    status = db.Column(db.String(20), default='menunggu') # menunggu / dijawab
    tgl_tanya = db.Column(db.DateTime, default=datetime.utcnow)