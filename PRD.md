# PRD: Upwind, pemantau asap karhutla dan titik panas hulu asap

Versi 0.1, 22 Oktober 2026. Pemilik: tim proyek PCD dan AI. Status: draf untuk dikerjakan agen AI; diperbarui setelah wawancara relawan.

Label klaim: **[Literatur]**, **[Asumsi]**, **[Usulan desain]**.

## 0. Untuk agen yang membaca ini pertama kali

Berkas pendukung berikut **wajib ada** di akar proyek dan wajib dibaca sebelum bekerja. Bila salah satu belum ada, buat dulu dari isi dokumen ini sebelum menulis kode apa pun.

| Berkas | Fungsi | Siapa yang memeliharanya |
| --- | --- | --- |
| `Tujuan.md` | Untuk apa proyek ini, pengguna, kriteria sukses, prinsip tidak boleh dilanggar | Pemilik proyek; agen hanya mengusulkan perubahan |
| `ARSITEKTUR.md` | Komponen, kontrak data, batasan teknis, hal belum diverifikasi | Agen arsitek; perubahan kontrak perlu persetujuan pengguna |
| `Agents.md` | Peran agen, aturan kerja, definisi selesai, kapan harus berhenti dan bertanya | Pemilik proyek |
| `Changelog.md` | Catatan setiap perubahan **dengan tanggal dan jam** (WIB dan UTC) | Semua agen, setiap selesai satu perubahan |

Urutan baca: Tujuan.md, ARSITEKTUR.md, Agents.md, lalu PRD ini. Setelah selesai satu unit pekerjaan, tambahkan entri di Changelog.md sebelum melapor. PRD ini tidak berisi kode; kode ditulis agen mengikuti PRD, ARSITEKTUR, dan Agents.

## 1. Ringkasan

Upwind mengambil citra Himawari-9, membuat peta asap karhutla di Riau dan Kalimantan Tengah, lalu menampilkannya di dasbor bersama titik panas dan angin, dengan daftar titik panas yang paling mungkin menjadi sumber asap (titik panas hulu asap). Pengguna: relawan lapangan (ponsel) dan komando satgas (desktop). Latar, tujuan, dan prinsip: lihat Tujuan.md.

## 2. Keputusan yang sudah diambil

| Keputusan | Pilihan | Sumber keputusan |
| --- | --- | --- |
| Nama aplikasi | **Upwind** dengan penjelas "pemantau asap karhutla dan titik panas hulu asap" | Dipilih pengguna, 22 Okt 2026 |
| Fokus proyek | Segmentasi asap near-real-time dan dasbor satgas | Arahan dosen, 22 Okt 2026 |
| Inti kontribusi | Segmentasi dari urutan frame; titik panas hulu asap | Disepakati pengguna, 22 Okt 2026 |
| Urutan kerja | Web lebih dulu dengan data tiruan, lalu sambung data asli | Dipilih pengguna |
| Stack web | Diserahkan kepada agen, dicatat di Changelog.md | Dipilih pengguna |
| Penayangan | Laptop lokal untuk demo | Dipilih pengguna |
| Pengguna dasbor | Relawan lapangan dan komando satgas, satu web responsif | Dipilih pengguna |
| Perangkat latih | Laptop GPU dengan 6 sampai 8 GB VRAM | Dijawab pengguna |
| Format dokumen | Berkas .md sepaket | Dipilih pengguna |
| Wawancara relawan | Paralel; PRD memakai asumsi di bagian 10 dan direvisi setelahnya | Dipilih pengguna |

## 3. Fase kerja

Setiap fase punya syarat keluar. Fase berikutnya tidak dimulai sebelum syarat keluar fase sebelumnya terpenuhi dan dicatat di Changelog.md. Fase 1 dan 2 dapat berjalan paralel karena web memakai data tiruan.

| Fase | Isi | Syarat keluar |
| --- | --- | --- |
| P0. Fondasi | Struktur folder, kelima berkas pendukung, pemilihan stack, kontrak data (ARSITEKTUR.md bagian 3) | Kontrak data disetujui pengguna; Changelog.md berisi pilihan stack dan alasannya |
| P1. Web dengan data tiruan | Dasbor penuh membaca data tiruan dari generator sesuai kontrak | Semua FR-W lulus kriteria penerimaan dengan `is_mock` benar; teman relawan bisa mencoba |
| P2. Pipeline data asli | Pengambilan Himawari, titik panas, angin; pengolahan citra; pemeriksaan visual asap gambut 2019 | Satu rangkaian hari tersimpan sesuai kontrak; hasil pemeriksaan visual dicatat (asap terlihat atau tidak) |
| P3. Model | Baseline, U-Net satu frame, U-Net multi-frame, SegFormer; evaluasi | Tabel hasil per skenario dengan tiga seed dan hasil per kejadian |
| P4. Smoke-to-source | Aturan skor, pembanding, evaluasi retrospektif | Tabel hasil terhadap pembanding; keterbatasan dinyatakan |
| P5. Integrasi | Data asli menggantikan data tiruan; pengukuran latensi | Dasbor menampilkan data asli tanpa mengubah web; latensi tercatat |
| P6. Evaluasi akhir dan demo | Uji dengan relawan, revisi, laporan | Laporan, demo lokal berjalan, daftar keterbatasan jujur |

Catatan jadwal: P2 berisiko, karena kenyataan data (band, akses titik panas dan angin, terlihatnya asap gambut) belum diverifikasi. Pemeriksaan di P2 boleh dimajukan lebih awal; hasilnya bisa mengubah P3. **[Asumsi]**

## 4. Kebutuhan fungsional: aplikasi web (FR-W)

Antarmuka berbahasa Indonesia. Waktu ditampilkan dalam WIB atau WITA sesuai wilayah, dengan UTC tersedia di keterangan.

| ID | Kebutuhan | Kriteria penerimaan |
| --- | --- | --- |
| FR-W1 | Peta utama dengan pilihan wilayah (Riau, Kalimantan Tengah) | Peta terbuka pada wilayah terpilih; berpindah wilayah memuat bingkai terbaru wilayah itu |
| FR-W2 | Lapisan mask asap dengan slider transparansi | Lapisan bisa dinyalakan dan dimatikan; transparansi berubah halus |
| FR-W3 | Lapisan ketidakpastian per piksel | Bisa dinyalakan terpisah; legenda menjelaskan artinya |
| FR-W4 | Lapisan titik panas | Setiap titik bisa dipilih dan menampilkan waktu, sumber, kepercayaan |
| FR-W5 | Lapisan angin berupa panah | Panah menunjukkan arah dan kecepatan; ada keterangan satuan |
| FR-W6 | Panel "Titik panas hulu asap" | Menampilkan peringkat, skor, penjelasan satu kalimat; memilih baris menyorot titik di peta |
| FR-W7 | Panah arah gerak asap | Menampilkan arah dan perkiraan kecepatan; menyatakan bila perkiraan tidak dapat dihitung |
| FR-W8 | Kartu ringkasan: luas asap (km²), jumlah titik panas, jumlah desa dalam zona asap bila data batas desa tersedia | Angka sama dengan data bingkai; kartu desa disembunyikan bila batas desa belum ada, tidak diisi karangan |
| FR-W9 | Pencarian waktu 24 jam terakhir | Menggeser waktu mengganti bingkai asap, titik panas, dan peringkat sesuai waktunya |
| FR-W10 | Penanda data tiruan | Bila `is_mock` benar, spanduk "DATA CONTOH, BUKAN DATA ASLI" tampil permanen di atas peta dan di tangkapan layar; tidak bisa ditutup |
| FR-W11 | Status data | Menampilkan waktu citra terakhir, usia data dalam menit, status tiap sumber; peringatan bila usia data melewati ambang |
| FR-W12 | Penanda malam hari dan awan | Pada `daylight` salah, menampilkan "Malam: tidak ada pembaruan asap"; menampilkan tutupan awan bila tinggi |
| FR-W13 | Label dan batas | Setiap layar memuat "perkiraan, bukan jaminan"; halaman "Tentang dan keterbatasan" menjelaskan bahwa asap bukan titik api dan titik panas bisa meleset |
| FR-W14 | Atribusi sumber | Himawari, NASA FIRMS atau sumber titik panas lain, sumber angin, tertulis di kaki halaman; sesuai syarat lisensi |
| FR-W15 | Responsif | Ponsel: panel menjadi lembar geser dari bawah, kontrol utama terjangkau satu tangan; desktop: panel samping dan ringkasan |
| FR-W16 | Hemat data | Gambar hasil dikompres; tidak memuat bingkai yang belum diminta pengguna |
| FR-W17 | Identitas aplikasi | Nama "Upwind" dan penjelas "pemantau asap karhutla dan titik panas hulu asap" tampil di header dan halaman Tentang; judul tab peramban memuat "Upwind" |

Tidak ada akun, notifikasi, atau penayangan publik pada versi ini.

## 5. Kebutuhan fungsional: data dan pengolahan citra (FR-D)

| ID | Kebutuhan | Kriteria penerimaan |
| --- | --- | --- |
| FR-D1 | Pengambilan citra Himawari-9 dari AWS tanpa akun, pada jadwal tetap | Citra terbaru wilayah terunduh; kegagalan dicatat dan tidak menghentikan jadwal |
| FR-D2 | Pemotongan wilayah Riau dan Kalimantan Tengah dan penyusunan tumpukan band | Keluaran sesuai bentuk masukan model; band yang dipakai tercatat |
| FR-D3 | Masking awan dan malam | Mask tersedia per bingkai; fraksi awan tercatat |
| FR-D4 | Penyusunan tumpukan N frame berturut-turut | Frame yang hilang ditangani dan dicatat, bukan diisi karangan |
| FR-D5 | Pasca-proses mask: hapus gumpalan kecil, hitung luas | Luas km² dihitung dari piksel dan resolusi sebenarnya |
| FR-D6 | Pengambilan titik panas | Sumber diverifikasi dulu (ARSITEKTUR.md bagian 7); data lolos kontrak 3.2 |
| FR-D7 | Pengambilan angin | Sumber diverifikasi dulu; bila komponen angin yang dibutuhkan tidak tersedia, agen melapor ke pengguna, tidak mengarang |
| FR-D8 | Jejak asal | Setiap keluaran mencatat citra masukan, versi model dan kode, waktu pemrosesan |
| FR-D9 | Pengukuran latensi | Waktu dari pengambilan citra sampai hasil siap tercatat per bingkai |

## 6. Kebutuhan fungsional: model (FR-M)

| ID | Kebutuhan | Kriteria penerimaan |
| --- | --- | --- |
| FR-M1 | Pemeriksaan visual kelayakan | Beberapa kasus 2019 diperiksa; dicatat apakah asap gambut terlihat di citra Himawari; hasil negatif dilaporkan ke pengguna sebelum model dibangun |
| FR-M2 | Strategi label | Anotasi poligon sendiri di QGIS dengan VIIRS true color sebagai pembanding; pelatihan awal dari SmokeViz bila lisensi dan sensornya terbukti cocok; target awal kecil, dikembangkan sesuai kurva belajar |
| FR-M3 | Baseline B1 dan B2 | Aturan ambang dan Random Forest per piksel; hasil dilaporkan lebih dulu |
| FR-M4 | Model M1 dan M2 | U-Net dengan satu frame dan dengan beberapa frame; hasil dibandingkan di data uji yang sama |
| FR-M5 | Model pembanding M3 | SegFormer kecil |
| FR-M6 | Ablation | Satu frame lawan multi-frame; dengan dan tanpa masking awan; dengan dan tanpa indeks aerosol Sentinel-5P bila dipakai |
| FR-M7 | Ketidakpastian per piksel | Peta ketidakpastian dihasilkan dan dievaluasi terhadap kesalahan |
| FR-M8 | Metrik | IoU, F1, precision, recall, selisih luas, tingkat awan salah dikira asap; rata-rata dan simpangan baku tiga seed; hasil per kejadian |
| FR-M9 | Pembagian data | Per hari atau kejadian; satu kejadian dan satu provinsi disisihkan untuk uji lintas wilayah |
| FR-M10 | Batas perangkat | Pelatihan berjalan pada 6 sampai 8 GB VRAM; ukuran potongan, batch, dan presisi tercatat |

## 7. Kebutuhan fungsional: smoke-to-source (FR-S)

| ID | Kebutuhan | Kriteria penerimaan |
| --- | --- | --- |
| FR-S1 | Perkiraan arah dan kecepatan gerak asap dari bingkai berturut-turut | Hasil beserta kualitas; "tidak dapat dihitung" bila bingkai tidak cukup |
| FR-S2 | Sektor hulu dari arah gerak dan angin | Sektor ditampilkan di peta bila pengguna meminta |
| FR-S3 | Kandidat dan skor titik panas | Skor dari jarak ke tepi hulu, kesesuaian sudut, dan kepercayaan titik panas; bobot tercatat sebagai parameter |
| FR-S4 | Penjelasan per baris peringkat | Satu kalimat Indonesia yang menyebut faktor utama |
| FR-S5 | Pembanding | Titik panas terdekat dengan pusat asap, dan pilihan acak, dievaluasi dengan cara yang sama |
| FR-S6 | Evaluasi retrospektif | Apakah titik panas peringkat atas kemudian terbukti terbakar (misalnya lewat area terbakar Sentinel-2 beberapa hari kemudian); laporan menyatakan bahwa ini menguji sumber kebakaran, bukan sumber asap tertentu |
| FR-S7 | Ablation bobot | Pengaruh tiap faktor skor dilaporkan |

Skor ini heuristik dan hasilnya belum diketahui. Bila tidak mengalahkan pembanding, laporkan apa adanya. **[Asumsi]**

## 8. Kebutuhan non-fungsional

| ID | Kebutuhan | Ukuran |
| --- | --- | --- |
| NFR1 | Latensi | Sasaran kurang dari 60 menit dari pengambilan citra sampai tampil pada siang hari; batas keras 24 jam. **[Usulan desain]** |
| NFR2 | Keandalan | Kegagalan satu sumber tidak mematikan dasbor; status tampil di FR-W11 |
| NFR3 | Kinerja web | Bingkai pertama tampil kurang dari 3 detik di laptop lokal dengan data tiruan. **[Usulan desain]** |
| NFR4 | Kejujuran | Tidak ada data karangan tampil sebagai data asli; semua hasil dilabeli sesuai kelasnya |
| NFR5 | Reproduksibilitas | Hasil evaluasi bisa diulang dari kode, seed, dan versi data yang tercatat |
| NFR6 | Lisensi | Atribusi dan batas pemakaian dipatuhi (Tujuan.md bagian 6) |
| NFR7 | Keamanan dasar | Tidak ada rahasia di repositori; masukan pengguna divalidasi |

## 9. Pertanyaan terbuka dan hal yang harus diverifikasi

Agen tidak boleh mengisi jawabannya dengan dugaan. Bila terblokir, laporkan ke pengguna.

1. Daftar band, resolusi, dan format berkas Himawari-9 di AWS.
2. Apakah asap gambut terlihat jelas di citra Himawari pada kasus 2019 (FR-M1).
3. Akses dan lisensi titik panas (FIRMS atau pengganti).
4. Sumber angin dan ketersediaan komponen 10 m.
5. Lisensi, sensor, dan wilayah SmokeViz.
6. Ketersediaan batas desa untuk FR-W8.
7. Pembanding resmi: isi SiPongi dan produk BMKG, untuk klaim kontribusi di laporan.

## 10. Asumsi pengguna yang divalidasi lewat wawancara relawan

Setiap asumsi ini **[Asumsi]** sampai ada jawaban. Daftar ini juga pertanyaan wawancara.

| Asumsi | Pertanyaan untuk relawan |
| --- | --- |
| Relawan memakai ponsel di lapangan dengan sinyal terbatas | Perangkat dan kualitas sinyal apa yang Anda pakai di lokasi? |
| Daftar titik panas paling berguna bila diurutkan | Bagaimana Anda sekarang memutuskan titik mana yang dicek lebih dulu? |
| Peta asap membantu keputusan | Kapan peta asap berguna, dan kapan tidak? |
| Pembaruan beberapa kali sehari cukup | Seberapa sering Anda butuh informasi baru? |
| Penjelasan satu kalimat cukup | Informasi apa yang kurang pada penjelasan seperti ini? (tunjukkan contoh) |
| Relawan paham istilah "titik panas" dan "ketidakpastian" | Istilah apa yang membingungkan? |
| Informasi malam hari tidak dapat diandalkan | Apakah keterangan "tidak ada pembaruan malam" membantu atau mengganggu? |
| Komando butuh ringkasan dan riwayat | Siapa yang memakai ringkasan, dan untuk laporan apa? |

Hasil wawancara dicatat di `docs/` dan dirangkum di Changelog.md; PRD direvisi setelahnya.

## 11. Risiko

| Risiko | Mitigasi |
| --- | --- |
| Asap gambut tidak terlihat jelas di Himawari | Pemeriksaan FR-M1 dimajukan; hasil negatif dilaporkan sebelum investasi besar |
| Tidak ada label Indonesia | Anotasi sendiri, pelatihan awal, pseudo-label; target kecil |
| Asap tertukar dengan awan | Masking awan, metrik khusus, uji multi-frame |
| Titik panas meleset | Peringkat dilabeli perkiraan; keterbatasan di halaman Tentang |
| Produk BMKG sudah ada | Tidak mengklaim kebaruan; kontribusi dirumuskan sebagai evaluasi dan fitur hulu asap |
| Peringkat tidak mengalahkan pembanding | Laporkan jujur; hasil negatif tetap temuan |
| Waktu habis | Web dengan data tiruan selesai lebih dulu; fase lanjutan boleh dipotong |
| Data tiruan terbaca sebagai asli | FR-W10 wajib, diuji pada setiap rilis |

## 12. Di luar lingkup

Lihat Tujuan.md bagian 5.

## 13. Sumber

- [Himawari di AWS Open Data](https://registry.opendata.aws/noaa-himawari/)
- [BMKG Satelit Cuaca](https://www.bmkg.go.id/satelit/)
- [BRIN: validasi hotspot Himawari-8 Kalimantan Tengah](https://karya.brin.go.id/id/eprint/11573/)
- [JAXA Himawari-8 Wild Fire product](https://www.eorc.jaxa.jp/ptree/documents/README_H08_L2WLF.txt)
- [SmokeViz, NeurIPS 2025](https://neurips.cc/virtual/2025/poster/121682)
- [SIT-FUSE](https://arxiv.org/pdf/2510.09845)
- [MultiNatSmoke](https://arxiv.org/pdf/2604.23542)
- [Sentinel-5P NRTI aerosol index](https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S5P_NRTI_L3_AER_AI)