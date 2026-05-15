// ==========================================
// JADWAL.JS - PENARIK DATA KAJIAN DARI FLASK
// ==========================================

document.addEventListener("DOMContentLoaded", async function() {
    // Cari elemen HTML tempat kita bakal naruh kartu kajian
    const jadwalContainer = document.getElementById("jadwalContainer");
    
    // Kalau nggak ada container-nya (berarti user lagi nggak di halaman jadwal), berhentikan script.
    if (!jadwalContainer) return;

    try {
        // Tembak API Flask pakai jalur GET
        const response = await fetch(`${API_URL}/kajian`);
        const result = await response.json();

        if (response.ok) {
            const daftarKajian = result.data;
            
            // Kosongkan dulu isi containernya biar bersih
            jadwalContainer.innerHTML = ""; 

            // Looping data dari SQLite dan cetak jadi Kartu HTML
            daftarKajian.forEach(kajian => {
                const cardHTML = `
                    <div class="card p-4 mb-3 shadow-sm border-0" style="border-radius: 20px;">
                        <h5 class="fw-bold mb-3 text-uppercase">${kajian.judul}</h5>
                        <p class="text-muted mb-2">
                            <strong style="color: #008080;"><i class="bi bi-person-fill"></i> ${kajian.ustaz}</strong>
                        </p>
                        <p class="text-muted mb-1"><i class="bi bi-clock"></i> ${kajian.tanggal}, ${kajian.waktu}</p>
                        <p class="text-muted mb-3"><i class="bi bi-geo-alt"></i> ${kajian.lokasi}</p>
                        
                        <div class="d-flex gap-2 mt-2">
                            <button class="btn btn-outline-teal w-50 fw-bold" style="border-color: #008080; color: #008080; border-radius: 10px;">Detail</button>
                            <!-- Tombol ini nanti kita fungsikan buat API Pendaftaran Tiket -->
                            <button class="btn w-50 fw-bold shadow-sm" style="background-color: #008080; color: white; border-radius: 10px;" onclick="daftarKajian(${kajian.id})">Daftar</button>
                        </div>
                    </div>
                `;
                // Suntikkan kartu ke dalam HTML
                jadwalContainer.innerHTML += cardHTML;
            });
        }
    } catch (error) {
        console.error("Waduh, gagal narik data:", error);
        jadwalContainer.innerHTML = `<div class="alert alert-danger">Server mati bro! Nyalain python app.py dulu.</div>`;
    }
});

// Fungsi sementara buat tombol daftar
function daftarKajian(idKajian) {
    alert("Fitur daftar ke Kajian ID " + idKajian + " lagi kita bangun bos!");
}