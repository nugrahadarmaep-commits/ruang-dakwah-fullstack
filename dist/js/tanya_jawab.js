// ==========================================
// TANYA_JAWAB.JS - FITUR GLOBAL CHAT (CRUD LENGKAP)
// ==========================================

document.addEventListener("DOMContentLoaded", function() {
    const chatContainer = document.getElementById("chatContainer");
    const chatInput = document.getElementById("chatInput");
    const sendBtn = document.getElementById("btnKirimChat");
    
    // Ambil data user yang lagi login buat nyocokin kepemilikan chat
    const userDataStr = localStorage.getItem("ruang_dakwah_user");
    const namaSaya = userDataStr ? JSON.parse(userDataStr).nama : "";
    
    if (!chatContainer) return;

    // 1. SEDOT SEMUA HISTORI CHAT (READ)
    async function loadChat() {
        try {
            const response = await fetch("http://127.0.0.1:5000/chat_global");
            const result = await response.json();
            
            if (response.ok) {
                chatContainer.innerHTML = ""; 
                result.data.forEach(chat => {
                    // Masukin ID chat-nya juga biar JS tau mana yang mau dihapus
                    tambahBubbleChat(chat.id, chat.nama, chat.pesan);
                });
                scrollToBottom();
            }
        } catch (error) {
            chatContainer.innerHTML = "<p class='text-danger text-center'>Gagal memuat chat.</p>";
        }
    }

    // 2. TEMBAK CHAT BARU KE FLASK (CREATE)
    async function kirimChat() {
        const teks = chatInput.value.trim();
        if (!teks) return;

        const token = localStorage.getItem("ruang_dakwah_jwt");
        if (!token) {
            alert("Login untuk mengirim pesan!");
            window.location.href = "login.html";
            return;
        }

        try {
            const response = await fetch("http://127.0.0.1:5000/kirim_chat", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                },
                body: JSON.stringify({ pesan: teks })
            });

            if (response.ok) {
                chatInput.value = ""; 
                loadChat(); // Refresh chat biar langsung dapet ID dari database
            } else {
                const result = await response.json();
                alert(result.pesan);
            }
        } catch (error) {
            alert("Gagal kirim pesan!");
        }
    }

    // 3. FUNGSI HAPUS CHAT (DELETE) - Sengaja ditaruh di window biar bisa dipanggil dari HTML
    window.hapusChat = async function(idChat) {
        // Munculin pop-up konfirmasi
        if (!confirm("Yakin mau mehapus pesan ini?")) return;

        const token = localStorage.getItem("ruang_dakwah_jwt");
        if (!token) return;

        try {
            // Tembak API DELETE lu
            const response = await fetch(`http://127.0.0.1:5000/hapus_chat/${idChat}`, {
                method: "DELETE",
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            });
            
            const result = await response.json();

            if (response.ok) {
                // Kalau sukses, langsung sedot ulang data terbaru dari database
                loadChat();
            } else {
                alert("Gagal hapus: " + result.pesan);
            }
        } catch (error) {
            alert("Waduh, koneksi ke server putus!");
        }
    };

    // --- TEMPLATE KARTU BUBBLE CHAT ---
    function tambahBubbleChat(id, nama, pesan) {
        // Cek apakah chat ini punya user yang lagi login?
        // Kalau iya, munculin tong sampah. Kalau bukan, biarin kosong.
        let tombolHapus = "";
        if (nama === namaSaya) {
            tombolHapus = `<i class="bi bi-trash3-fill text-danger ms-auto" style="cursor: pointer; transition: 0.2s;" onclick="hapusChat(${id})" title="Tarik Pesan"></i>`;
        }

        const elemenBaru = `
        <div class="qa-group mb-3" style="animation: fadeIn 0.4s ease-out;">
            <div class="d-flex gap-3">
                <div class="bg-secondary bg-opacity-10 rounded-circle d-flex align-items-center justify-content-center shadow-sm" style="width: 35px; height: 35px; min-width: 35px;">
                    <i class="bi bi-person text-muted"></i>
                </div>
                <div class="bg-white p-3 rounded-4 shadow-sm border-start border-4 border-teal d-flex flex-column" style="border-left-color: #008080 !important; width: 100%;">
                    
                    <div class="d-flex justify-content-between align-items-start mb-1">
                        <p class="small fw-bold mb-0" style="color: #008080;">${nama}</p>
                        ${tombolHapus} </div>
                    
                    <p class="small mb-0 text-dark">${pesan}</p>
                </div>
            </div>
        </div>`;
        chatContainer.insertAdjacentHTML("beforeend", elemenBaru);
    }

    function scrollToBottom() {
        window.scrollTo({ top: document.body.scrollHeight, behavior: "smooth" });
    }

    // PANGGIL FUNGSI LOAD PAS HALAMAN DIBUKA
    loadChat();

    // PASANG SENSOR KLIK & ENTER
    if(sendBtn) sendBtn.addEventListener("click", kirimChat);
    if(chatInput) chatInput.addEventListener("keypress", function(e) {
        if (e.key === "Enter") kirimChat();
    });
});