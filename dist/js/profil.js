// ==========================================
// PROFIL.JS - NGURUSIN HURUF "U" (UPDATE)
// ==========================================

document.addEventListener("DOMContentLoaded", function() {
    // elemen-elemen form di profil.HTML
    const formProfil = document.getElementById("formUpdateProfil");
    const inputNama = document.getElementById("editNama");
    const inputEmail = document.getElementById("editEmail");

    // Kalau kita gak lagi di halaman profil, stop scriptnya
    if (!formProfil) return;

    // 1. OTOMATIS NGISI FORM SAMA DATA LAMA
    const userData = JSON.parse(localStorage.getItem("ruang_dakwah_user"));
    if (userData) {
        inputNama.value = userData.nama;
        inputEmail.value = userData.email;
    }

    // 2. PAS TOMBOL UPDATE DIKLIK
    formProfil.addEventListener("submit", async function(e) {
        e.preventDefault(); // Biar halamannya gak nge-refresh sendiri

        const token = localStorage.getItem("ruang_dakwah_jwt");
        if (!token) {
            alert("Login dulu bos!");
            window.location.href = "login.html";
            return;
        }

        const namaBaru = inputNama.value.trim();
        const emailBaru = inputEmail.value.trim();

        try {
            // Tembak API Update pakai metode PUT
            const response = await fetch("http://127.0.0.1:5000/update_profil", {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                },
                body: JSON.stringify({ 
                    nama_lengkap: namaBaru, 
                    email: emailBaru 
                })
            });

            const result = await response.json();

            if (response.ok) {
                alert(result.pesan); // Bakal muncul "SIUUUU! Profil berhasil diupdate!"
                
                // Update juga data yang ada di brankas browser biar sinkron
                localStorage.setItem("ruang_dakwah_user", JSON.stringify(result.user));
                
                // Refresh halaman biar namanya langsung berubah
                location.reload();
            } else {
                alert("Gagal bos: " + result.pesan);
            }
        } catch (error) {
            alert("Waduh, server Flask lu mati kayaknya!");
            console.error(error);
        }
    });
});