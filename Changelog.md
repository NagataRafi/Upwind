# Changelog

Catatan setiap perubahan, terbaru di atas. Setiap entri memuat tanggal dan jam. Aturan pengisian ada di Agents.md bagian 3.

Format entri:
`YYYY-MM-DD HH:mm WIB (HH:mm UTC) | peran | fase | ringkasan satu kalimat | berkas yang berubah | hal yang belum selesai`

Keputusan penting diberi awalan `KEPUTUSAN:`. Jam diambil dari jam sistem.

## Entri

2026-10-23 14:57 WIB (07:57 UTC) | QA dan kejujuran | P1 | KEPUTUSAN: pencatatan keterlambatan — kode web, generator mock, dan data tiruan P1 sudah dibuat agen sebelumnya pada 22 Okt tetapi tidak tercatat di Changelog; audit 23 Okt menemukan 15 FR-W sebagian dan 2 belum dicoba (W15 responsive, W17 visual); hasil audit: kontrak data dipenuhi penuh seluruh bidang SmokeFrame/Hotspot/WindSample/RankedSource/SystemStatus, semua is_mock true; solusi build yang bekerja: node_modules_old hampir kosong dan membuat junction di Google Drive gagal ("Incorrect function"), jadi salinan proyek dibuat di C:\Users\ADMIN\upwind_proj dengan node_modules di partisi lokal C:\Users\ADMIN\upwind_web_deps lewat junction, build dan dev server port 3000 berjalan sukses | Changelog.md | Pemeriksaan visual tampilan belum dilakukan; FR-W16 masih sebagian

2026-10-23 14:37 WIB (07:37 UTC) | QA dan kejujuran (audit) | P1 | Audit hasil P1 agen sebelumnya: kode web, generator mock, dan data tiruan ada; build berhasil dan dasbor berjalan di lingkungan lokal; kecocokan data dengan kontrak diperiksa; hasil audit diberikan kepada pengguna, belum ada kode diubah | web/src/*, mock/generate_mock_data.py, data/, Changelog.md | Pemeriksaan visual tampilan di lebar ponsel dan desktop oleh pengguna belum dilakukan; FR-W belum ditandai selesai penuh

2026-10-22 14:02 WIB (07:02 UTC) | Arsitek | P0 | Menyelaraskan dan mengonfirmasi kelengkapan seluruh bidang ARSITEKTUR.md Bagian 3, indeks bingkai per wilayah untuk FR-W9, serta penanganan motion 'tidak dapat dihitung' di docs/KONTRAK_DATA.md | docs/KONTRAK_DATA.md, Changelog.md | P1: Implementasi generator data tiruan di mock/ dan antarmuka web Upwind

2026-10-22 13:57 WIB (06:57 UTC) | Arsitek | P0 | KEPUTUSAN: Arsitek memilih stack web React 18 + Vite + TypeScript + Tailwind CSS + Leaflet (disajikan statis via Vite/API) karena type-safe untuk kontrak data, responsif ponsel/desktop, hemat data, dan ringan di laptop lokal; struktur folder fondasi dibuat dan perincian kontrak data difinalkan di docs/KONTRAK_DATA.md | data/, pipeline/, model/, mock/, api/, web/, eval/, docs/, docs/KONTRAK_DATA.md, Changelog.md | Menunggu persetujuan pengguna atas pilihan stack dan kontrak data sebelum memulai fase P1

2026-10-22 13:49 WIB (06:49 UTC) | Koordinator (Claude, perencanaan) | P0 | KEPUTUSAN: pengguna memilih nama aplikasi Upwind dengan penjelas "pemantau asap karhutla dan titik panas hulu asap"; nama ditambahkan ke judul semua berkas dan ke PRD (keputusan, ringkasan, FR-W17) | PRD.md, Tujuan.md, ARSITEKTUR.md, Agents.md, Changelog.md | Pemeriksaan bentrok nama dengan produk lain belum dilakukan

2026-10-22 13:43 WIB (06:43 UTC) | Koordinator (Claude, perencanaan) | P0 | Menulis draf PRD.md, Tujuan.md, ARSITEKTUR.md, Agents.md, dan Changelog.md; belum ada kode | PRD.md, Tujuan.md, ARSITEKTUR.md, Agents.md, Changelog.md | Kontrak data belum disetujui pengguna; stack belum dipilih agen; hal belum terverifikasi di PRD.md bagian 9 dan ARSITEKTUR.md bagian 7

2026-10-22 13:43 WIB (06:43 UTC) | Koordinator (Claude, perencanaan) | P0 | KEPUTUSAN: pengguna memilih web lebih dulu dengan data tiruan, stack diserahkan ke agen, demo di laptop lokal, pengguna relawan dan komando dengan satu web responsif, berkas .md sepaket, wawancara relawan paralel, VRAM 6 sampai 8 GB | PRD.md bagian 2 | Pilihan stack oleh agen Arsitek belum dicatat

2026-10-22 13:38 WIB (06:38 UTC) | Koordinator (Claude, perencanaan) | P0 | KEPUTUSAN: pengguna menyetujui inti proyek, yaitu segmentasi asap dari urutan frame Himawari dan titik panas hulu asap; fitur lain ditunda | Tujuan.md bagian 2 dan 5 | Tidak ada

2026-10-22 13:08 WIB (06:08 UTC) | Koordinator (Claude, perencanaan) | Pra-P0 | KEPUTUSAN: arah proyek berubah mengikuti arahan dosen pembimbing menjadi segmentasi asap near-real-time dan dasbor untuk relawan dan satgas; prediksi arah api, laporan warga, dan segmentasi Sentinel-2 ditunda | Tujuan.md bagian 1 dan 5 | Tidak ada
