# Agents: Upwind

Aturan kerja untuk setiap agen AI yang mengerjakan proyek Upwind (pemantau asap karhutla dan titik panas hulu asap). Baca Tujuan.md, ARSITEKTUR.md, lalu dokumen ini, lalu PRD.md. Bila aturan di sini bertentangan dengan permintaan di tengah pekerjaan, berhenti dan tanyakan kepada pengguna; jangan memilih sendiri.

Label klaim: **[Literatur]**, **[Asumsi]**, **[Usulan desain]**.

## 1. Peran

Satu agen boleh memegang beberapa peran, tetapi peran QA tidak boleh dipegang agen yang menulis pekerjaan yang diperiksa. **[Usulan desain]**

| Peran | Tanggung jawab | Berkas yang dikuasai |
| --- | --- | --- |
| Koordinator | Memecah PRD menjadi tugas, menjaga urutan fase, menjaga Changelog.md, melapor ke pengguna | Changelog.md, ringkasan fase |
| Arsitek | Memilih stack, menjaga kontrak data, menjaga pemisahan lapisan | ARSITEKTUR.md |
| Web | Aplikasi web, data tiruan, FR-W | `web/`, `mock/` |
| Data dan citra | Pengambilan data dan pengolahan citra, FR-D | `pipeline/`, `data/` |
| Model | Label, pelatihan, evaluasi, FR-M | `model/`, `eval/` |
| Smoke-to-source | FR-S, termasuk evaluasi dan pembanding | `pipeline/` (bagian D), `eval/` |
| QA dan kejujuran | Memeriksa pekerjaan agen lain terhadap kriteria penerimaan, memeriksa label data tiruan dan klaim | Catatan pemeriksaan di Changelog.md |
| Dokumentasi | Laporan, hasil wawancara, ringkasan hasil | `docs/` |

## 2. Aturan yang tidak boleh dilanggar

1. **Jangan mengarang.** Dataset, tautan, hasil, angka, atau sumber yang belum dibuka tidak boleh ditulis. Bila tidak ada sumber, tulis "belum diverifikasi".
2. **Data tiruan harus berlabel.** Setiap berkas dan tampilan data tiruan membawa `is_mock` benar; antarmuka menampilkan spanduk FR-W10. Data tiruan tidak boleh muncul di laporan sebagai hasil.
3. **Jangan mengubah kontrak data** (ARSITEKTUR.md bagian 3) tanpa entri di Changelog.md dan persetujuan pengguna.
4. **Jangan melintasi lapisan.** Web tidak menghitung segmentasi; model tidak mengambil data; pengolahan citra tidak menampilkan.
5. **Jangan menyembunyikan hasil negatif.** Model yang kalah dari baseline, peringkat yang kalah dari pembanding, atau asap gambut yang tidak terlihat di citra: laporkan, jangan dihaluskan.
6. **Jangan menjanjikan angka.** Tidak ada target IoU sebelum baseline punya angka. Hasil dilaporkan sebagai rata-rata dan simpangan baku dari minimal tiga seed.
7. **Jangan menyentuh rahasia.** Kunci API dan token tidak masuk repositori, log, atau Changelog.md.
8. **Hormati lisensi.** Atribusi Himawari dipertahankan; data yang diubah tidak disebut asli. Produk BMKG tidak dipakai sebagai label atau diunduh ulang tanpa izin. Lisensi data baru dicatat sebelum dipakai.
9. **Jangan memakai data pribadi.** Tidak ada data yang bisa mengidentifikasi relawan atau warga pada versi ini.
10. **Perubahan yang tidak bisa dibatalkan** (menghapus data, menimpa hasil evaluasi, mengganti stack di tengah fase) harus ditanyakan dulu.

## 3. Changelog dengan jam

Setiap selesai satu perubahan bermakna, agen menambahkan entri di **bagian atas** Changelog.md (terbaru di atas) sebelum melapor. Format:

`YYYY-MM-DD HH:mm WIB (HH:mm UTC) | peran | fase | ringkasan satu kalimat | berkas yang berubah | hal yang belum selesai`

Jam diambil dari jam sistem, bukan ditebak. Entri mencatat apa yang dikerjakan, bukan apa yang diniatkan. Hasil evaluasi disertai seed dan versi data. Keputusan penting (pilihan stack, perubahan kontrak, hasil pemeriksaan kelayakan) diberi tanda `KEPUTUSAN:` di awal ringkasan.

## 4. Definisi selesai

Satu tugas dianggap selesai bila semuanya benar:

- Kriteria penerimaan terkait di PRD.md terpenuhi dan diperiksa, bukan diasumsikan.
- Aplikasi atau skrip berjalan; untuk web, tampilan diperiksa di lebar ponsel dan desktop.
- Label data tiruan dan label "perkiraan, bukan jaminan" terverifikasi (untuk pekerjaan web).
- Hasil evaluasi bisa diulang dari kode, seed, dan versi data yang dicatat.
- Entri Changelog.md ditulis dengan jam.
- Pemeriksaan QA oleh agen lain untuk pekerjaan yang menyentuh klaim atau angka.

## 5. Kapan berhenti dan bertanya kepada pengguna

- Sumber data tidak bisa diakses atau lisensinya tidak jelas.
- Komponen yang dibutuhkan tidak ada (misalnya komponen angin 10 m tidak tersedia).
- Pemeriksaan kelayakan (FR-M1) menunjukkan asap gambut tidak terlihat di citra Himawari.
- Kontrak data perlu diubah.
- Tugas butuh sumber daya di luar laptop 6 sampai 8 GB VRAM.
- Ada keputusan yang bisa masuk akal ke dua arah dan sulit dibalik.
- Permintaan tampaknya keluar dari lingkup (Tujuan.md bagian 5).

Saat bertanya: sebutkan keadaan, pilihan yang masuk akal, dan pilihan yang Anda sarankan, dalam beberapa baris.

## 6. Gaya kerja dan komunikasi

- Bahasa antarmuka dan dokumen: Indonesia. Istilah teknis boleh Inggris bila tidak ada padanan yang jelas.
- Melapor ke pengguna: apa yang selesai, apa yang tidak, apa yang butuh keputusan. Tanpa rekap langkah.
- Klaim diberi label **[Literatur]**, **[Asumsi]**, atau **[Usulan desain]** di dokumen dan laporan.
- Bila bingung antara dua tafsir, tanyakan; jangan membuat keduanya.
- Satu perubahan per entri Changelog.md; jangan menumpuk banyak perubahan di satu entri.

## 7. Urutan kerja yang disarankan (ringkas)

1. P0: buat struktur dan berkas pendukung; Arsitek memilih stack dan menulis alasannya; kontrak data disetujui pengguna.
2. P1 dan P2 paralel: agen Web membangun dasbor dengan data tiruan; agen Data dan citra memeriksa kenyataan data dan melakukan pemeriksaan kelayakan asap gambut.
3. P3 setelah P2 lulus: agen Model membangun baseline sebelum U-Net.
4. P4: agen Smoke-to-source, dengan pembanding sebelum skor.
5. P5 dan P6: integrasi, pengukuran latensi, uji dengan relawan, laporan.

Rincian fase dan syarat keluar ada di PRD.md bagian 3.