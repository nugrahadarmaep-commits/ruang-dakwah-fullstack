# 🕌 KITAB PANDUAN RUANG DAKWAH (BUDAYAKAN MEMBACA SEBELUM BERTANYA!)

Aplikasi Ruang Dakwah adalah platform web untuk jadwal kajian dan tanya jawab publik. Dokumen ini adalah panduan mutlak untuk menginstal, menjalankan, dan melakukan demonstrasi API saat presentasi.

---

## 🛠️ TAHAP 1: CARA INSTALL & MENJALANKAN APLIKASI (WAJIB!)

### A. Install Library Python (Biar Nggak Error)

Pastikan Python sudah terinstall. Buka Terminal di VS Code, lalu ketik perintah ini satu per satu:
`pip install flask`
`pip install flask-cors`
`pip install PyJWT`
`pip install werkzeug`
`pip install flask-sqlalchemy`

jika tidak bisa tambahkan dengan contoh sebagai berikut:

`py -m pip install flask-sqlalchemy`

kenapa (py -m) karena type windows lebih menerima itu jadi di install langsung ke ibunya python.

### B. Menjalankan Server Backend (Flask)

1. Buka Terminal di VS Code (klik menu `Terminal` -> `New Terminal`).
2. Ketik perintah ini:
   `py backend-api/app.py`
   _(Catatan: Jika `py` tidak bisa, gunakan `python backend-api/app.py`)_
3. Tunggu sampai terminal memunculkan tulisan: `Running on http://127.0.0.1:5000`. **Jangan tutup terminal ini!**

### C. Menjalankan Frontend (UI)

1. Buka folder utama proyek di VS Code.
2. Gunakan ekstensi **Live Server**.
3. Klik tulisan "Go Live" di pojok kanan bawah VS Code untuk membuka antarmuka web di browser.

---

## ⚡ TAHAP 2: PANDUAN DEMO REST API (THUNDER CLIENT)

Bagian ini khusus untuk demonstrasi "Dapur" (Backend) kita menggunakan **Thunder Client**.
**Cara Mulai:** Klik ekstensi Thunder Client di sebelah kiri VS Code -> Klik `New Request`.

### 🟢 1. CEK STATUS SERVER (Pemanasan)

- **Method:** GET
- **URL:** `http://127.0.0.1:5000/`
- **Fungsi:** Buat nunjukin kalau Flask udah running dan siap menerima perintah.
- **Hasil yang benar:** `{"pesan": "Server flask sudah berjalan", "status": "sukses"}`

### 🔵 2. REGISTER AKUN BARU (CREATE)

- **Method:** POST
- **URL:** `http://127.0.0.1:5000/register`
- **Cara Tembak:** Buka tab **Body** -> pilih **JSON**. Masukkan kode ini:
  ```json
  {
    "nama": "Dosen Penguji",
    "email": "dosen@umsida.ac.id",
    "password": "rahasia"
  }
  ```

### 🔵 3. LOGIN & CETAK TIKET (READ) ==> ⚠️ SANGAT PENTING BANGET!

- **Method:** POST
- **URL:** `http://127.0.0.1:5000/login`
- **Cara Tembak:** Buka tab **Body** -> pilih **JSON**. Masukkan email dan password yang barusan dibikin.
- **Fungsi:** Kalau login sukses, server akan mengembalikan Token JWT. Token ini ibarat KTP digital biar user bisa masuk ke fitur khusus.
- **DISCLAIMER:** DIUSAHAKAN TOKEN DI COPY LALU DITARUH DI NOTEPAD BIAR TIDAK LUPA SAAT MELAKUKAN TEST SELANJUTNYA!

### 🟢 4. TARIK JADWAL KAJIAN (READ)

- **Method:** GET
- **URL:** `http://127.0.0.1:5000/kajian`
- **Fungsi:** Nunjukin narik data jadwal _(Pastiin udah pernah nembak /seed_kajian sebelumnya lewat browser biar datanya ada)_.

### 🟢 5. TARIK SEMUA CHAT (READ)

- **Method:** GET
- **URL:** `http://127.0.0.1:5000/chat_global`
- **Fungsi:** Narik data riwayat chat publik.

---

## 🛡️ ZONA WAJIB BAWA TIKET JWT (SATPAM AKTIF)

Untuk 3 endpoint di bawah ini, **WAJIB** memasukkan Token JWT yang di-copy dari hasil Login tadi.
**Cara di Thunder Client:** Buka tab **Auth** -> Pilih **Bearer** -> Paste token kalian di situ.

### 🟠 6. KIRIM CHAT BARU (CREATE)

- **Method:** POST
- **URL:** `http://127.0.0.1:5000/kirim_chat`
- **Cara Tembak:** Buka tab **Body** -> pilih **JSON**.
  ```json
  {
    "pesan": "Halo, ini tes chat dari Thunder Client!"
  }
  ```

### 🟠 7. UPDATE PROFIL (UPDATE)

- **Method:** PUT
- **URL:** `http://127.0.0.1:5000/update_profil`
- **Cara Tembak:** Buka tab **Body** -> pilih **JSON**.
  ```json
  {
    "nama_lengkap": "BEBAS NAMA KALIAN (Edited)",
    "email": "subuhsita_baru@umsida.ac.id"
  }
  ```

### 🔴 8. HAPUS CHAT (DELETE)

- **Method:** DELETE
- **URL:** `http://127.0.0.1:5000/hapus_chat/1` _(Angka 1 ganti sama ID chat yang mau dihapus)_
- **Cara Tembak:** Nggak butuh Body JSON, cukup URL dan pastikan Token JWT tertempel di tab Auth.

---

_(Disclaimer: Sebetulnya ada 9 Endpoint, tapi ke-9 itu `/seed_kajian` yang sifatnya cuma buat setup awal database, jadi nggak usah dipamerin pas demo API)._
