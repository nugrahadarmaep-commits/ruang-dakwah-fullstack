from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps 
from models import db, User, Kajian, Tiket, TanyaJawab

# inisialisasi aplikasi flask
app = Flask(__name__)
# izinkan akses dari frontend (cors)
CORS(app)

# konfigurasi secret key untuk jwt
app.config['SECRET_KEY'] = 'rahasia_ruang_dakwah_2026' 

# konfigurasi database sqlite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ruang_dakwah.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# menghubungkan db dengan aplikasi flask
db.init_app(app)

# ==========================================
# 1. FUNGSI JWT LOGIN
# ==========================================
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token_lengkap = request.headers.get('Authorization')
        if not token_lengkap:
            return jsonify({'pesan': 'Akses ditolak! Token JWT hilang bos!'}), 401
        try:
            token_asli = token_lengkap.split(" ")[1]
            data = jwt.decode(token_asli, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.get(data['user_id'])
        except:
            return jsonify({'pesan': 'Token tidak valid!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated


# route untuk cek status backend
@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "status": "sukses",
        "pesan": "Server flask sudah berjalan"
    }), 200

# ==========================================
# 2. API DAFTAR AKUN (REGISTER)
# ==========================================
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json() 
    
    user_exist = User.query.filter_by(email=data['email']).first()
    if user_exist:
        return jsonify({"status": "gagal", "pesan": "Email sudah terdaftar bro!"}), 400
    
    hashed_pw = generate_password_hash(data['password'], method='pbkdf2:sha256')
    
    new_user = User(nama_lengkap=data['nama'], email=data['email'], password=hashed_pw)
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({"status": "sukses", "pesan": "Berhasil daftar! Silakan login."}), 201


# ==========================================
# 3. API MASUK AKUN LOGIN & CETAK JWT
# ==========================================
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not check_password_hash(user.password, data['password']):
        return jsonify({"status": "gagal", "pesan": "Email atau password salah!"}), 401
        
    token = jwt.encode({
        'user_id': user.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }, app.config['SECRET_KEY'], algorithm='HS256')
    
    return jsonify({
        "status": "sukses",
        "pesan": "Login berhasil!",
        "token": token,
        "user": {
            "nama": user.nama_lengkap, 
            "email": user.email
        }
    }), 200


# ==========================================
# 4. API BUAT NARIK JADWAL KAJIAN (GET)
# ==========================================
@app.route('/kajian', methods=['GET'])
def get_kajian():
    daftar_kajian = Kajian.query.all()
    hasil = []
    
    for k in daftar_kajian:
        hasil.append({
            "id": k.id,
            "judul": k.judul,
            "ustaz": k.ustaz,
            "tanggal": k.tanggal,
            "waktu": k.waktu,
            "lokasi": k.lokasi,
            "kategori": k.kategori
        })
        
    return jsonify({"status": "sukses", "data": hasil}), 200

# ==========================================
# 5. JALUR KE DATABASE SQLITE (SEED DATA KAJIAN)
# ==========================================
@app.route('/seed_kajian', methods=['GET'])
def seed_kajian():
    if Kajian.query.first():
        return jsonify({"pesan": "Data Masuk Silahkan Check!"})
        
    kajian1 = Kajian(
        judul="MEMAHAMI FIKIH MUAMALAH KONTEMPORER",
        ustaz="Ustaz Adi Hidayat, Lc., MA.",
        tanggal="Sabtu, 18 Mei",
        waktu="09:00 WIB",
        lokasi="Masjid Raya Sidoarjo",
        kategori="Fiqih"
    )
    
    kajian2 = Kajian(
        judul="KAJIAN RUTIN: ADAB SEHARI-HARI",
        ustaz="Ustaz Abdul Somad, Ph.D.",
        tanggal="Minggu, 19 Mei",
        waktu="13:00 WIB",
        lokasi="Masjid At-Taqwa, Tulangan",
        kategori="Akidah"
    )

    kajian3 = Kajian(
        judul="KAJIAN RUTIN: BELAJAR BASIS DATA DENGAN GEBRAK PAPAN",
        ustaz="Ustadz Subuhsita, Ph.D.",
        tanggal="Minggu, 20 Juni",
        waktu="18:00 WIB",
        lokasi="Masjid Al-Ikhlas, K2 Umsida",
        kategori="Basis Data"
    )
    
    db.session.add(kajian1)
    db.session.add(kajian2)
    db.session.add(kajian3)
    db.session.commit()
    
    return jsonify({"pesan": "Data kajian berhasil ditambahkan ke database!"})

# ==========================================
# 6. API GLOBAL CHAT
# ==========================================

# A. RUTE BUAT NAMPILIN SEMUA CHAT (GET)
@app.route('/chat_global', methods=['GET'])
def get_chat():
    semua_chat = TanyaJawab.query.all()
    hasil = []
    
    for chat in semua_chat:
        pengirim = User.query.get(chat.user_id)
        # BUG FIX: Pake nama_lengkap, bukan nama
        nama_user = pengirim.nama_lengkap if pengirim else "Warga Anonim"
        
        hasil.append({
            "id": chat.id,
            "nama": nama_user,
            "pesan": chat.pertanyaan
        })
        
    return jsonify({"status": "sukses", "data": hasil}), 200

# B. RUTE BUAT NGIRIM CHAT BARU (POST)
@app.route('/kirim_chat', methods=['POST'])
@token_required 
def kirim_chat(current_user):
    data = request.get_json()
    isi_pesan = data.get('pesan')
    
    if not isi_pesan:
        return jsonify({'pesan': 'Pesan kosong bro!'}), 400
        
    chat_baru = TanyaJawab(user_id=current_user.id, pertanyaan=isi_pesan)
    db.session.add(chat_baru)
    db.session.commit()
    
    return jsonify({
        'status': 'sukses', 
        # BUG FIX: Pake nama_lengkap
        'nama': current_user.nama_lengkap, 
        'pesan': isi_pesan
    }), 201

# ==========================================
# 7. API UPDATE PROFIL (PUT)
# ==========================================
@app.route('/update_profil', methods=['PUT'])
@token_required # Wajib pake satpam biar gak bisa ngedit profil orang lain
def update_profil(current_user):
    data = request.get_json()
    
    # Ambil ketikan nama dan email yang baru dari frontend
    nama_baru = data.get('nama_lengkap')
    email_baru = data.get('email')
    
    if not nama_baru or not email_baru:
        return jsonify({'pesan': 'Nama dan Email gak boleh kosong bos!'}), 400
        
    # Proses Update Data (Ubah data lama jadi data baru)
    current_user.nama_lengkap = nama_baru
    current_user.email = email_baru
    
    # Simpan perubahan ke SQLite
    db.session.commit()
    
    return jsonify({
        'status': 'sukses',
        'pesan': 'SIUUUU! Profil berhasil diupdate!',
        'user': {
            'nama': current_user.nama_lengkap,
            'email': current_user.email
        }
    }), 200

# ==========================================
# 8. API HAPUS CHAT (DELETE)
# ==========================================
@app.route('/hapus_chat/<int:chat_id>', methods=['DELETE'])
@token_required # Wajib bawa tiket satpam
def hapus_chat(current_user, chat_id):
    # 1. Cari chat-nya di database berdasarkan ID
    chat_target = TanyaJawab.query.get(chat_id)
    
    # 2. Kalau chat-nya ternyata nggak ada / udah kehapus
    if not chat_target:
        return jsonify({'pesan': 'Chat tidak ditemukan bos!'}), 404
        
    # 3. VALIDASI KEAMANAN: Cegah hapus chat orang lain!
    if chat_target.user_id != current_user.id:
        return jsonify({'pesan': 'Anda tidak memiliki izin untuk menghapus chat ini!'}), 403
        
    # 4. Eksekusi eksekusi mati (Hapus dari SQLite)
    db.session.delete(chat_target)
    db.session.commit()
    
    return jsonify({
        'status': 'sukses', 
        'pesan': 'Mantap! Chat berhasil dihapus dari muka bumi!'
    }), 200

# untuk menjalankan aplikasi flask
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
    app.run(debug=True, port=5000)