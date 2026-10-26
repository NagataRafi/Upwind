# Panduan Belajar Proyek Upwind (Pelajari.md)

Panduan ini disusun untuk mahasiswa D4 Jaringan Telekomunikasi Digital yang sedang mempelajari pengolahan citra satelit dan *deep learning* melalui proyek Upwind (*Pemantau Asap Karhutla dan Titik Panas Hulu Asap*). Dokumen ini menyajikan peta kode nyata, alur data fisis, konsep teoretis penting, status terkini proyek, dan urutan belajar bertahap.

Label klaim yang digunakan di seluruh dokumen:
- **[Literatur]**: bersumber dari makalah, dokumentasi teknis resmi, atau standar operasional yang dapat ditautkan.
- **[Asumsi]**: premis kerja yang masuk akal namun belum dibuktikan secara empiris dalam data proyek.
- **[Usulan desain]**: rancangan arsitektural dan spesifikasi rekayasa yang dipilih untuk sistem Upwind.

---

## 1. Peta Folder dan Berkas Penting

Semua lintasan (*path*) di bawah ini telah diverifikasi langsung terhadap sistem berkas pada repositori `C:\Users\ADMIN\upwind_proj` dan media penyimpanan eksternal terkait.

> [!WARNING]
> Folder Google Drive di `G:\My Drive\github\projects\Upwind` adalah **salinan cadangan lama**. Folder tersebut tidak boleh digunakan untuk kompilasi kode atau eksekusi *pipeline* karena perbedaan penanganan tautan simbolik (*symlink/junction*) pada Windows serta risiko konflik sinkronisasi. Seluruh pekerjaan resmi berada di partisi lokal `C:\Users\ADMIN\upwind_proj`.

### Tabel Struktur Folder Utama

| Jalur Direktori | Fungsi Utama (Satu Kalimat) | Status |
| :--- | :--- | :---: |
| `pipeline/` | Berisi seluruh skrip pengunduhan data satelit, pembacaan biner HSD, kalibrasi radiometrik, pembuatan dataset, dan perenderan visual adegan. | **ADA** |
| `eval/` | Berisi skrip pengujian integritas pemisahan data latih/uji dan pengujian verifikasi spesifikasi dataset P3a. | **ADA** |
| `model/` | Folder khusus arsitektur model AI, skrip pelatihan, skrip evaluasi metrik, dan penyimpanan bobot model (*weights*). | **KOSONG** |
| `api/` | Tempat penyajian layanan antarmuka pemrograman aplikasi (API backend) jika disajikan secara dinamis. | **KOSONG** |
| `web/` | Aplikasi antarmuka web dasbor interaktif berbasis React 18, Vite, TypeScript, Tailwind CSS, dan Leaflet. | **ADA** |
| `data_real/` | Berkas keluaran data asli (Himawari-9) berformat GeoJSON/JSON dan overlay PNG yang mematuhi kontrak data (`is_mock: false`). | **ADA** |
| `mock/` | Skrip generator data tiruan (`generate_mock_data.py`) untuk mensimulasikan dasbor web sebelum model AI dan data asli lengkap. | **ADA** |
| `docs/` | Dokumentasi arsitektur, kontrak data, protokol anotasi, ringkasan operasional, panduan belajar, serta komposit visual adegan. | **ADA** |
| `data/` | Data tiruan JSON, lapisan overlay PNG tiruan untuk dasbor, data geospasial garis pantai Natural Earth, dan titik tautan (*junction*). | **ADA** |
| `D:\upwind_data` *(di luar repo C:)* | Lokasi penyimpanan data besar di partisi D:, mencakup direktori berkas mentah satelit Himawari-8/9 dan berkas log unduhan. | **ADA** |
| `D:\upwind_data\dataset_p3a` *(di luar repo C:)* | Tempat penyimpanan 112 berkas patch `.npz` (15 kanal, 256×256 piksel) beserta berkas katalog indeks `dataset_index.json`. | **ADA** |

---

### Tabel Berkas Kunci dan Status Ketersediaannya

| Jalur Berkas | Fungsi Teknis | Status |
| :--- | :--- | :---: |
| [`pipeline/config.py`](file:///C:/Users/ADMIN/upwind_proj/pipeline/config.py) | Membaca konfigurasi `.env` dan menentukan variabel `DATA_ROOT` secara terpusat tanpa membocorkan kunci rahasia. | **ADA** |
| [`pipeline/hsd_header.py`](file:///C:/Users/ADMIN/upwind_proj/pipeline/hsd_header.py) | Mengurai struktur biner blok header Himawari Standard Data (HSD) sesuai panduan teknis resmi JMA. **[Literatur]** | **ADA** |
| [`pipeline/olah_himawari_fm1.py`](file:///C:/Users/ADMIN/upwind_proj/pipeline/olah_himawari_fm1.py) | Melakukan kalibrasi reflektansi optik, konversi suhu kecerahan (TB) radiasi termal Planck, dan transformasi koordinat piksel. | **ADA** |
| [`pipeline/kotak_fm1.py`](file:///C:/Users/ADMIN/upwind_proj/pipeline/kotak_fm1.py) | Memotong citra wilayah geografis Riau dan Kalimantan Tengah serta menambahkan kisi koordinat dan batas pantai 10 m. | **ADA** |
| [`pipeline/pembuat_dataset.py`](file:///C:/Users/ADMIN/upwind_proj/pipeline/pembuat_dataset.py) | Memproses data mentah menjadi tumpukan 15 kanal temporal grid 1 km dan memotongnya menjadi petak 256×256 (`.npz`). | **ADA** |
| [`pipeline/pipeline_h9.py`](file:///C:/Users/ADMIN/upwind_proj/pipeline/pipeline_h9.py) | Eksekusi otomatis Komponen A (unduh segmen AWS S3) dan Komponen B (pengolahan frame terkini Himawari-9). | **ADA** |
| [`pipeline/render_adegan.py`](file:///C:/Users/ADMIN/upwind_proj/pipeline/render_adegan.py) | Merender komposit RGB visual untuk 8 adegan pilot ke direktori `docs/adegan/` untuk verifikasi pengguna. | **ADA** |
| [`pipeline/siapkan_anotasi.py`](file:///C:/Users/ADMIN/upwind_proj/pipeline/siapkan_anotasi.py) | Menghasilkan GeoTIFF 4-band georeferensi dan template GeoJSON untuk keperluan digitasi poligon asap di QGIS. | **ADA** |
| [`pipeline/unduh_himawari_fm1.py`](file:///C:/Users/ADMIN/upwind_proj/pipeline/unduh_himawari_fm1.py) | Skrip pengunduh berkas uji kelayakan asap FM-1 dari repositori AWS Open Data. | **ADA** |
| [`pipeline/unduh_hotspot_firms.py`](file:///C:/Users/ADMIN/upwind_proj/pipeline/unduh_hotspot_firms.py) | Mengunduh data titik panas sensor VIIRS dari NASA FIRMS API dan memetakan ke skema kontrak data Upwind. | **ADA** |
| [`pipeline/unduh_pilot_8_adegan.py`](file:///C:/Users/ADMIN/upwind_proj/pipeline/unduh_pilot_8_adegan.py) | Mengunduh 135 berkas data Himawari-8 & Himawari-9 untuk 8 adegan pilot dengan multithreading dan resume unduhan. | **ADA** |
| `pipeline/smoke_to_source.py` | Modul estimasi vektor gerak asap, proyeksi kerucut hulu, dan perangkingan titik panas pemicu asap (FR-S). | **BELUM ADA** |
| [`eval/test_split_integrity.py`](file:///C:/Users/ADMIN/upwind_proj/eval/test_split_integrity.py) | Menguji aturan bahwa pembagian set latih dan set uji wajib dipisah per hari kalender untuk mencegah kebocoran data. | **ADA** |
| [`eval/uji_dataset_p3a.py`](file:///C:/Users/ADMIN/upwind_proj/eval/uji_dataset_p3a.py) | Memvalidasi kesetaraan dimensi tumpukan fitur (15, 256, 256), tipe data float32, dan statistik awan pada dataset P3a. | **ADA** |
| `model/baseline_threshold.py` | Model acuan dasar (B1) berbasis aturan ambang logika spektral per piksel. | **BELUM ADA** |
| `model/baseline_rf.py` | Model acuan dasar (B2) Random Forest per piksel menggunakan nilai 15 kanal fitur. | **BELUM ADA** |
| `model/unet_single.py` | Model segmentasi deep learning U-Net satu bingkai waktu ($t_0$). | **BELUM ADA** |
| `model/unet_multi.py` | Model segmentasi deep learning U-Net multi-bingkai temporal (15 kanal masukan $t_0, t-10, t-30, t-40$). | **BELUM ADA** |
| `model/segformer.py` | Model segmentasi Vision Transformer kecil sebagai pembanding terhadap U-Net. | **BELUM ADA** |
| [`mock/generate_mock_data.py`](file:///C:/Users/ADMIN/upwind_proj/mock/generate_mock_data.py) | Generator data simulasi JSON dan PNG mask sesuai spesifikasi kontrak data untuk skenario normal, stale, dan malam. | **ADA** |
| [`docs/KONTRAK_DATA.md`](file:///C:/Users/ADMIN/upwind_proj/docs/KONTRAK_DATA.md) | Spesifikasi formal kontrak data antarmuka antara lapisan pengolahan/model dengan lapisan web. | **ADA** |
| [`docs/PROTOKOL_ANOTASI.md`](file:///C:/Users/ADMIN/upwind_proj/docs/PROTOKOL_ANOTASI.md) | Panduan standar operasional anotasi poligon asap di QGIS dan aturan kesepakatan dua penganotasi. | **ADA** |

---

## 2. Alur Data dari Awal sampai Akhir

Alur pemrosesan data Upwind dirancang mengikuti prinsip modularitas: lapisan pengolahan data mentah menghasilkan tumpukan matriks numerik, lapisan model memprediksi probabilitas biner, lapisan heuristik melacak hulu, dan lapisan web menyajikan hasil ke pengguna akhir. **[Usulan desain]**

```
[1. Satelit Himawari-8/9 (AWS S3)]
               │
               ▼  (pipeline/unduh_pilot_8_adegan.py / pipeline_h9.py)
[2. Berkas Mentah HSD (.DAT.bz2)]
               │
               ▼  (pipeline/hsd_header.py & pipeline/olah_himawari_fm1.py)
[3. Dekode Radiansi, Albedo (B01-B04), dan TB Kelvin (B07, B13)]
               │
               ▼  (pipeline/pembuat_dataset.py)
[4. Penyetaraan ke Grid Bersama 1 km (Bilinear & Area-Averaging)]
               │
               ▼  (pipeline/pembuat_dataset.py)
[5. Tumpukan Temporal 15 Kanal + Topeng Awan Dingin (TB13 < 265 K)]
               │
               ▼  (D:\upwind_data\dataset_p3a\*.npz)
[6. Pemotongan Patch Spasial 256×256 Piksel]
               │
               ├──────────────────────────────────────────┐
               ▼ (Fase P3 - BELUM ADA)                    │
[7. Prediksi Model AI (U-Net / Baseline)]                 │ (pipeline/render_adegan.py)
               │ (Menghasilkan mask_prob & unc)           ▼
               ▼ (Fase P4 - BELUM ADA)          [Verifikasi Visual Ahli /
[8. Heuristik Smoke-to-Source + Angin + FIRMS]    NASA Worldview (docs/adegan/)]
               │ (Menghasilkan ranked_sources)            ▲
               ▼                                          │
[9. Ekspor JSON & PNG Sesuai Kontrak Data (data_real/)] ──┘
               │
               ▼
[10. Antarmuka Web Dasbor Interaktif (web/)]
```

### Tahapan Teknis Pemrosesan:
1. **Pengunduhan Data Mentah (Komponen A)**:
   - Data mentah diunduh dari *bucket* publik AWS S3 `noaa-himawari8` (arsip 2019) dan `noaa-himawari9` (operasional 2026). Formatnya adalah biner terkompresi *Himawari Standard Data* (`.DAT.bz2`).
   - Kode pelaksana: [`pipeline/unduh_pilot_8_adegan.py`](file:///C:/Users/ADMIN/upwind_proj/pipeline/unduh_pilot_8_adegan.py) untuk data latih pilot dan [`pipeline/pipeline_h9.py`](file:///C:/Users/ADMIN/upwind_proj/pipeline/pipeline_h9.py) untuk data operasional terkini.
2. **Kalibrasi Radiometrik Fisis**:
   - Nilai hitungan digital (*digital count*) pada berkas HSD diubah menjadi besaran fisis:
     - Kanal optik tampak/inframerah dekat (B01, B02, B03, B04) dikalibrasi menjadi **Reflektansi Puncak Atmosfer (Albedo)**.
     - Kanal inframerah termal (B07 3,9 µm dan B13 10,4 µm) dikalibrasi radiansi lalu dikonversi menjadi **Brightness Temperature (TB)** dalam satuan Kelvin menggunakan inversi persamaan radiasi Planck.
   - Kode pelaksana: [`pipeline/hsd_header.py`](file:///C:/Users/ADMIN/upwind_proj/pipeline/hsd_header.py) dan [`pipeline/olah_himawari_fm1.py`](file:///C:/Users/ADMIN/upwind_proj/pipeline/olah_himawari_fm1.py).
3. **Penyetaraan Geometri ke Grid Bersama 1 km**:
   - Resolusi asli instrumen AHI (*Advanced Himawari Imager*) berbeda-beda per kanal: B03 H9 beresolusi 0,5 km, B01/B02/B04 beresolusi 1 km, dan B07/B13 beresolusi 2 km pada titik sub-satelit. **[Literatur]**
   - Agar dapat disusun menjadi satu larik tensor, seluruh kanal disetarakan ke grid seragam 0,01 derajat (~1 km):
     - Kanal resolusi kasar 2 km diinterpolasi menggunakan metode **Bilinear**.
     - Kanal resolusi tajam 0,5 km (B03 H9) diperkecil skalanya menggunakan metode **Area-Averaging** (agregasi kotak rata-rata) guna menjaga integritas energi pantulan dan mencegah distorsi aliasing. **[Usulan desain]**
   - Kode pelaksana: [`pipeline/pembuat_dataset.py`](file:///C:/Users/ADMIN/upwind_proj/pipeline/pembuat_dataset.py).
4. **Penyusunan Tumpukan 15 Kanal Fitur Temporal**:
   - Asap kebakaran hutan memiliki sifat dinamis (bergerak dan memudar seiring waktu), berbeda dengan daratan yang statis atau awan konvektif yang bergerak cepat. Oleh karena itu, model dirancang menerima informasi multi-temporal dari 4 cuplikan waktu: **[Usulan desain]**
     - $t_0$ (waktu observasi utama, 6 kanal): B01 (Biru 0,47 µm), B02 (Hijau 0,51 µm), B03 (Merah 0,64 µm), B04 (NIR 0,86 µm), B07 (SWIR 3,9 µm / TB), B13 (TIR 10,4 µm / TB).
     - $t-10$ menit (3 kanal): B03, B04, B13.
     - $t-30$ menit (3 kanal): B03, B04, B13.
     - $t-40$ menit (3 kanal): B03, B04, B13.
     *(Catatan: slot $t-20$ sengaja tidak digunakan karena slot waktu tersebut merupakan jendela kalibrasi rutin/housekeeping internal satelit JMA yang sering kosong).*
   - Total dimensi masukan: $(15, H, W)$.
5. **Pembuatan Topeng Awan Dingin (Cold Cloud Mask)**:
   - Dibuat dari kanal termal B13 pada waktu $t_0$: semua piksel dengan $TB_{13} < 265\text{ K}$ ditandai sebagai awan es/awan tebal tinggi bertemperatur sangat dingin.
   - Topeng ini bertindak sebagai filter biner keras: piksel awan dingin otomatis dieksklusi dari pendeteksian asap.
6. **Pemotongan Ukuran Standar 256×256**:
   - Wilayah studi Kalimantan Tengah (grid 460×640) dipotong menjadi 6 petak *patch* 256×256.
   - Wilayah Riau (grid 500×900) dipotong menjadi 8 petak *patch* 256×256.
   - Menghasilkan 14 petak per adegan (total 112 petak untuk 8 adegan pilot), disimpan dalam format `.npz` float32 pada `D:\upwind_data\dataset_p3a`.
7. **Rencana Inferensi Model AI (Fase P3 - BELUM ADA)**:
   - File patch diproses oleh model segmentasi AI untuk menghasilkan peta probabilitas keberadaan asap $[0.0, 1.0]$ dan peta estimasi ketidakpastian (*uncertainty*).
8. **Rencana Algoritma Smoke-to-Source (Fase P4 - BELUM ADA)**:
   - Menghitung vektor kecepatan dan arah gerak asap dari selisih posisi massa asap antara bingkai waktu, memadukan arah angin 10 m, memproyeksikan kerucut sektor hulu, dan mencocokkannya dengan titik panas VIIRS dari NASA FIRMS.
9. **Penyajian Dasbor Web (Fase P1/P5)**:
   - Hasil disimpan ke berkas JSON dan PNG transparan di folder `data_real/` sesuai [`docs/KONTRAK_DATA.md`](file:///C:/Users/ADMIN/upwind_proj/docs/KONTRAK_DATA.md).
   - Antarmuka web ([`web/`](file:///C:/Users/ADMIN/upwind_proj/web/)) membaca berkas statis tersebut dan menyajikannya secara interaktif di peramban pengguna.

---

## 3. Model dan Algoritma yang Direncanakan

> [!IMPORTANT]
> **Status Verifikasi Lapangan:** Saat ini **belum ada model yang dilatih** pada dataset proyek Upwind. Seluruh model di bawah ini berstatus **rencana pengembangan** dan **belum ada bukti empiris mengenai model mana yang memiliki performa terbaik**. Klaim perbandingan performa baru dapat dibuat setelah baseline dan model selesai dilatih pada data yang sama dengan seed yang tercatat.

### 1. Baseline 1: Aturan Ambang Spektral (*Thresholding Rule*) - B1
- **Penjelasan Sederhana:** Klasifikasi berbasis sekumpulan aturan logika matematika kondisi "jika-maka" sederhana per piksel. Misalnya: suatu piksel diklasifikasikan sebagai asap jika nilai reflektansi kanal merah (B03) melebihi batas tertentu, selisih reflektansi merah dan biru positif, dan suhu inframerah termalnya ($TB_{13}$) hangat/mendekati suhu daratan tropis.
- **Mengapa Dipilih:** Sebagai acuan performa paling dasar (*dummy/rule-based baseline*). Tidak memerlukan pelatihan data, deterministik, dan komputasinya instan. **[Usulan desain]**
- **Pertanyaan Penelitian yang Dijawab:** Seberapa akurat deteksi asap dapat dilakukan hanya dengan batasan fisika spektral tanpa bantuan algoritma pembelajaran mesin?
- **Kelemahan dan Risiko:** Sangat rentan menghasilkan alarm palsu (*false positive*) pada permukaan tanah terbuka yang terang, pasir pantai, atau lapisan awan rendah yang hangat.
- **Lokasi Kode:** Direncanakan di `model/baseline_threshold.py` (**BELUM ADA**).

### 2. Baseline 2: Random Forest per Piksel - B2
- **Penjelasan Sederhana:** Algoritma *machine learning* klasik berbasis ansambel puluhan pohon keputusan (*decision trees*). Model memeriksa nilai 15 kanal fitur pada satu titik piksel secara mandiri tanpa melihat piksel tetangganya, lalu pohon-pohon melakukan pemungutan suara (*voting*) apakah piksel tersebut asap atau bukan.
- **Mengapa Dipilih:** Sebagai acuan perbandingan pembelajaran mesin standar non-deep learning. Mampu memodelkan interaksi non-linear yang kompleks antar-kanal spektral. **[Usulan desain]**
- **Pertanyaan Penelitian yang Dijawab:** Berapa peningkatan akurasi yang diperoleh jika kita beralih dari aturan logika manual (B1) ke pemodelan statistik data per piksel (B2), sebelum beralih ke model konvolusi spasial?
- **Kelemahan dan Risiko:** Mengabaikan informasi bentuk dan pola spasial (buta konteks sekitar); ukuran memori model dan waktu inferensi per piksel dapat menjadi lambat jika memproses jutaan piksel citra satelit secara individual.
- **Lokasi Kode:** Direncanakan di `model/baseline_rf.py` (**BELUM ADA**).

### 3. Model Utama 1: U-Net Satu Bingkai (*Single-frame U-Net*) - M1
- **Penjelasan Sederhana:** Jaringan saraf tiruan konvolusional (CNN) berbentuk huruf 'U'. Bagian kiri (*encoder*) memperkecil resolusi spasial untuk memahami konteks objek secara global, sedangkan bagian kanan (*decoder*) mengembalikan resolusi piksel ke ukuran asli dengan bantuan sambungan pintas (*skip connections*) agar batas tepi asap tetap tajam. Model ini hanya melihat 6 kanal pada satu waktu $t_0$. **[Literatur]**
- **Mengapa Dipilih:** Standar arsitektur segmentasi semantik citra biomedis dan penginderaan jauh yang sudah teruji keandalannya. Mampu mengenali tekstur gumpalan dan batas asap.
- **Pertanyaan Penelitian yang Dijawab:** Apakah pengenalan pola spasial 2D mampu secara signifikan menurunkan *false positive* pada tanah terbuka jika dibandingkan dengan klasifikasi per piksel (B1 & B2)?
- **Kelemahan dan Risiko:** Karena hanya melihat satu waktu statis, model dapat terkecoh oleh kabut alami (*haze*), awan tipis stratus, atau asap pabrik lokal yang bentuk teksturnya menyerupai asap karhutla.
- **Lokasi Kode:** Direncanakan di `model/unet_single.py` (**BELUM ADA**).

### 4. Model Utama 2: U-Net Multi-Bingkai (*Multi-frame Temporal U-Net*) - M2
- **Penjelasan Sederhana:** Arsitektur U-Net yang diperluas untuk menerima masukan tumpukan 15 kanal dari empat cuplikan waktu ($t_0, t-10, t-30, t-40$). Lapisan konvolusi awal secara bersamaan mempelajari korelasi spektral spasial dan dinamika temporal dari pergerakan asap. **[Usulan desain]**
- **Mengapa Dipilih:** Karhutla tropis menghasilkan kepulan asap yang bergerak mengikuti arah angin dan meluas secara bertahap. Informasi deret waktu 10-menitan dari Himawari adalah pembeda fisis paling kuat antara asap kebakaran dan objek statis di bumi.
- **Pertanyaan Penelitian yang Dijawab:** Seberapa besar peningkatan metrik IoU dan ketahanan terhadap gangguan awan jika dimensi riwayat waktu ($t-10, t-30, t-40$) diintegrasikan langsung ke dalam konvolusi dibandingkan model satu bingkai ($t_0$)?
- **Kelemahan dan Risiko:** Membutuhkan memori VRAM lebih tinggi; rentan gagal beroperasi (*pipeline failure*) jika salah satu berkas citra historis pada server satelit mengalami kekosongan (*missing frames*).
- **Lokasi Kode:** Direncanakan di `model/unet_multi.py` (**BELUM ADA**).

### 5. Model Pembanding: SegFormer Kecil - M3
- **Penjelasan Sederhana:** Arsitektur segmentasi mutakhir yang menggabungkan konsep *Vision Transformer* (ViT) bertingkat dengan decoder multilayer perceptron (MLP) ringan. Menggunakan mekanisme *self-attention* untuk membandingkan hubungan setiap bagian citra terhadap seluruh area citra lainnya tanpa dibatasi oleh ukuran kernel konvolusi. **[Literatur]**
- **Mengapa Dipilih:** Untuk membandingkan paradigma konvolusi CNN (U-Net) dengan paradigma *attention* Transformer pada data penginderaan jauh berskala luas.
- **Pertanyaan Penelitian yang Dijawab:** Apakah mekanisme atensi global Transformer memberikan hasil segmentasi sebaran asap tipis yang lebih baik dibandingkan konvolusi lokal CNN?
- **Kelemahan dan Risiko:** Memerlukan data pelatihan yang lebih banyak agar generalisasinya baik; beban komputasi kuadratik pada mekanisme atensi dapat melampaui batas anggaran VRAM laptop 6-8 GB bila ukuran patch terlalu besar.
- **Lokasi Kode:** Direncanakan di `model/segformer.py` (**BELUM ADA**).

### 6. Heuristik Smoke-to-Source (Komponen D)
- **Penjelasan Sederhana:** Algoritma berbasis aturan fisis dan geometri vektor (bukan deep learning). Algoritma menghitung arah pergerakan gumpalan asap dari frame berturut-turut, memadukannya dengan vektor angin 10 meter untuk membentuk corong proyeksi arah hulu (*upwind sector*), lalu memeringkat titik panas (hotspot FIRMS) berdasarkan jarak, deviasi sudut, dan daya radiasi api (*fire radiative power* / FRP). **[Usulan desain]**
- **Mengapa Dipilih:** Memberikan informasi yang langsung dapat ditindaklanjuti oleh relawan dan satgas pemadam karhutla untuk menemukan asal mula api di hulu asap, bukan sekadar melihat polusi asap di hilir.
- **Pertanyaan Penelitian yang Dijawab:** Apakah perangkingan berbasis vektor hulu mampu mengungguli metode sederhana seperti memilih titik panas yang paling dekat dengan pusat massa asap (*nearest distance*) atau pemilihan acak?
- **Kelemahan dan Risiko:** Sangat bergantung pada kualitas data kecepatan angin dan keakuratan segmentasi tepi batas asap; bersifat heuristik empiris yang bobot parameternya harus diuji secara terpisah (*ablation study*).
- **Lokasi Kode:** Direncanakan di `pipeline/smoke_to_source.py` (**BELUM ADA**).

---

## 4. Istilah Penting untuk Pemula Telekomunikasi

1. **Reflektansi (Albedo):**
   Rasio perbandingan antara intensitas radiasi matahari yang dipantulkan oleh permukaan bumi kembali ke sensor satelit terhadap total radiasi matahari yang datang. Nilainya dinormalisasi antara 0,0 (menyerap seluruh cahaya / gelap sempurna) hingga 1,0 (memantulkan seluruh cahaya / putih cemerlang). Pada kanal optik (B01-B04), asap karhutla memiliki reflektansi sedang, sedangkan awan tebal memiliki reflektansi sangat tinggi. **[Literatur]**
2. **Brightness Temperature (Suhu Kecerahan - TB):**
   Temperatur ekuivalen suatu benda hitam sempurna (*blackbody*) dalam satuan Kelvin ($K$) yang akan memancarkan jumlah radiasi termal yang sama pada panjang gelombang tertentu, dihitung menggunakan pembalikan persamaan Planck:
   $$T_B = \frac{h \cdot c}{k \cdot \lambda \cdot \ln\left(\frac{2 \cdot h \cdot c^2}{\lambda^5 \cdot L_\lambda} + 1\right)}$$
   Di mana $L_\lambda$ adalah radiansi spektral yang diukur satelit. Kanal B13 (10,4 µm) mengukur suhu puncak awan atau permukaan bumi. **[Literatur]**
3. **Topeng Awan Dingin ($TB_{13} < 265\text{ K}$):**
   Aturan penyaringan fisis yang menetapkan bahwa setiap piksel dengan suhu kecerahan inframerah termal kanal 13 di bawah $265\text{ K}$ (sekitar $-8,15^\circ\text{C}$) dipastikan merupakan awan konvektif tinggi atau lapisan es puncak troposfer, bukan asap gambut dekat permukaan tanah tropis yang bersuhu hangat ($>275\text{ K}$). **[Usulan desain]**
4. **Resampling Bilinear vs Area-Averaging:**
   - *Bilinear Interpolation:* Mengestimasi nilai piksel baru berdasarkan interpolasi rata-rata terbobot jarak dari 4 piksel tetangga terdekat. Sangat cocok untuk memperhalus atau memperbesar citra dari resolusi kasar (2 km) ke resolusi target (1 km).
   - *Area-Averaging (Box Aggregation):* Menghitung nilai piksel baru berdasarkan rata-rata murni seluruh piksel asal yang berada di dalam luasan kotak target. Wajib digunakan saat memperkecil (*downsampling*) pita resolusi tajam (misal B03 0,5 km ke 1 km) agar energi pantulan radiometrik tetap lestari tanpa menghasilkan artefak interferensi (*aliasing*). **[Literatur]**
5. **Intersection over Union (IoU) / Jaccard Index:**
   Metrik evaluasi standar untuk segmentasi citra yang mengukur rasio antara luas area perpotongan (*irisan*) prediksi dan label asli terhadap luas area gabungan (*union*) keduanya:
   $$\text{IoU} = \frac{|A \cap B|}{|A \cup B|} = \frac{\text{TP}}{\text{TP} + \text{FP} + \text{FN}}$$
6. **Presisi (Precision), Recall, dan F1-Score:**
   - *Presisi (Precision):* Dari seluruh piksel yang diprediksi model sebagai asap, berapa persen yang benar-benar asap asli? $\text{Presisi} = \frac{\text{TP}}{\text{TP} + \text{FP}}$.
   - *Recall (Sensitivitas):* Dari seluruh piksel asap asli yang ada di lapangan, berapa persen yang berhasil ditemukan oleh model? $\text{Recall} = \frac{\text{TP}}{\text{TP} + \text{FN}}$.
   - *F1-Score (Dice Coefficient):* Nilai rata-rata harmonik antara Presisi dan Recall: $\text{F1} = 2 \cdot \frac{\text{Presisi} \cdot \text{Recall}}{\text{Presisi} + \text{Recall}}$.
7. **Pembagian per Hari (Split by Day) dan Bahaya Kebocoran Data (*Data Leakage*):**
   Aturan bahwa seluruh potongan adegan yang diambil pada **tanggal kalender yang sama** wajib diletakkan pada kelompok yang sama (semua masuk set latih ATAU semua masuk set uji). Bila potongan pada jam 03:00 UTC dimasukkan ke set latih dan potongan pada jam 04:00 UTC pada hari yang sama dimasukkan ke set uji, model akan "menyontek" pola cuaca, awan, dan bentuk gumpalan asap yang hampir identik. Ini disebut kebocoran data (*data leakage*), yang menyebabkan metrik evaluasi tampak tinggi di atas kertas namun gagal total saat diuji pada hari baru di dunia nyata. **[Literatur]**
8. **Seed (Bilangan Pengacak Awal) dan Reproduksibilitas:**
   Nilai angka awal yang diberikan kepada pembangkit bilangan acak komputer (*pseudo-random number generator*) saat menginisialisasi bobot jaringan saraf tiruan atau mengocok urutan data. Dengan menetapkan nilai *seed* yang sama (misal *seed* 42), seluruh hasil eksperimen, bobot, dan kurva pelatihan dapat diulang (*reproduced*) secara identik oleh peneliti lain. Standar proyek Upwind mewajibkan pelaporan hasil sebagai rata-rata dan simpangan baku dari minimal tiga seed berbeda (misal seed 42, 43, 44). **[Usulan desain]**

---

## 5. Status Pekerjaan Proyek

### (a) Tabel Pekerjaan yang SUDAH DIBUAT

Disusun dari riwayat resmi `Changelog.md` dan `git log` pada repositori `origin/main`:

| Fase | Ringkasan Hasil Pekerjaan | Berkas yang Terlibat | Hash Commit |
| :---: | :--- | :--- | :---: |
| **Pra-P0** | Perubahan arah proyek mengikuti arahan dosen pembimbing menjadi segmentasi asap Himawari dan peringatan hulu asap. | `Tujuan.md` | Inisial |
| **P0** | Perumusan dokumen fondasi, spesifikasi kebutuhan PRD, dokumen arsitektur 3-lapisan, dan kontrak data awal. | `PRD.md`, `Arsitektur.md`, `Agents.md`, `docs/KONTRAK_DATA.md` | Inisial / `84aa0b9` |
| **P1** | Pembangunan antarmuka web dasbor interaktif (React + Leaflet), generator data tiruan, penanganan skenario data basi/malam, dan uji responsif ponsel/desktop. | `web/src/*`, `mock/generate_mock_data.py`, `docs/tangkapan/*` | `04bd5fc`, `9e09f79` |
| **P2** | Audit data satelit Himawari AWS, verifikasi struktur biner HSD, perbaikan rumus radiometrik TB Kelvin, dan renderer adegan kotak Kalteng & Riau dengan batas pantai 10 m. | `pipeline/hsd_header.py`, `pipeline/olah_himawari_fm1.py`, `pipeline/kotak_fm1.py` | `11c268e`, `9e3fac8`, `13191df` |
| **P2** | Penyelesaian uji kelayakan asap FM-1 (skor kelayakan visual 8/10 oleh pengguna); verifikasi ketersediaan data FIRMS dan atribusi Open-Meteo; penyusunan protokol anotasi QGIS. | `docs/PROTOKOL_ANOTASI.md`, `pipeline/pipeline_h9.py`, `pipeline/siapkan_anotasi.py`, `data_real/*` | `0986f42`, `a3063c4` |
| **P2** | Audit skrip unduhan pilot, penyesuaian jadwal housekeeping JMA, verifikasi 3.396 titik panas Kalteng pada FIRMS, dan perumusan grid bersama 1 km. | `pipeline/unduh_pilot_8_adegan.py`, `pipeline/unduh_hotspot_firms.py` | `0e7dee8`, `1aa6ca6` |
| **P2** | Pengunduhan lengkap 135 berkas data Himawari untuk 8 adegan pilot (4,19 GB) dengan kecocokan ukuran 100%; perenderan 16 komposit RGB visual adegan ke `docs/adegan/`. | `pipeline/render_adegan.py`, `docs/adegan/*.png` | `f18e34c` |
| **P3a** | Pembuat dataset tanpa label: 112 potongan 256×256 (15 kanal) tersimpan di `D:\upwind_data\dataset_p3a`; bentuk tumpukan (15, 256, 256) terverifikasi identik antara H8 dan H9; uji integritas pemisahan data per hari lolos. | `pipeline/pembuat_dataset.py`, `eval/test_split_integrity.py`, `eval/uji_dataset_p3a.py` | `264c250` |

---

### (b) Tabel Pekerjaan yang AKAN DIBUAT dan Prasyarat

> [!CAUTION]
> **Peringatan Ilmiah Batasan Data:** Saat ini pembagian latih/uji (*train/test split*) **belum dikunci**, dan dataset pilot **hanya memiliki empat hari kejadian asap** (5, 12, 14 September 2019, dan 23 Oktober 2026). Jumlah ini sangat terbatas dan **belum mencukupi untuk mendukung klaim kesimpulan performa akhir model**. Diperlukan penambahan hari asap dan penyelesaian anotasi sebelum klaim ilmiah dapat dipublikasikan. **[Asumsi]**

| Rencana Fase | Tugas Teknis yang Akan Dibuat | Prasyarat yang Menunggu Pengguna | Pihak yang Bertindak |
| :---: | :--- | :--- | :---: |
| **P2/P3** | Verifikasi visual adegan komposit terhadap data pembanding eksternal. | **Menunggu Pengguna:** Membuka NASA Worldview dan membandingkan 16 gambar di `docs/adegan/` untuk tanggal 5, 12, 14 Sep 2019, 15 Okt 2019, 15 Jan 2019, dan 23 Okt 2026. | Pengguna |
| **P3b** | Instalasi perangkat lunak GIS dan pelaksanaan anotasi ground-truth. | **Menunggu Pengguna:** Menginstal QGIS pada komputer lokal dan melakukan anotasi percobaan poligon asap bersama 1 rekan penganotasi (2 orang) pada 3 adegan uji untuk mengukur kesepakatan IoU $\ge 0.70$. | Pengguna (dibantu panduan `docs/PROTOKOL_ANOTASI.md`) |
| **P3b** | Pengayaan variasi kejadian asap karhutla pada dataset. | **Menunggu Pengguna:** Menentukan hari-hari kejadian asap tambahan dari catatan historis karhutla (misal puncak karhutla Oktober 2015 atau Agustus 2019) untuk memperbanyak sampel data latih. | Pengguna & Agen Data |
| **P3** | Persetujuan formal fase P3 untuk memulai tahap pemodelan. | **Menunggu Pengguna:** Memberikan persetujuan tertulis (*sign-off*) untuk melangkah ke pelatihan model AI setelah anotasi awal siap. | Pengguna |
| **P3c** | Pembuatan dan evaluasi model acuan dasar B1 dan B2. | Tersedianya label biner hasil konversi GeoJSON anotasi QGIS. | Agen Model |
| **P3d** | Pembangunan dan pelatihan arsitektur U-Net satu frame dan multi-frame (15 kanal) dengan 3 seed. | Model acuan dasar B1 dan B2 telah memiliki metrik angka evaluasi resmi. | Agen Model |
| **P4** | Implementasi algoritma Smoke-to-Source dan evaluasi perbandingan terhadap *nearest distance*. | Model segmentasi asap menghasilkan keluaran mask probabilitas yang stabil. | Agen Smoke-to-Source |
| **P5** | Integrasi end-to-end pipa data asli ke dasbor web dan pengukuran latensi pemrosesan. | Model AI dan skrip smoke-to-source selesai diuji. | Agen Web & Agen Data |

---

## 6. Urutan Belajar yang Disarankan untuk Mahasiswa D3

Agar proses belajar terstruktur dan tidak membingungkan, pelajari berkas proyek sesuai urutan logis berikut. Setiap tahapan dilengkapi dengan fokus pencarian dan tiga pertanyaan latihan mandiri:

### Langkah 1: Memahami Masalah, Batasan, dan Kebutuhan Sistem
- **Berkas yang dibaca:** [`Tujuan.md`](file:///C:/Users/ADMIN/upwind_proj/Tujuan.md) dan [`PRD.md`](file:///C:/Users/ADMIN/upwind_proj/PRD.md).
- **Apa yang dicari di dalamnya:**
  - Mengapa proyek ini fokus pada asap karhutla dan arah hulu (*smoke-to-source*), bukan prediksi pergerakan api?
  - Siapa pengguna utama sistem (relawan dan tim satgas darat) dan bagaimana batas komputasi perangkat laptop (6–8 GB VRAM)?
  - Apa saja kriteria penerimaan FR-M (kebutuhan model AI) dan FR-S (kebutuhan pelacakan hulu asap)?
- **3 Pertanyaan Latihan:**
  1. Mengapa proyek Upwind membatasi pelaporan hasil evaluasi model sebagai rata-rata dan simpangan baku dari minimal tiga *seed* pengacakan?
  2. Apa alasan utama di balik aturan bahwa produk sebaran asap BMKG dilarang digunakan langsung sebagai label pelatihan model Upwind?
  3. Mengapa kebutuhan latensi sistem (NFR1) menetapkan batas maksimal 60 menit dari saat satelit memotret bumi hingga hasil tampil di dasbor?

### Langkah 2: Memahami Pemisahan Lapisan dan Batas Kontrak Data
- **Berkas yang dibaca:** [`Arsitektur.md`](file:///C:/Users/ADMIN/upwind_proj/Arsitektur.md) dan [`docs/KONTRAK_DATA.md`](file:///C:/Users/ADMIN/upwind_proj/docs/KONTRAK_DATA.md).
- **Apa yang dicari di dalamnya:**
  - Konsep arsitektur 3-lapisan (Pengolahan Citra, Model AI, dan Web Dasbor).
  - Mengapa antarmuka web dilarang menghitung segmentasi dan model AI dilarang mengunduh data mentah secara langsung (*separation of concerns*)?
  - Struktur data JSON untuk `SmokeFrame`, `Hotspot`, `WindSample`, `RankedSource`, dan `SystemStatus`.
- **3 Pertanyaan Latihan:**
  1. Mengapa seluruh penanda waktu (*timestamp*) di dalam sistem wajib disimpan dalam zona waktu UTC dan hanya dikonversi ke WIB/WITA saat ditampilkan di layar web?
  2. Apa fungsi bidang `is_mock` pada kontrak data, dan mengapa keberadaannya sangat krusial bagi kejujuran laporan ilmiah?
  3. Bagaimana kontrak data menangani situasi ketika pergerakan asap (*motion*) tidak dapat dihitung karena bingkai citra sebelumnya hilang?

### Langkah 3: Memahami Akses Data dan Pembacaan Biner Satelit
- **Berkas yang dibaca:** [`pipeline/config.py`](file:///C:/Users/ADMIN/upwind_proj/pipeline/config.py) dan [`pipeline/hsd_header.py`](file:///C:/Users/ADMIN/upwind_proj/pipeline/hsd_header.py).
- **Apa yang dicari di dalamnya:**
  - Bagaimana skrip Python membaca variabel lingkungan `.env` untuk mengarahkan penyimpanan data mentah ke drive eksternal `D:\upwind_data`?
  - Bagaimana berkas biner Himawari Standard Data (HSD) disusun ke dalam blok-blok header (Header 1 hingga Header 7)?
  - Bagaimana koefisien kalibrasi radiometrik dibaca langsung dari biner berkas tanpa menggunakan pustaka pihak ketiga yang berat?
- **3 Pertanyaan Latihan:**
  1. Mengapa kunci API atau token akses layanan (seperti NASA FIRMS MAP_KEY) dilarang keras ditulis langsung (*hardcoded*) di dalam skrip kode?
  2. Blok header HSD nomor berapa yang menyimpan parameter sudut pemindaian dan informasi proyeksi geosentrik bumi?
  3. Mengapa penanganan data mentah satelit diarahkan ke partisi `D:\upwind_data` dan bukan di dalam direktori proyek partisi `C:`?

### Langkah 4: Memahami Fisika Pengolahan Citra Satelit dan Kalibrasi
- **Berkas yang dibaca:** [`pipeline/olah_himawari_fm1.py`](file:///C:/Users/ADMIN/upwind_proj/pipeline/olah_himawari_fm1.py).
- **Apa yang dicari di dalamnya:**
  - Fungsi `tb_ir`: bagaimana persamaan inversi Planck mengubah radiansi inframerah kanal B07 dan B13 menjadi temperatur kecerahan (Kelvin).
  - Fungsi `potong_lalo`: bagaimana koordinat garis lintang dan garis bujur (*latitude/longitude*) diubah menjadi indeks koordinat piksel baris dan kolom (*line/column*) pada proyeksi geostasioner bumi.
  - Perbedaan perlakuan antara kanal optik pantulan siang hari dan kanal termal emisi radiasi bumi.
- **3 Pertanyaan Latihan:**
  1. Mengapa kanal inframerah gelombang menengah B07 (3,9 µm) mengalami gangguan (*kontaminasi radiasi matahari*) bila digunakan untuk deteksi titik api pada siang hari bolong?
  2. Apa yang terjadi pada gambar hasil render komposit RGB jika tiap kanal warna direntangkan (*contrast stretching*) secara terpisah tanpa peregangan bersama?
  3. Mengapa arah sumbu vertikal $y$ pada proyeksi satelit geostasioner Himawari terbalik نسبت ke sumbu garis lintang geografis bumi?

### Langkah 5: Memahami Penyusunan Tensor Dataset dan Validasi Integritas
- **Berkas yang dibaca:** [`pipeline/pembuat_dataset.py`](file:///C:/Users/ADMIN/upwind_proj/pipeline/pembuat_dataset.py), [`eval/uji_dataset_p3a.py`](file:///C:/Users/ADMIN/upwind_proj/eval/uji_dataset_p3a.py), dan [`eval/test_split_integrity.py`](file:///C:/Users/ADMIN/upwind_proj/eval/test_split_integrity.py).
- **Apa yang dicari di dalamnya:**
  - Mengapa kanal B03 Himawari-9 yang beresolusi 0,5 km diolah dengan metode *area-averaging*, sedangkan kanal 2 km diolah dengan *bilinear* saat disetarakan ke grid 1 km?
  - Bagaimana larik matriks NumPy disusun menjadi bentuk dimensi $(15, 256, 256)$ pada format `.npz`?
  - Bagaimana skrip pengujian memverifikasi bahwa tidak ada tanggal kalender yang sama yang terbelah ke dalam set latih dan set uji?
- **3 Pertanyaan Latihan:**
  1. Jika terdapat 8 adegan pilot, 6 patch per adegan di Kalteng, dan 8 patch per adegan di Riau, mengapa total berkas `.npz` yang terbentuk persis 112 berkas?
  2. Mengapa slot waktu $t-20$ menit dilewati dan digantikan oleh tumpukan kanal pada waktu $t_0, t-10, t-30,$ dan $t-40$ menit?
  3. Mengapa kebocoran data (*data leakage*) pada citra satelit deret waktu tidak dapat dicegah hanya dengan mengocok (*random shuffle*) petak patch secara acak?

### Langkah 6: Memahami Antarmuka Web dan Simulasi Data
- **Berkas yang dibaca:** [`mock/generate_mock_data.py`](file:///C:/Users/ADMIN/upwind_proj/mock/generate_mock_data.py) dan [`web/src/types.ts`](file:///C:/Users/ADMIN/upwind_proj/web/src/types.ts).
- **Apa yang dicari di dalamnya:**
  - Bagaimana struktur antarmuka TypeScript mencerminkan secara persis kontrak data yang didefinisikan pada dokumen arsitektur.
  - Bagaimana generator data tiruan mensimulasikan gumpalan asap elips parametrik, pergeseran koordinat akibat angin, dan penanda kondisi malam hari.
- **3 Pertanyaan Latihan:**
  1. Komponen visual apa di antarmuka web dasbor yang akan muncul ketika properti `is_mock: true` terdeteksi pada berkas data?
  2. Bagaimana antarmuka web membedakan tampilan antara kondisi data normal, data yang mengalami keterlambatan (*stale* > 60 menit), dan kondisi malam hari tanpa pembaruan asap?
  3. Mengapa dasbor web menyajikan visualisasi probabilitas asap dalam bentuk berkas citra PNG transparan yang ditumpangkan (*overlay*) di atas peta Leaflet, dan bukan mengirim larik angka biner mentah ke peramban?

---

## 7. Daftar Hal yang Belum Diverifikasi atau Masih Terbuka

Dokumen ini mencatat secara jujur beberapa hal teknis yang belum dapat dipastikan secara tuntas dalam basis kode saat ini dan memerlukan verifikasi lebih lanjut pada tahap berikutnya:

1. **Kesetaraan Kalibrasi Radiometrik Antara Sensor Himawari-8 dan Himawari-9:**
   Dataset proyek menggabungkan citra arsip tahun 2019 (Himawari-8) dengan citra operasional tahun 2026 (Himawari-9). Meskipun kedua instrumen memiliki spesifikasi kanal AHI yang serupa, kesetaraan koefisien kalibrasi absolut antar-sensor (*cross-calibration drift*) belum diverifikasi secara radiometrik. Perlu dipastikan apakah model yang dilatih pada data H8 2019 dapat langsung inferensi pada data H9 2026 tanpa pergeseran distribusi nilai (*domain shift*). **[Asumsi]**
2. **Ketersediaan Resolusi Pita Merah (B03) pada Arsip AWS:**
   Berdasarkan verifikasi struktur berkas di AWS S3, kanal B03 pada Himawari-8 memiliki pilihan resolusi spasial R05 (0,5 km), R10 (1 km), dan R20 (2 km). Namun pada bucket `noaa-himawari9`, kanal B03 hanya disediakan pada resolusi tertinggi R05 (0,5 km per segmen). Penyetaraan grid 1 km saat ini menggunakan *area-averaging* untuk H9 R05 dan interpolasi *bilinear* untuk H8 R10; dampak perbedaan metode resampling ini terhadap akurasi model belum diuji secara empiris. **[Literatur]**
3. **Aksesibilitas dan Stabilitas Sumber Titik Panas Near-Real-Time:**
   Integrasi titik panas saat ini bergantung pada layanan NASA FIRMS API. Ketersediaan kunci API pengguna (*FIRMS MAP_KEY*), kuota batas unduhan harian, serta latensi waktu edar satelit kutub orbit rendah (S-NPP / NOAA-20 VIIRS yang hanya melintas 1–2 kali per hari pada suatu wilayah) menjadi faktor pembatas utama dalam pelacakan titik panas seketika (*near-real-time*). **[Asumsi]**
4. **Lisensi dan Batasan Kuota Penggunaan Prakiraan Angin Open-Meteo:**
   Pipeline real-time saat ini menggunakan layanan Open-Meteo untuk komponen angin 10 meter ($u, v$). Layanan ini mensyaratkan atribusi lisensi CC BY 4.0 dan memiliki batasan panggilan per jam (*rate limit*). Kebijakan *caching* lokal dan opsi cadangan reanalisis (seperti ERA5-Land dari ECMWF CDS) untuk analisis retrospektif belum diintegrasikan secara otomatis. **[Literatur]**
5. **Relevansi Dataset Pembanding Eksternal (SmokeViz):**
   Penggunaan bobot awal (*pre-trained weights*) dari dataset publik seperti SmokeViz (NeurIPS 2025) belum dapat dipastikan kecocokannya karena SmokeViz dibangun menggunakan instrumen sensor ABI pada satelit GOES yang memantau wilayah benua Amerika Utara (vegetasi hutan konifer/semak subtropis), yang memiliki karakteristik spektral berbeda nyata dengan kebakaran lahan gambut tropis di Indonesia. **[Literatur]**
6. **Kalibrasi Ambang Batas Topeng Awan Dingin Tropis:**
   Ambang batas $TB_{13} < 265\text{ K}$ saat ini ditetapkan sebagai aturan heuristik desain awal. Karakteristik awan sirus tipis (*cirrus*) di atmosfer tropis Indonesia yang sering kali bertemperatur relatif hangat ($265\text{ K} - 273\text{ K}$) namun tetap membingungkan deteksi visual asap belum dievaluasi batas toleransinya secara kuantitatif. **[Usulan desain]**
