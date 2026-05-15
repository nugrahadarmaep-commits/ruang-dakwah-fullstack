// ==========================================
// AUTH.JS - LOGIKA SATPAM & KONEKSI BACKEND FLASK
// ==========================================

// api calling di menuju app.py
const API_URL = "http://127.0.0.1:5000";

// Kunci untuk nyimpen token di brankas browser (Local Storage)
const TOKEN_KEY = "ruang_dakwah_jwt";

document.addEventListener("DOMContentLoaded", function() {
    
    // Cek user lagi buka halaman apa sekarang
    const currentUrl = window.location.pathname;
    const isLoginPage = currentUrl.endsWith("login.html") || 
                    currentUrl.endsWith("register.html") || 
                    currentUrl === "/" || 
                    currentUrl.endsWith("/");

    // Ambil token dari brankas
    const userToken = localStorage.getItem(TOKEN_KEY);

    // ==========================================
    // 1. ROUTE PROTECTION (SISTEM TENDANG OTOMATIS)
    // ==========================================
    
    // Skenario A: Belum login, tapi nekat masuk halaman dalam
    if (!userToken && !isLoginPage) {
        console.warn("Akses ilegal terdeteksi! Menendang user ke halaman Login...");
        window.location.replace("login.html"); 
        return; 
    }

    // Skenario B: Udah login, tapi nyasar buka halaman login lagi
    if (userToken && isLoginPage) {
        console.info("User sudah login. Mengalihkan ke Lobby...");
        window.location.replace("beranda.html");
        return;
    }

    // ==========================================
    // 2. LOGIKA TOMBOL MASUK (DI LOGIN.HTML)
    // ==========================================
    const loginForm = document.getElementById("loginForm");
    if (loginForm) {
        // PERHATIKAN: Kita pakai async karena nunggu balasan dari Flask
        loginForm.addEventListener("submit", async function(e) {
            e.preventDefault(); 
            
            // Ambil data dari form HTML
            const email = document.getElementById("logEmail").value;
            const password = document.getElementById("logPassword").value;

            try {
                console.log("Mengirim data ke Flask...");
                // Nembak ke backend
                const response = await fetch(`${API_URL}/login`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ email: email, password: password })
                });

                const data = await response.json();

                // Kalau backend bilang sukses
                if (response.ok) {
                    alert("Mantap, " + data.user.nama + "! Login sukses.");
                    
                    // Simpan JWT ASLI dari Flask ke Local Storage
                    localStorage.setItem(TOKEN_KEY, data.token);
                    localStorage.setItem("user_nama", data.user.nama);
                    
                    // Arahkan ke Beranda
                    window.location.href = "beranda.html";
                } else {
                    alert("Login Gagal: " + data.pesan);
                }
            } catch (error) {
                alert("Server Flask mati bro! Nyalain dulu python app.py di terminal");
                console.error(error);
            }
        });
    }

    // ==========================================
    // 3. LOGIKA TOMBOL DAFTAR (KALAU ADA FORM REGISTER DI LOGIN.HTML)
    // ==========================================
    // Pastikan form pendaftaran punya id="registerForm"
    const registerForm = document.getElementById("registerForm");
    if (registerForm) {
        registerForm.addEventListener("submit", async function(e) {
            e.preventDefault();
            
            const nama = document.getElementById("regNama").value;
            const email = document.getElementById("regEmail").value;
            const password = document.getElementById("regPassword").value;

            try {
                const response = await fetch(`${API_URL}/register`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ nama: nama, email: email, password: password })
                });

                const data = await response.json();

                if (response.ok) {
                    alert("Berhasil daftar! Silakan masuk bro.");
                    // Opsional: Reload halaman biar user bisa langsung login
                    window.location.reload(); 
                } else {
                    alert("Gagal: " + data.pesan);
                }
            } catch (error) {
                alert("Server Flask-nya belum nyala!");
                console.error(error);
            }
        });
    }

    // ==========================================
    // 4. LOGIKA TOMBOL KELUAR (DI PROFIL.HTML)
    // ==========================================
    const btnLogout = document.getElementById("btnLogout");
    if (btnLogout) {
        btnLogout.addEventListener("click", function() {
            const yakinKeluar = confirm("Yakin mau keluar akun?");
            
            if (yakinKeluar) {
                console.log("Menghapus token... Logout berhasil.");
                localStorage.removeItem(TOKEN_KEY);
                localStorage.removeItem("user_nama");
                window.location.replace("login.html");
            }
        });
    }
});