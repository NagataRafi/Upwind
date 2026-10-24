# Ringkasan Agen: Upwind

> [!IMPORTANT]
> Dokumen ini adalah ringkasan operasional dan pintu masuk awal sesi. [Agents.md](file:///C:/Users/ADMIN/upwind_proj/Agents.md) tetap otoritatif. Mulai sekarang, di awal setiap sesi baca dokumen ini dan entri teratas [Changelog.md](file:///C:/Users/ADMIN/upwind_proj/Changelog.md) lebih dulu; dokumen panjang hanya dibaca bila diperlukan rincian. Sumber kerja: `C:\Users\ADMIN\upwind_proj` (jangan bekerja/commit/push di folder Google Drive).

---

## 1. Aturan Inti (Tidak Boleh Dilanggar)

1. **Jangan Mengarang**: Dilarang menulis dataset, angka evaluasi, tautan, atau sumber yang belum diverifikasi secara nyata di disk/koneksi. Bila belum terbukti, tulis "belum diverifikasi".
2. **Data Tiruan Wajib Berlabel**: Setiap data contoh wajib membawa `is_mock: true`. UI wajib menampilkan spanduk permanen data contoh (FR-W10). Data tiruan dilarang dilaporkan sebagai hasil model/evaluasi.
3. **Integritas Repositori & Kontrak**:
   - Dilarang keras melakukan *force-push* atau menulis ulang riwayat git tanpa persetujuan eksplisit pengguna.
   - Dilarang mengubah kontrak data ([Arsitektur.md](file:///C:/Users/ADMIN/upwind_proj/Arsitektur.md) Bagian 3) tanpa persetujuan pengguna dan entri Changelog.
   - Dilarang melintasi lapisan (Web tidak menghitung inferensi; Model tidak mengambil data mentah; Pipeline citra tidak merender UI dasbor).
4. **Kejujuran Hasil & Batasan**: Laporkan hasil negatif apa adanya (asap tidak terlihat, baseline kalah, latensi lambat). Jangan menjanjikan metrik sebelum baseline terukur.
5. **Kerahasiaan & Lisensi**: Jangan menyimpan kunci API/token di kode/log. Patuhi lisensi data (Himawari AWS, JAXA, OSM, FIRMS).

---

## 2. Changelog dengan Jam Sistem

Setiap selesai satu perubahan bermakna, tambahkan entri di bagian paling atas [Changelog.md](file:///C:/Users/ADMIN/upwind_proj/Changelog.md) sebelum melapor:
`YYYY-MM-DD HH:mm WIB (HH:mm UTC) | peran | fase | ringkasan satu kalimat | berkas yang berubah | hal yang belum selesai`
- Jam diambil dari jam sistem, bukan ditebak.
- Keputusan penting diawali tanda `KEPUTUSAN:`.
- Temuan teknis penting diawali tanda `TEMUAN:`.

---

## 3. Kapan Harus Berhenti dan Bertanya

Berhenti dan tanyakan opsi kepada pengguna bila:
- Sumber data tidak dapat diakses atau lisensinya tidak jelas.
- Asap gambut tidak terlihat pada citra satelit (evaluasi kelayakan FR-M1).
- Tugas membutuhkan sumber daya melebihi laptop lokal (6–8 GB VRAM).
- Ditemukan konflik riwayat git atau perubahan yang tidak dapat dibatalkan.
- Permintaan berada di luar cakupan inti proyek ([Tujuan.md](file:///C:/Users/ADMIN/upwind_proj/Tujuan.md) Bagian 5).

---

## 4. Status Fase Saat Ini

| Fase | Status | Catatan Ringkas |
| :--- | :---: | :--- |
| **P0 (Fondasi)** | **Selesai** | Kontrak data, pemilihan stack, arsitektur 3 lapis disetujui. |
| **P1 (Web Mock)** | **Selesai** | Dasbor responsif dengan data tiruan terverifikasi Playwright (`is_mock: true`). |
| **P2 (Pipeline Data Asli)** | **Aktif / Tertahan Evaluasi** | Unduhan & dekode raw HSD Himawari-8/9 mandiri, penyejajaran grid komposit, topeng awan dingin B13, dan pemotongan kotak Riau/Kalteng selesai. **Tertahan**: menunggu penilaian visual kelayakan asap (FR-M1) oleh pengguna against NASA Worldview. Titik panas AHI-L2WLF 2019 menunggu akun JAXA P-Tree / FIRMS MAP_KEY. |
| **P3–P6** | **Belum Dimulai** | Menunggu syarat keluar P2 terpenuhi. |

---

## 5. Tautan Dokumen Otoritatif

- [Tujuan.md](file:///C:/Users/ADMIN/upwind_proj/Tujuan.md): Tujuan proyek, kriteria sukses, batasan ruang lingkup.
- [Arsitektur.md](file:///C:/Users/ADMIN/upwind_proj/Arsitektur.md): Arsitektur 3 lapis, alur data, kontrak data (SmokeFrame dkk).
- [Agents.md](file:///C:/Users/ADMIN/upwind_proj/Agents.md): Aturan kerja, pembagian peran, etika & kejujuran (*otoritatif*).
- [PRD.md](file:///C:/Users/ADMIN/upwind_proj/PRD.md): Rincian kebutuhan fungsional (FR-W, FR-D, FR-M, FR-S) dan syarat keluar tiap fase.
- [Changelog.md](file:///C:/Users/ADMIN/upwind_proj/Changelog.md): Riwayat perubahan kronologis dengan jam sistem.
