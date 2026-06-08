"""
================================================================================
           MANUAL BOOK & SYSTEM DOCUMENTATION: MULTI-SHAPE CYPHER ENGINE
================================================================================
Stack   : Python 3.x, OpenCV, MediaPipe, PyOpenGL, Pygame, NumPy
Target  : Portofolio Cybersecurity (GitHub / Vercel)
================================================================================

1. PRASYARAT & PERSIAPAN SISTEM (PREREQUISITES)
--------------------------------------------------------------------------------
Sebelum menjalankan program, pastikan lingkungan perangkat keras dan perangkat
lunak berikut telah disiapkan:

* Perangkat Keras (Hardware):
  - Webcam / Kamera Bawaan Laptop (Berfungsi dengan baik untuk tracking AI).
  - Pencahayaan yang cukup agar MediaPipe mengenali koordinat jari secara akurat.

* Perangkat Lunak (Software):
  - Python versi 3.8 s.d 3.11 (Sangat direkomendasikan untuk stabilitas OpenGL).
  - Pip (Python Package Installer) versi terbaru.

* Instalasi Modul / Library (Ketik di Terminal/CMD):
  pip install opencv-python mediapipe pygame pyopengl numpy

================================================================================

2. KOMPOSISI FILE PROYEK (PROJECT COMPOSITION)
--------------------------------------------------------------------------------
Untuk memastikan struktur proyek rapi di dalam repositori GitHub Anda, susun 
folder kerja Anda dengan komposisi sebagai berikut:

📂 cyber-security-aura/         <-- Folder Utama Proyek
 │
 ├── 📄 index.py                <-- Kode Utama Aplikasi (Engine & Render)
 ├── 📄 dokumentasi.py          <-- File Ini (Buku Panduan & Manual Book)
 └── 📄 requirements.txt        <-- Daftar Libs (Isi: opencv-python, dll)

================================================================================

3. ALUR EKSEKUSI PROGRAM (EXECUTION FLOW / LIFECYCLE)
--------------------------------------------------------------------------------
Berikut adalah urutan bagaimana program berjalan dari awal dinyalakan hingga
dimatikan secara aman:

  [ START ]
      │
      ▼
  [ 1. Inisialisasi ] ──► Load data NumPy (Geometri Perisai, Gembok, Emoji).
      │               ──► Setup Window Pygame & Context PyOpenGL (3D View).
      ▼
  [ 2. Spawn Thread ] ──► Mengaktifkan 'camera_cyber_thread' (AI Deteksi).
      │
      ├──► [ THREAD AI (Looping) ]
      │        Membaca Frame Kamera ──► Proses MediaPipe ──► Update Status
      │                                                         │
      ▼                                                         ▼
  [ 3. Main Loop Grafik (60 FPS) ] ◄────────────────────────────┘
      │
      ├───► A. Clear Screen & Draw Matrix Background (Hujan Biner dinamis).
      ├───► B. Render Mini Webcam HUD di pojok kanan atas layar.
      ├───► C. Hitung Animasi Morphing Partikel (Lerp 0.09 ke posisi target).
      ├───► D. Render Objek Utama (Jika PERISAI: Jalankan rotasi dual-ring).
      ├───► E. Render Teks Status Stratejik (Contoh: "SYSTEM SAFE").
      │
      ▼
  [ 4. Cek Input Exit? ] ──► (Tombol ESC atau silang window ditekan).
      │
      ├───► TIDAK: Kembali ke Langkah 3 (Ulangi Loop).
      └───► YA   : Lanjut ke Shutdown.
      │
      ▼
  [ 5. Safe Shutdown ] ──► Matikan flag 'running' -> Lepas Kamera (cap.release).
      │                ──► Tutup Jendela Pygame -> [ END / EXIT ].

================================================================================

4. ARSITEKTUR SISTEM (MULTI-THREADING)
--------------------------------------------------------------------------------
Aplikasi ini berjalan pada dua thread utama untuk menjaga performa tetap 60 FPS:
* Thread AI (Kamera)  : OpenCV membaca kamera -> MediaPipe menghitung posisi jari
                        -> Status disimpan di memori bersama (shared_data).
* Thread Main (Grafik): Pygame mengelola jendela -> NumPy simulasi partikel 3D 
                        -> PyOpenGL merender visualisasi akhir ke layar.

5. MATRIKS GESTUR TANGAN (INPUT AI)
--------------------------------------------------------------------------------
Sistem otomatis mengubah bentuk partikel berdasarkan deteksi jumlah jari terbuka:
* NO_HANDS --> Kamera kosong          --> Kabut Abstrak Renggang  (BIRU)
* ABSTRAK  --> Hanya 1 jari telunjuk  --> Emoji Tersenyum Statis   (CYAN)
* PERISAI  --> Tangan terbuka (>= 3)  --> Perisai & Dual-Orbit Ring (HIJAU)
* GEMBOK   --> Tangan mengepal (= 0)  --> Gembok & Alert Berkedip  (MERAH)

6. STRUKTUR PARTIKEL MODE PERISAI (TOTAL: 2.500 PARTIKEL)
--------------------------------------------------------------------------------
Khusus mode PERISAI HIJAU, partikel dipecah secara matematis menjadi 3 bagian:
* Partikel 0 - 1199 (1200 titik) : Badan perisai padat (elegan, tidak offset).
* Partikel 1200 - 1299 (100 titik): Garis lurus horizontal menutup mahkota atas.
* Partikel 1300 - 1899 (600 titik): Lingkaran DALAM (Radius 1.45, putar KANAN).
* Partikel 1900 - 2499 (600 titik): Lingkaran LUAR  (Radius 1.90, putar KIRI).

7. TRANSISI FLUIDA (ANIMASI MORPHING)
--------------------------------------------------------------------------------
Perubahan bentuk antar-gestur menggunakan rumus Linear Interpolation (Lerp):
    Delta_Pos = (Target_Pos - Current_Pos) * 0.09
Konstanta 0.09 memberikan efek redaman halus (easing) saat partikel berpindah.

================================================================================
                    PANDUAN KUSTOMISASI PARAMETER (DEVELOPER)
================================================================================

A. MENGATUR KECEPATAN HUJAN BINER (MATRIX BACKGROUND)
Cari fungsi 'draw_binary_matrix(status)' -> Ubah angka pada variabel 'speed':
    - NO_HANDS : speed = 5   (Lambat/Tenang)
    - PERISAI  : speed = 18  (Sedang/Stabil)
    - GEMBOK   : speed = 45  (Sangat Cepat/Kritis)

B. MENGATUR KECEPATAN PUTARAN LINGKARAN (DUAL-ORBIT)
Cari blok 'if current_status == "PERISAI":' di loop utama (paling bawah file):
    - Lingkaran Dalam: glRotatef(rotation_angle * 1.2, 0, 0, 1) -> Ganti 1.2
    - Lingkaran Luar : glRotatef(-rotation_angle * 0.8, 0, 0, 1) -> Ganti 0.8
    *(Tips: Tetap biarkan tanda minus '-' pada lingkaran luar agar arahnya ke kiri)*

C. MENGATUR UKURAN/RADIUS LINGKARAN CYBER
Cari rumus perulangan lingkaran di Langkah ke-2:
    - Lingkaran Dalam: radius = np.random.uniform(1.4, 1.5)
    - Lingkaran Luar : radius = np.random.uniform(1.85, 1.95)

================================================================================
                  STATUS INDIKATOR HUD: [ SYSTEM SAFE ] ACTIVATED
================================================================================
"""