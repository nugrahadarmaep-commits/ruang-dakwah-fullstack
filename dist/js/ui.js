document.addEventListener("DOMContentLoaded", function () {
  // ==========================================
  // AUTO-ACTIVE BOTTOM NAV
  // ==========================================
  // Biar ikon menu di bawah otomatis nyala hijau sesuai halaman
  const currentPath = window.location.pathname;
  const navLinks = document.querySelectorAll("nav.fixed-bottom .nav-link");

  navLinks.forEach((link) => {
    // Bersihkan semua state active
    link.classList.remove("active", "text-teal");
    link.classList.add("text-muted");

    // Deteksi halaman aktif
    if (link.href.includes(currentPath) && currentPath !== "/") {
      link.classList.remove("text-muted");
      link.classList.add("active", "text-teal");

      // Ganti ikon jadi versi 'fill' (opsi kalau Bootstrap Icon support)
      const icon = link.querySelector("i");
      if (
        icon &&
        !icon.classList.contains("bi-house-door-fill") &&
        link.href.includes("beranda")
      ) {
        icon.classList.replace("bi-house-door", "bi-house-door-fill");
      }
    }
  });

  // ==========================================
  // INTERAKSI FILTER JADWAL
  // ==========================================
  // Biar chip kategori bisa diklik dan ganti warna
  const filterChips = document.querySelectorAll(
    "header .d-flex.gap-2 button.btn",
  );
  if (filterChips.length > 0) {
    filterChips.forEach((chip) => {
      chip.addEventListener("click", function () {
        // Reset semua chip ke warna abu-abu (outline)
        filterChips.forEach((c) => {
          c.classList.remove("btn-teal", "active");
          c.classList.add("btn-outline-secondary");
          c.style.backgroundColor = "";
          c.style.color = "";
        });

        // Ubah chip yang diklik jadi hijau teal
        this.classList.remove("btn-outline-secondary");
        this.classList.add("btn-teal", "active");
        this.style.backgroundColor = "#008080";
        this.style.color = "white";
      });
    });
  }

  // ==========================================
  // INTERAKSIMODAL & TOAST KETIKA PENDAFTARAN
  // ==========================================
  const btnYakin = document.getElementById("btnYakinDaftar");
  const toastElement = document.getElementById("toastSukses");
  const modalElement = document.getElementById("modalDaftar");

  if (btnYakin && toastElement && modalElement) {
    const toast = new bootstrap.Toast(toastElement, { delay: 3000 });
    const modal =
      bootstrap.Modal.getInstance(modalElement) ||
      new bootstrap.Modal(modalElement);

    btnYakin.addEventListener("click", function () {
      modal.hide();
      toast.show();
    });
  }

  // ==========================================
  // INTERAKSI TOAST KETIKA BATALKAN TIKET
  // ==========================================
  const btnBatal = document.getElementById("btnBatalkanTiket");
  const toastBatalElement = document.getElementById("toastBatal");

  if (btnBatal && toastBatalElement) {
    const toastBatal = new bootstrap.Toast(toastBatalElement, { delay: 3000 });

    btnBatal.addEventListener("click", function () {
      toastBatal.show();
    });
  }

  // ==========================================
  // MESIN PENGGERAK DARK MODE
  // ==========================================
  const btnTema = document.getElementById("btnToggleTema");
  const ikonTema = document.getElementById("ikonTema");
  const temaAktif = localStorage.getItem("tema_pilihan") || "light";

  // Pasang saklar di <html>
  if (temaAktif === "dark") {
    document.documentElement.setAttribute("data-theme", "dark");
    document.documentElement.setAttribute("data-bs-theme", "dark");
    if (ikonTema) {
      ikonTema.classList.replace("bi-moon-fill", "bi-sun-fill");
      ikonTema.style.color = "#e2b93b";
    }
  }

  if (btnTema) {
    btnTema.addEventListener("click", function () {
      const modeSekarang = document.documentElement.getAttribute("data-theme");

      if (modeSekarang === "dark") {
        // balik ke mode terang
        document.documentElement.removeAttribute("data-theme");
        document.documentElement.removeAttribute("data-bs-theme"); // <--- INI LU LUPA MASUKIN BANG!
        localStorage.setItem("tema_pilihan", "light");
        ikonTema.classList.replace("bi-sun-fill", "bi-moon-fill");
        ikonTema.style.color = "var(--text-utama)";
      } else {
        document.documentElement.setAttribute("data-theme", "dark");
        document.documentElement.setAttribute("data-bs-theme", "dark");
        localStorage.setItem("tema_pilihan", "dark");
        ikonTema.classList.replace("bi-moon-fill", "bi-sun-fill");
        ikonTema.style.color = "#e2b93b";
      }
    });
  }

  // ==========================================
  // AUTO-SYNC NAMA USER DI SEMUA HALAMAN
  // ==========================================
  const dataUserStr = localStorage.getItem("ruang_dakwah_user");

  if (dataUserStr) {
    const dataUser = JSON.parse(dataUserStr);

    // Cari elemen nama di Beranda
    const namaBeranda = document.getElementById("namaBeranda");
    if (namaBeranda) {
      const namaDepan = dataUser.nama.split(" ")[0];
      namaBeranda.innerText = namaDepan + " 👋";
    }

    // Cari elemen nama di Profil (biar nggak usah nunggu profil.js)
    const namaTampil = document.getElementById("namaTampil");
    if (namaTampil) {
      namaTampil.innerText = dataUser.nama;
    }
  }
});
