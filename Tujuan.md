# Tujuan: Upwind

**Upwind: pemantau asap karhutla dan titik panas hulu asap.** Itu nama dan penjelas aplikasi ini.

Dokumen ini menjawab satu pertanyaan: untuk apa proyek ini ada. Baca ini sebelum menyentuh apa pun yang lain. Bila sebuah keputusan teknis bertentangan dengan dokumen ini, dokumen ini yang menang dan keputusan itu dilaporkan, bukan dilakukan diam-diam.

Label klaim yang dipakai di seluruh dokumen:

- **[Literatur]**: dari sumber yang sudah dibuka dan dibaca.
- **[Asumsi]**: dugaan yang belum terbukti.
- **[Usulan desain]**: keputusan rancangan yang bisa diubah.

## 1. Latar belakang

Proyek besar mata kuliah Pengolahan Citra Digital dan AI, bertema kebakaran hutan dan lahan (karhutla) di Indonesia. Wilayah studi: Riau dan Kalimantan Tengah (lahan gambut). Pengerjaan oleh tim 2 sampai 4 orang dengan laptop GPU 6 sampai 8 GB VRAM. **[Usulan desain]**

Arahan dosen pembimbing (22 Oktober 2026): fokus pada segmentasi kabut asap yang diperbarui kurang dari 24 jam, dengan keluaran berupa dasbor yang membantu relawan dan tim satgas memadamkan api. Lingkup sengaja dibuat kecil agar tidak terlalu berat.

## 2. Tujuan proyek

Membangun sistem yang, dari citra satelit geostasioner Himawari-9, menghasilkan peta asap karhutla yang diperbarui secara berkala dan menunjukkan kepada tim lapangan titik panas mana yang paling mungkin menjadi sumber asap tersebut. **[Usulan desain]**

Dua inti kontribusi, disepakati pengguna pada 22 Oktober 2026:

1. **Segmentasi asap dari urutan frame.** Model menerima beberapa citra Himawari berturut-turut (setiap 10 menit), bukan satu citra. Hipotesis: gerak dan penyebaran asap membantu memisahkannya dari awan. Ini hipotesis, belum terbukti; ablation satu frame lawan beberapa frame yang menjawabnya. **[Asumsi]**
2. **Titik panas hulu asap (smoke-to-source).** Menggabungkan arah gerak asap, angin, dan titik panas untuk mengurutkan titik panas dari yang paling mungkin menjadi sumber asap. Skor ini heuristik dan harus dievaluasi terhadap pembanding sederhana. **[Usulan desain]**

Pembagian peran yang tidak boleh tercampur:

| Lapisan | Tugas | Bukan tugasnya |
| --- | --- | --- |
| Pengolahan citra digital | Mengunduh, mengoreksi, memotong, masking awan dan malam, menyusun tumpukan band, merapikan mask, menghitung luas | Belajar dari data |
| Model AI | Mempelajari kelas asap per piksel, menghasilkan probabilitas dan ketidakpastian | Menampilkan hasil, mengambil data |
| Aplikasi web | Menampilkan hasil dan lapisan konteks, menerima interaksi pengguna | Menghitung inti segmentasi |

## 3. Pengguna

| Pengguna | Kebutuhan | Perangkat |
| --- | --- | --- |
| Relawan lapangan | Tahu di mana asap dan titik panas mana yang perlu dicek dulu | Ponsel, data terbatas |
| Komando tim satgas | Gambaran luas, ringkasan, riwayat 24 jam | Desktop atau layar besar |

Satu web responsif melayani keduanya. Kebutuhan di atas adalah **[Asumsi]** sampai ada wawancara dengan relawan; wawancara berjalan paralel dan hasilnya merevisi PRD.

## 4. Kriteria sukses

Untuk proyek mata kuliah:

- Model dibandingkan dengan baseline yang jujur, dan hasilnya dilaporkan apa adanya, termasuk bila selisihnya kecil. Tidak ada angka IoU yang dijanjikan sebelum baseline punya angka sendiri.
- Latensi dari pengambilan citra sampai tampil di dasbor diukur dan dilaporkan sebagai median dan persentil ke-95. Sasaran: kurang dari 60 menit pada siang hari. Syarat dosen (kurang dari 24 jam) pasti terpenuhi. **[Usulan desain]**
- Peringkat titik panas hulu asap dievaluasi terhadap pembanding sederhana (titik panas terdekat dengan pusat asap, dan acak).
- Dasbor berjalan di laptop lokal untuk demo dan bisa dicoba teman relawan.

Untuk pengguna:

- Relawan yang mencoba dasbor bisa menjawab "di mana asapnya, ke mana bergerak, titik panas mana yang saya cek dulu" tanpa penjelasan tambahan. Ini diuji dengan wawancara dan uji coba singkat.

## 5. Di luar lingkup (ditunda)

Prediksi arah penjalaran api, laporan dan konfirmasi warga, segmentasi area terbakar Sentinel-2, akun pengguna, notifikasi, dan penayangan publik di internet. Semuanya sah sebagai pengembangan lanjutan, tetapi tidak boleh masuk sebelum lingkup inti selesai.

## 6. Prinsip yang tidak boleh dilanggar

1. **Jujur soal batas.** Asap bukan titik api. Titik panas satelit meleset dari posisi api sebenarnya: validasi BRIN di Kalimantan Tengah mendapat akurasi 51,33% dalam radius 2 km untuk algoritma terbaik pada Himawari-8. **[Literatur]** Semua keluaran berlabel "perkiraan, bukan jaminan".
2. **Tidak ada data karangan yang tampil sebagai data asli.** Data tiruan wajib berlabel jelas di antarmuka dan di berkas (lihat PRD, FR-W10).
3. **Malam hari dan awan tebal tampil apa adanya.** Dasbor menyatakan "tidak ada pembaruan asap" daripada menyembunyikan celahnya.
4. **Tidak mengklaim kebaruan.** Produk BMKG Citra Sebaran Asap sudah ada dan beroperasi (siang sampai sore). **[Literatur]** Kontribusi dirumuskan sebagai evaluasi di asap gambut, segmentasi urutan frame, ketidakpastian per piksel, latensi terukur, dan peringkat titik panas hulu asap, sampai tinjauan pustaka selesai.
5. **Lisensi dihormati.** Himawari di AWS memerlukan atribusi dan data yang diubah tidak boleh disebut asli. Produk BMKG tidak dipakai sebagai label tanpa izin.

## 7. Sumber

- [Himawari di AWS Open Data](https://registry.opendata.aws/noaa-himawari/)
- [BMKG Satelit Cuaca](https://www.bmkg.go.id/satelit/)
- [BRIN: validasi hotspot Himawari-8 Kalimantan Tengah](https://karya.brin.go.id/id/eprint/11573/)
- [JAXA Himawari-8 Wild Fire product](https://www.eorc.jaxa.jp/ptree/documents/README_H08_L2WLF.txt)
- [SIT-FUSE, segmentasi asap GOES](https://arxiv.org/pdf/2510.09845)