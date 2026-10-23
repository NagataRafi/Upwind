# ARSITEKTUR: Upwind

Upwind adalah nama aplikasi (pemantau asap karhutla dan titik panas hulu asap). Dokumen ini menjelaskan bagaimana bagian-bagian sistem tersusun dan apa yang mereka janjikan satu sama lain. Baca Tujuan.md lebih dulu. Dokumen ini tidak berisi kode.

Label klaim: **[Literatur]**, **[Asumsi]**, **[Usulan desain]**, sama seperti di Tujuan.md.

## 1. Prinsip arsitektur

1. **Web dibangun lebih dulu dengan data tiruan.** Web hanya membaca berkas dan layanan yang mengikuti kontrak data di bagian 3. Data asli kemudian menggantikan data tiruan tanpa mengubah web.
2. **Tiga lapisan terpisah.** Pengolahan citra, model AI, dan web tidak saling memanggil di luar kontrak. Web tidak menghitung segmentasi.
3. **Satu sumber kebenaran untuk waktu.** Semua waktu disimpan dalam UTC (ISO 8601) dan hanya diubah ke WIB atau WITA pada tampilan.
4. **Setiap keluaran membawa jejak asal.** Setiap berkas hasil mencatat citra masukan, versi model, versi kode, dan waktu pemrosesan.
5. **Stack dipilih agen** dalam batas di bagian 6; pilihan dicatat di Changelog.md beserta alasannya. **[Usulan desain]**

## 2. Komponen dan alur

```
Himawari-9 (AWS, 10 menit) ──┐
Titik panas (FIRMS/lainnya) ─┼─► [A] Pengambilan data ─► [B] Pengolahan citra ─► [C] Model segmentasi
Angin (reanalisis/prakiraan) ┘                                                      │
                                                                                    ▼
                                      [E] Penyimpanan hasil ◄── [D] Smoke-to-source (peringkat titik panas)
                                              │
                                              ▼
                                      [F] API/berkas statis ─► [G] Web dasbor (ponsel dan desktop)
```

| Kode | Komponen | Tugas | Lapisan |
| --- | --- | --- | --- |
| A | Pengambilan data | Mengambil citra Himawari, titik panas, dan angin pada jadwal tetap; mencatat kegagalan unduh | Pengolahan citra |
| B | Pengolahan citra | Kalibrasi, pemotongan wilayah, masking awan dan malam, tumpukan band dan frame, pasca-proses mask, luas | Pengolahan citra |
| C | Model segmentasi | Probabilitas asap per piksel dan peta ketidakpastian | Model AI |
| D | Smoke-to-source | Arah gerak asap, sektor hulu, kandidat titik panas, skor dan penjelasan | Pengolahan citra dan aturan heuristik; bukan model belajar pada versi awal |
| E | Penyimpanan hasil | Berkas hasil per waktu dan indeks | Pendukung |
| F | API atau berkas statis | Menyajikan hasil sesuai kontrak data | Pendukung |
| G | Web dasbor | Peta, panel, pencarian waktu, status data | Aplikasi web |

Mode data tiruan: komponen A sampai D digantikan satu generator data contoh yang menulis berkas sesuai kontrak. Mode data asli: komponen asli menulis berkas yang sama. Web tidak tahu bedanya selain lewat penanda `is_mock` (lihat bagian 3).

## 3. Kontrak data

Kontrak ini adalah batas antara web dan sisanya. Mengubahnya memerlukan entri di Changelog.md dan persetujuan pengguna. Nama lapangan di bawah adalah usulan awal; agen boleh menyempurnakan selama semua bidang yang tertulis tetap ada.

### 3.1 Bingkai asap (`SmokeFrame`), satu per waktu

| Bidang | Isi |
| --- | --- |
| `timestamp_utc` | Waktu pengambilan citra terbaru yang dipakai |
| `processed_utc` | Waktu hasil selesai dibuat |
| `region_id` | `riau` atau `kalteng` |
| `bbox` | Batas geografis (barat, selatan, timur, utara) |
| `mask_overlay` | Berkas gambar transparan (PNG) atau kotak peta untuk mask asap |
| `probability_overlay` | Probabilitas asap per piksel untuk tampilan |
| `uncertainty_overlay` | Ketidakpastian per piksel |
| `area_km2` | Luas asap dalam kilometer persegi |
| `motion` | Arah (derajat dari utara) dan kecepatan perkiraan gerak asap, serta kualitas perkiraan |
| `source_frames` | Daftar waktu frame yang dipakai |
| `daylight` | Benar bila citra tampak tersedia; salah pada malam hari |
| `cloud_cover_fraction` | Perkiraan tutupan awan pada wilayah |
| `model_version`, `code_version` | Jejak asal |
| `is_mock` | Benar bila data tiruan |

### 3.2 Titik panas (`Hotspot`)

| Bidang | Isi |
| --- | --- |
| `id` | Pengenal tetap |
| `time_utc`, `lat`, `lon` | Waktu dan posisi |
| `source` | Nama sumber (FIRMS VIIRS atau lainnya) |
| `confidence`, `frp` | Kepercayaan dan daya radiasi api bila tersedia dari sumber |
| `is_peat` | Apakah di atas lahan gambut, bila lapisan gambut tersedia |
| `is_mock` | Penanda data tiruan |

### 3.3 Angin (`WindSample`)

| Bidang | Isi |
| --- | --- |
| `time_utc`, `lat`, `lon` | Waktu dan posisi |
| `u`, `v` | Komponen angin (m/s) |
| `height_m` | Ketinggian pengukuran (misalnya 10 m) |
| `source`, `is_mock` | Sumber dan penanda tiruan |

### 3.4 Peringkat titik panas hulu asap (`RankedSource`)

| Bidang | Isi |
| --- | --- |
| `frame_timestamp_utc` | Bingkai asap yang dianalisis |
| `hotspot_id`, `rank`, `score` | Titik panas, peringkat, skor |
| `factors` | Rincian skor: jarak ke tepi hulu asap, selisih sudut arah, kepercayaan titik panas, dan sebagainya |
| `explanation` | Kalimat pendek dalam bahasa Indonesia yang bisa dibaca relawan |
| `method_version`, `is_mock` | Versi aturan dan penanda tiruan |

### 3.5 Status sistem (`SystemStatus`)

Waktu citra terakhir yang berhasil diproses, usia data dalam menit, status tiap sumber (berhasil, tertunda, gagal), dan penanda `night_no_smoke_update`.

## 4. Pemrosesan dan model (acuan untuk agen data dan ML)

- **Masukan citra:** potongan 256×256 piksel dari beberapa band Himawari (tampak, inframerah dekat, 3,9 µm, 10,8 µm) dan selisih band, dengan N frame berturut-turut (N antara 1 dan 6). Daftar band yang tersedia dan resolusinya harus **diverifikasi** dari dokumentasi produk sebelum desain tumpukan dikunci. **[Asumsi]** Produk JAXA memakai 2,3, 3,9, dan 10,8 µm. **[Literatur]**
- **Model:** U-Net kecil sebagai utama (satu frame dan multi-frame), SegFormer kecil sebagai pembanding, baseline aturan ambang dan Random Forest per piksel. Dibatasi 6 sampai 8 GB VRAM: potongan kecil, batch kecil, presisi campuran. **[Usulan desain]**
- **Label:** tidak ada dataset asap berlabel piksel dari Indonesia yang saya temukan. Strategi: anotasi poligon sendiri dengan citra VIIRS true color sebagai pembanding, pelatihan awal dari SmokeViz bila lisensi dan sensornya cocok, dan opsi pseudo-label. **[Asumsi]**
- **Pembagian data:** per hari atau per kejadian, bukan acak per potongan; satu kejadian dan satu provinsi disisihkan untuk uji lintas wilayah.
- **Smoke-to-source (D):** (1) dari bingkai asap berturut-turut hitung arah dan kecepatan gerak pusat asap; (2) tentukan sektor hulu dari arah gerak dan angin; (3) kumpulkan titik panas di dalam atau dekat tepi hulu dalam jarak tertentu; (4) beri skor dari jarak, kesesuaian sudut, dan kepercayaan titik panas; (5) hasilkan peringkat dengan penjelasan. Bobot skor adalah parameter yang dicatat dan diuji ablation. Pembanding wajib: titik panas terdekat dengan pusat asap, dan pemilihan acak. **[Usulan desain]**
- **Validasi retrospektif peringkat:** apakah titik panas peringkat atas kemudian terbukti terbakar, misalnya lewat area terbakar Sentinel-2 beberapa hari kemudian. Ini membuktikan sumber kebakaran, bukan sumber asap tertentu; pembatas ini harus dinyatakan di laporan. **[Asumsi]**

## 5. Struktur folder (nama saja)

```
/
  Tujuan.md  PRD.md  ARSITEKTUR.md  Agents.md  Changelog.md
  data/            (data mentah dan olahan; tidak masuk repositori bila besar)
  pipeline/        (komponen A, B, D)
  model/           (komponen C: pelatihan, evaluasi, bobot)
  mock/            (generator data tiruan sesuai kontrak)
  api/             (komponen F, bila diperlukan)
  web/             (komponen G)
  eval/            (skrip evaluasi dan hasil)
  docs/            (catatan, hasil wawancara, laporan)
```

## 6. Batasan teknis yang mengikat

- Web berjalan lokal di laptop untuk demo; tidak memerlukan akun atau penayangan publik. **[Usulan desain]**
- Web responsif: ringkas di ponsel, lengkap di desktop; antarmuka berbahasa Indonesia; hemat data (gambar hasil dikompres, tidak memuat data yang tidak terlihat).
- Komponen pengolahan citra dan model memakai Python; kerangka web dipilih agen. Pilihan dicatat di Changelog.md.
- Rahasia (kunci API, token) tidak masuk repositori; dibaca dari lingkungan atau berkas yang diabaikan git.
- Setiap sumber data eksternal punya pembungkus tunggal, sehingga bila akses berubah, hanya pembungkus itu yang diganti.

## 7. Hal yang belum diverifikasi

| Hal | Status | Cara memverifikasi |
| --- | --- | --- |
| Daftar band Himawari-9 di AWS dan format berkas | Halaman AWS tidak mencantumkan band dan format | Baca dokumentasi produk, buka satu berkas |
| Asap gambut terlihat jelas di citra Himawari | Belum diuji | Periksa beberapa kasus 2019 secara visual sebelum membangun model |
| Akses FIRMS titik panas | Belum dipastikan | Daftar dan uji unduhan; cadangan: produk titik panas Himawari JAXA |
| Komponen angin 10 m di ERA5-Land | Belum dikonfirmasi pada katalog | Periksa daftar band; cadangan: sumber angin lain, jangan dikarang |
| Lisensi dan sensor SmokeViz | Tidak tertulis di halaman poster | Baca makalah dan halaman data |
| Jaringan sensor kualitas udara saat ini | Halaman tahun 2015 sudah usang | Cari sumber terbaru bila dipakai |
| Peran produk BMKG dan SiPongi | Isi SiPongi belum dibaca | Tinjauan pustaka dan produk |

## 8. Sumber

- [Himawari di AWS Open Data](https://registry.opendata.aws/noaa-himawari/)
- [JAXA Himawari-8 Wild Fire product](https://www.eorc.jaxa.jp/ptree/documents/README_H08_L2WLF.txt)
- [SmokeViz, NeurIPS 2025](https://neurips.cc/virtual/2025/poster/121682)
- [SIT-FUSE](https://arxiv.org/pdf/2510.09845)
- [BMKG Satelit Cuaca](https://www.bmkg.go.id/satelit/)
- [Sentinel-5P NRTI aerosol index](https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S5P_NRTI_L3_AER_AI)