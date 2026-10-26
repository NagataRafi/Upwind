# Daftar Hari Kandidat Asap Karhutla Berbasis Titik Panas (P3b)

> [!IMPORTANT]
> **Pernyataan Kejujuran Ilmiah (Titik Panas adalah Proksi):**
> Titik panas (*hotspot*) yang terdeteksi oleh sensor inframerah satelit polar (VIIRS S-NPP dan NOAA-20) adalah **PROKSI** keberadaan anomali termal/kebakaran aktif di permukaan tanah, **BUKAN BUKTI LANGSUNG** bahwa asap terlihat pada citra satelit geostasioner Himawari.
> Dalam kondisi riil di lapangan:
> 1. Kebakaran aktif berdaya tinggi dapat tertutup oleh lapisan awan tebal di atasnya sehingga asapnya tidak tampak pada kanal optik satelit. **[Literatur]**
> 2. Angin kencang dapat meniup gumpalan asap keluar dari kotak wilayah pantauan atau menguraikannya menjadi kabut sangat tipis. **[Literatur]**
> 3. Sebaliknya, asap pekat yang menyelimuti suatu daerah bisa jadi merupakan asap kiriman dari provinsi tetangga (*transboundary haze*) di mana titik api lokalnya bernilai nol. **[Literatur]**
> Oleh karena itu, seluruh klasifikasi jenis hari pada dokumen ini berstatus **[Asumsi]** hingga pengguna memverifikasi langsung kenampakan visualnya pada NASA Worldview.

---

## 1. Verifikasi Ketersediaan Arsip Data Satelit

Sebelum memilih hari kandidat, ketersediaan data satelit mentah di repositori AWS S3 Open Data telah diverifikasi langsung:

1. **Himawari-8 (2015 s.d. 2022) pada bucket `noaa-himawari8`:**
   - **Tahun 2015:** Arsip Himawari-8 di AWS dimulai pada tanggal **7 Juli 2015** (`AHI-L1b-FLDK/2015/07/07/0200/`). Periode puncak karhutla El Niño 2015 (Agustus s.d. Oktober 2015) **TERSEDIA LENGKAP** di AWS. **[Literatur]**
   - **Tahun 2019:** Arsip tersedia penuh sepanjang tahun 2019 (Januari s.d. Desember).
2. **Himawari-9 (2023 s.d. sekarang) pada bucket `noaa-himawari9`:**
   - **Tahun 2023:** Seluruh data operasional Himawari-9 tahun 2023 **TERSEDIA LENGKAP** di AWS (mencakup periode puncak karhutla El Niño September–Oktober 2023).
   - **Tahun 2026:** Data operasional near-real-time tersedia.
3. **Data Titik Panas NASA FIRMS:**
   - `VIIRS_SNPP_SP` (Suomi-NPP Standard Processing): Tersedia dari 20 Januari 2012 s.d. 30 Juni 2026.
   - `VIIRS_NOAA20_SP` (NOAA-20 Standard Processing): Tersedia dari 1 April 2018 s.d. 30 Juni 2026.
4. **Kapasitas Penyimpanan Lokal:**
   - Ruang kosong pada partisi `D:\` saat ini: **36,91 GB** (34,37 GiB).

---

## 2. Parameter Teknis Pengunduhan Kandidat

Bila hari-hari kandidat di bawah ini disetujui untuk diunduh pada fase mendatang:
- **Jendela Jam Siang Aman (UTC):** Sekitar pukul **02:00 s.d. 07:00 UTC** (09:00 s.d. 14:00 WIB), dengan sudut elevasi matahari tinggi yang optimal untuk kanal tampak (B01–B04).
- **Jeda Rutin JMA:** Jam **02:40 UTC** wajib dihindari karena merupakan jendela pemeliharaan internal satelit JMA (*housekeeping*) yang tidak menghasilkan citra (HTTP 404). Jam observasi yang disarankan: **03:00 UTC**, **04:00 UTC**, **05:00 UTC**, atau **06:00 UTC**. **[Usulan desain]**
- **Perkiraan Ukuran Unduhan per Adegan:**
  - Mengikuti pola 8 adegan pilot (total 4,19 GB untuk 8 adegan atau ~524 MB per adegan untuk Himawari-8 berkas FLDK penuh).
  - Untuk Himawari-9 (hanya segmen S05 dan S06): ~70 MB per adegan.
- **Batasan Operasional:** Tidak ada pengunduhan citra Himawari baru yang dijalankan pada tugas ini. **[Usulan desain]**

---

## 3. Tabel Kandidat Hari Asap Karhutla (15–20 Hari Pilihan)

Tabel di bawah mengurutkan hari-hari terpilih dari hasil rekapitulasi API NASA FIRMS (VIIRS S-NPP dan NOAA-20) pada kotak koordinat geografis resmi proyek Upwind (Kalimantan Tengah: `111.0°BT s.d. 116.0°BT, -3.5°LS s.d. 0.8°LU`; Riau: `100.0°BT s.d. 104.0°BT, -1.1°LS s.d. 2.5°LU`).

Kolom **Verifikasi Worldview (diisi pengguna)** dan **Label (diisi pengguna)** sengaja dibiarkan kosong agar diisi secara independen oleh pengguna setelah memeriksa citra NASA Worldview.

| No | Tanggal (YYYY-MM-DD) | Wilayah | Satelit | Jumlah Titik Panas VIIRS (S-NPP / NOAA-20) | Jenis Hari yang Diharapkan [Asumsi] | Karakteristik Kejadian & Hubungan Temporal | Rekomendasi Jam UTC Siang (Di luar 02:40) | Estimasi Ukuran Unduhan | Verifikasi Worldview (diisi pengguna) | Label (diisi pengguna) |
| :-: | :---: | :---: | :---: | :---: | :---: | :--- | :---: | :-: | :---: | :---: |
| 1 | **2015-10-14** | Kalteng | H8 | 11.558 / - | **Padat (Super Ekstrem)** [Asumsi] | Puncak bencana karhutla gambut El Niño 2015 terparah sepanjang sejarah. | 03:00 UTC | ~524 MB | | |
| 2 | **2015-09-24** | Kalteng | H8 | 2.641 / - | **Padat** [Asumsi] | Gelombang kebakaran September 2015 sebelum kabut asap tebal se-Asia Tenggara. | 03:00 UTC | ~524 MB | | |
| 3 | **2019-09-13** | Kalteng | H8 | 7.143 / - | **Padat (Puncak Ekstrem)** [Asumsi] | Puncak harian karhutla Kalteng 2019. *[Berurutan dengan pilot 12 & 14 Sep]*. | 03:00 UTC | ~524 MB | | |
| 4 | **2019-09-14** | Kalteng | H8 | 5.970 / 6.969 | **Padat (Puncak)** [Asumsi] | *Sudah di Pilot.* Puncak polusi PM2.5 Kalimantan (PMC11531407). | 03:00, 04:00, 06:00 UTC | ~1,57 GB | | |
| 5 | **2019-09-12** | Kalteng | H8 | 4.484 / - | **Padat** [Asumsi] | *Sudah di Pilot.* 1.188 hotspot BNPB Kalimantan. | 03:00 UTC | ~524 MB | | |
| 6 | **2019-09-24** | Kalteng | H8 | 3.159 / - | **Padat** [Asumsi] | Gelombang kedua kebakaran akhir September 2019 (terpisah 10 hari dari puncak). | 03:00 UTC | ~524 MB | | |
| 7 | **2019-09-05** | Kalteng | H8 | 3.145 / - | **Padat** [Asumsi] | *Sudah di Pilot.* Awal eskalasi kebakaran September Kalteng. | 03:00 UTC | ~524 MB | | |
| 8 | **2023-10-02** | Kalteng | H9 | 2.561 / - | **Padat** [Asumsi] | Puncak karhutla El Niño 2023 pada sensor Himawari-9 terkini. | 03:00 UTC | ~70 MB | | |
| 9 | **2023-09-29** | Kalteng | H9 | 1.386 / - | **Sedang-Padat** [Asumsi] | Fase kenaikan titik api Kalteng El Niño September 2023. | 03:00 UTC | ~70 MB | | |
| 10 | **2019-08-12** | Riau | H8 | 596 / 481 | **Padat** [Asumsi] | Puncak kebakaran Riau Tahap II Agustus 2019. | 03:00 UTC | ~524 MB | | |
| 11 | **2019-08-08** | Riau | H8 | 403 / - | **Padat** [Asumsi] | Awal lonjakan titik panas Riau (terpisah 4 hari dari 12 Ags). | 03:00 UTC | ~524 MB | | |
| 12 | **2019-08-13** | Kalteng | H8 | 728 / - | **Sedang-Padat** [Asumsi] | Peningkatan kebakaran Kalimantan sebelum fase darurat September. | 03:00 UTC | ~524 MB | | |
| 13 | **2019-08-14** | Kalteng | H8 | 259 / - | **Sedang** [Asumsi] | Titik panas sedang pertengahan Agustus Kalteng. *[Berurutan dengan 13 Ags]*. | 03:00 UTC | ~524 MB | | |
| 14 | **2019-08-10** | Riau | H8 | 148 / - | **Sedang** [Asumsi] | Periode transisi kebakaran lahan Riau Agustus 2019. | 03:00 UTC | ~524 MB | | |
| 15 | **2019-10-04** | Kalteng | H8 | 119 / - | **Sedang** [Asumsi] | Penurunan titik api awal Oktober sebelum musim hujan tiba. | 03:00 UTC | ~524 MB | | |
| 16 | **2019-10-15** | Kalteng & Riau | H8 | 175 (KT) / 75 (Riau) | **Sedikit (Kontrol Bersih)** [Asumsi] | *Sudah di Pilot.* Mulai hujan merata di Sumatra & Kalimantan (PMC11531407). | 03:00 UTC | ~524 MB | | |
| 17 | **2019-10-17** | Riau | H8 | 5 / - | **Sedikit (Kontrol Negatif)** [Asumsi] | Pasca hujan lebat Riau, titik api hampir padam sempurna. | 03:00 UTC | ~524 MB | | |
| 18 | **2019-10-18** | Kalteng | H8 | 32 / - | **Sedikit (Kontrol Negatif)** [Asumsi] | Pasca hujan lebat Kalteng, asap diperkirakan hilang. | 03:00 UTC | ~524 MB | | |
| 19 | **2019-01-15** | Kalteng & Riau | H8 | 0-3 / - | **Nol (Kontrol Awan Basah)** [Asumsi] | *Sudah di Pilot.* Puncak musim hujan monsun barat, awan tebal tanpa karhutla. | 03:00 UTC | ~524 MB | | |
| 20 | **2019-01-17** | Riau | H8 | 4 / - | **Nol (Kontrol Negatif)** [Asumsi] | Hari kontrol hujan lebat murni di Riau. | 03:00 UTC | ~524 MB | | |
| 21 | **2019-01-18** | Kalteng | H8 | 1 / - | **Nol (Kontrol Negatif)** [Asumsi] | Hari kontrol hujan lebat murni di Kalteng. | 03:00 UTC | ~524 MB | | |
| 22 | **2026-10-23** | Kalteng & Riau | H9 | 3.396 (KT) / 2 (Riau) | **Padat (KT) / Nol (Riau)** [Asumsi] | *Sudah di Pilot.* Kebakaran aktif terkini di Kalteng pada sensor H9. | 03:00 UTC | ~70 MB | | |

---

## 4. Analisis Pemilihan dan Rekomendasi Tahap Berikutnya

1. **Komposisi Distribusi Sampel:**
   - **Padat / Ekstrem (>1.000 titik panas):** 9 hari (termasuk rekor 2015, puncak 2019, dan El Niño 2023).
   - **Sedang (100–1.000 titik panas):** 6 hari (kebakaran skala menengah di Riau dan Kalteng).
   - **Sedikit / Kontrol Nol (<100 titik panas):** 7 hari (kondisi atmosfer bersih atau musim hujan lebat).
2. **Keterwakilan Multi-Kejadian dan Sensor:**
   - Mencakup 3 fenomena iklim besar: El Niño 2015 (H8), Kebakaran Nasional 2019 (H8), dan El Niño 2023 (H9).
   - Mengisi kekosongan wilayah Riau dengan menambahkan kandidat puncak Agustus 2019 (12 Agustus dan 8 Agustus).
3. **Pengendalian Hari Berurutan (*Autocorrelation Guard*):**
   - Sebagian besar kandidat dipisahkan jeda waktu 4 hingga 10 hari untuk menghindari pengambilan sampel dari kepulan asap tunggal yang sama.
   - Hari yang berurutan (misal 13 September 2019 di antara 12 dan 14 September) diberi tanda khusus `[Berurutan]` agar saat pembagian data latih/uji (*train/test split*) wajib dikelompokkan ke sisi yang sama demi mencegah kebocoran data (*data leakage*).
4. **Langkah yang Menunggu Pengguna:**
   - Pengguna membuka [NASA Worldview](https://worldview.earthdata.nasa.gov/) untuk tanggal-tanggal di atas.
   - Mengamati apakah kabut asap terlihat jelas pada produk *Corrected Reflectance (True Color)* VIIRS/MODIS.
   - Mengisi kolom **Verifikasi Worldview** dan **Label** pada tabel di atas sebelum keputusan pengunduhan citra satelit Himawari diambil.
