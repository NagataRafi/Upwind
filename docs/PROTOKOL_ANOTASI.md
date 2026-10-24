# Protokol Anotasi Label Asap Karhutla (Persiapan P3)

> [!IMPORTANT]
> Dokumen ini mengatur tata cara pembuatan label ground-truth untuk pelatihan dan evaluasi model segmentasi AI pada Fase P3. Dokumen ini mengikuti prinsip kejujuran: **tidak membuat label otomatis sendiri** dan **tidak menggunakan produk sebaran asap BMKG sebagai label** (menghormati lisensi dan aturan Tujuan.md Bagian 6). Label klaim: **[Literatur]**, **[Asumsi]**, **[Usulan desain]**.

---

## 1. Definisi Kelas & Karakteristik Visual

Pada citra geostasioner Himawari (resolusi 0,5 km – 2 km), pembedaan asap gambut dari awan dan daratan memerlukan kombinasi kanal optik (B01–B04) dan kanal inframerah termal (B13 10,4 µm).

| Kelas | Kode | Kriteria Spektral & Visual | Perlakuan Anotasi |
| :--- | :---: | :--- | :--- |
| **Asap Pekat** | `1` | Warna kelabu keputihan/kecokelatan seragam; mengaburkan kontur permukaan tanah; tepi difus/menyebar; suhu kecerahan $TB_{13} > 275\text{ K}$ (dekat permukaan tanah tropis). | Digambar poligon utuh mengikuti tepi gumpalan utama. |
| **Asap Tipis / Kabur** | `2` | Lapisan kabur tipis; kenampakan daratan di bawahnya masih terlihat samar; albedo sedikit lebih tinggi dari tanah bersih. | Diberi poligon terpisah dengan label atribut `asap_tipis`. Jangan dicampur ke dalam poligon asap pekat agar model tidak terdistorsi pada batas kabur. **[Usulan desain]** |
| **Awan Dingin / Tinggi** | `0` (Mask) | Reflektansi tampak sangat tinggi (putih cemerlang); puncak awan dingin dengan $TB_{13} < 265\text{ K}$. | Otomatis dieksklusi oleh topeng awan dingin B13; penganotasi **tidak boleh** melabeli sebagai asap. |
| **Awan Rendah / Kumulus** | `0` (Negatif) | Gumpalan putih berbutir dengan tepi tajam (*popcorn clouds*); bayangan awan terlihat jelas di sisi berlawanan matahari. | Dilabeli negatif (bukan asap). |
| **Asap di Bawah Awan** | `3` (Terhalang) | Area asap yang tertutup oleh awan es tinggi di atasnya ($TB_{13} < 265\text{ K}$). | Ditandai sebagai `terhalang_awan` (*obscured*), tidak dilabeli sebagai asap terbuka. |
| **Bayangan Awan** | `0` (Negatif) | Bercak gelap pada daratan yang sejajar dengan posisi awan kumulus di atasnya. | Dilarang dikira sebagai area terbakar atau asap gelap. |

---

## 2. Panduan Mengatasi Keraguan (Ambiguity Protocol)

1. **Membandingkan dengan Kontrol Bersih (Side-by-side)**:
   Setiap adegan asap (misal 14 September 2019 pukul 03:00 UTC) **wajib disandingkan** dengan citra kontrol bersih pada jam yang sama (15 Oktober 2019 pukul 03:00 UTC).
   - Bila suatu area tampak terang di kedua tanggal, area tersebut adalah pantulan tanah terbuka/tanah kering, **bukan asap**.
   - Bila area tersebut hanya tampak kelabu-putih difus pada tanggal kebakaran, area tersebut adalah **asap**.
2. **Area Sangat Ragu (*Uncertain Areas*)**:
   Bila penganotasi tidak dapat memastikan apakah suatu piksel adalah kabut tipis atau pantulan tanah/kabut uap air alami, tandai poligon tersebut dengan atribut `ragu: true`. Poligon ini akan dieksklusi dari perhitungan rugi-rugi (*loss function*) model saat pelatihan agar tidak merusak konvergensi.

---

## 3. Aturan Konsistensi Dua Penganotasi (*Inter-Annotator Agreement*)

Agar label yang dihasilkan konsisten bila dikerjakan oleh 2 sampai 4 anggota tim:

1. **Kalibrasi Awal**:
   Kedua penganotasi secara independen membuat poligon untuk **3 adegan uji yang sama** (tanpa saling melihat hasil).
2. **Pengukuran Kesepakatan**:
   Hitung nilai *Intersection over Union* (IoU) antar-mask:
   $$\text{IoU} = \frac{|A \cap B|}{|A \cup B|}$$
3. **Syarat Kelulusan**:
   - Target kesepakatan awal: $\text{IoU} \ge 0.70$ untuk kelas Asap Pekat. **[Usulan desain]**
   - Bila $\text{IoU} < 0.70$, kedua penganotasi wajib mengadakan sesi evaluasi bersama (*reconciliation meeting*) untuk menyamakan persepsi batas tepi sebelum melanjutkan ke adegan lainnya.

---

## 4. Alat Bantu Anotasi Sederhana

Proyek menyediakan skrip pembantu [`pipeline/siapkan_anotasi.py`](file:///C:/Users/ADMIN/upwind_proj/pipeline/siapkan_anotasi.py) untuk menyiapkan bahan anotasi:
1. Mengekstrak crop wilayah Riau / Kalimantan Tengah dari citra mentah HSD.
2. Menyusun GeoTIFF 4-band georeferensi WGS84 (B03-Merah, B02-Hijau, B01-Biru, B13-Termal).
3. Menghasilkan template GeoJSON dengan skema atribut resmi:
   ```json
   {
     "type": "Feature",
     "properties": {
       "kelas": "asap_pekat",
       "penganotasi": "nama_peneliti",
       "confidence": "tinggi",
       "ragu": false,
       "waktu_anotasi_utc": "2026-10-24T10:00:00Z"
     },
     "geometry": { ... }
   }
   ```
4. Penganotasi cukup membuka GeoTIFF dan GeoJSON tersebut di perangkat lunak gratis **QGIS** (atau CVAT/Labelme) untuk menggambar poligon batas asap.

---

## 5. Usulan Anggaran Adegan Awal & Estimasi Waktu

> [!NOTE]
> Angka berikut adalah **[Usulan desain]**, bukan fakta yang dipaksakan.

- **Jumlah Adegan Awal yang Diusulkan**: **5 hingga 8 adegan**
  - 3 adegan puncak asap (September 2019 Kalimantan & Sumatra).
  - 2 adegan kontrol bersih / musim hujan (Oktober 2019 & Januari 2019).
  - 1–3 adegan variasi Himawari-9 terkini.
- **Estimasi Waktu Pengerjaan per Adegan**:
  - Diperkirakan membutuhkan **20 hingga 45 menit per adegan** bagi seorang penganotasi (bergantung pada luas dan percabangan gumpalan asap serta fraksi awan).
