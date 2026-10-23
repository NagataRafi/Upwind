# Kontrak Data: Upwind

Dokumen ini adalah perincian teknis dari ARSITEKTUR.md Bagian 3, mendefinisikan skema JSON dan representasi data yang dipertukarkan antara Lapisan Pengolahan Citra / Model AI / Data Tiruan (Penyedia) dan Lapisan Web Dasbor (Konsumen).

Label klaim: **[Usulan desain]**

---

## 1. Konvensi Umum
1. **Waktu:** Seluruh waktu disimpan dalam string ISO 8601 UTC dengan akhiran `Z` (contoh: `"2026-10-22T06:00:00Z"`). Pada antarmuka pengguna, kedua wilayah (Riau dan Kalimantan Tengah) ditampilkan dalam waktu Indonesia Barat (WIB = UTC+7) dengan keterangan waktu UTC tersedia di tooltip/keterangan.
2. **Koordinat:** Seluruh koordinat geografis menggunakan format WGS84 (EPSG:4326), `[longitude, latitude]`.
3. **Bbox:** Array empat angka: `[min_lon, min_lat, max_lon, max_lat]` (Barat, Selatan, Timur, Utara).
4. **Data Tiruan:** Bidang `is_mock` wajib bertipe `boolean`. Bila bernilai `true`, web wajib menampilkan spanduk FR-W10 secara permanen.
5. **Wilayah (`region_id`):** `"riau"` atau `"kalteng"`.

---

## 2. Struktur Endpoint dan Indeks Berkas

Untuk memenuhi FR-W9 (pencarian waktu 24 jam terakhir), sistem menyediakan indeks daftar bingkai per wilayah:
- Ringkasan Status Sistem: `/data/status.json`
- Indeks Bingkai per Wilayah: `/data/{region_id}/index.json`
  Berisi daftar urutan kronologis bingkai 24 jam terakhir:
  ```json
  [
    {
      "timestamp_utc": "2026-10-22T06:00:00Z",
      "daylight": true,
      "cloud_cover_fraction": 0.28,
      "area_km2": 142.5,
      "has_smoke": true
    }
  ]
  ```
- Data Lengkap per Bingkai: `/data/{region_id}/{timestamp_utc_safe}.json` (karakter `:` diganti `-` pada nama berkas bila perlu kompatibilitas filesystem, misal `2026-10-22T06-00-00Z.json`).
- Lapisan Gambar Transparan (Overlay):
  - Mask Asap: `/overlays/{region_id}/{timestamp_utc_safe}/smoke_mask.png`
  - Probabilitas: `/overlays/{region_id}/{timestamp_utc_safe}/smoke_prob.png`
  - Ketidakpastian: `/overlays/{region_id}/{timestamp_utc_safe}/smoke_unc.png`

---

## 3. Rincian Skema Objek (Lengkap ARSITEKTUR.md Bagian 3)

### 3.1 `SmokeFrame` (Bingkai Asap)
Mewakili kondisi segmentasi asap pada satu waktu tertentu untuk satu wilayah.

```json
{
  "timestamp_utc": "2026-10-22T06:00:00Z",
  "processed_utc": "2026-10-22T06:25:12Z",
  "region_id": "riau",
  "bbox": [100.0, -1.1, 104.0, 2.5],
  "mask_overlay": "/overlays/riau/2026-10-22T06-00-00Z/smoke_mask.png",
  "probability_overlay": "/overlays/riau/2026-10-22T06-00-00Z/smoke_prob.png",
  "uncertainty_overlay": "/overlays/riau/2026-10-22T06-00-00Z/smoke_unc.png",
  "area_km2": 142.5,
  "motion": {
    "direction_deg": 45.0,
    "speed_kmh": 12.3,
    "quality": "good",
    "status_text": "45° (Timur Laut) - 12 km/jam"
  },
  "source_frames": [
    "2026-10-22T05:40:00Z",
    "2026-10-22T05:50:00Z",
    "2026-10-22T06:00:00Z"
  ],
  "daylight": true,
  "cloud_cover_fraction": 0.28,
  "model_version": "unet_multiframe_v0.1",
  "code_version": "git-7a8f3c",
  "is_mock": true
}
```

**Keterangan Lapangan Wajib:**
- `probability_overlay`: Path/URL gambar probabilitas asap per piksel untuk visualisasi gradien keyakinan model.
- `uncertainty_overlay`: Path/URL gambar ketidakpastian per piksel (FR-W3).
- `motion`: Objek perkiraan gerak asap.
  - `direction_deg`: Derajat arah gerak (0-360, null bila tidak dapat dihitung).
  - `speed_kmh`: Kecepatan dalam km/jam (null bila tidak dapat dihitung).
  - `quality`: `"good" | "moderate" | "poor" | "unavailable"`.
  - `status_text`: Teks status deskriptif. Bila frame tidak cukup atau gerak tak dapat ditentukan, bernilai `"tidak dapat dihitung"` (sesuai FR-S1 dan FR-W7).
- `source_frames`: Array string timestamp UTC dari citra masukan yang dipakai. Bila ada frame yang hilang dalam urutan, array ini mencerminkan celah tersebut secara jujur.
- `daylight`: `boolean`. Jika `false` (malam hari), web menampilkan "Malam: tidak ada pembaruan asap" (FR-W12).
- `cloud_cover_fraction`: Pecahan tutupan awan (0.0 sampai 1.0). Bila >0.7, web menampilkan peringatan tutupan awan tinggi.
- `model_version`, `code_version`: Jejak asal pemrosesan (FR-D8).
- `is_mock`: `boolean` (wajib `true` pada fase data tiruan).

---

### 3.2 `Hotspot` (Titik Panas)

```json
{
  "id": "hp_riau_20261022_001",
  "time_utc": "2026-10-22T05:30:00Z",
  "lat": 1.345,
  "lon": 101.452,
  "source": "VIIRS_NOAA20",
  "confidence": 85,
  "frp": 24.6,
  "is_peat": true,
  "is_mock": true
}
```

**Keterangan Lapangan Wajib:**
- `is_peat`: `boolean`. `true` bila titik panas berada di atas kubah gambut.
- `confidence`: Tingkat keyakinan deteksi (angka 0-100 atau label string).
- `frp`: *Fire Radiative Power* (MW).

---

### 3.3 `WindSample` (Sampel Angin)

```json
{
  "time_utc": "2026-10-22T06:00:00Z",
  "lat": 1.35,
  "lon": 101.45,
  "u": 2.1,
  "v": 1.8,
  "height_m": 10,
  "source": "ERA5_reanalysis",
  "is_mock": true
}
```

**Keterangan Lapangan Wajib:**
- `height_m`: Ketinggian pengukuran angin (default: 10 m sesuai ARSITEKTUR.md).
- `u`, `v`: Komponen kecepatan angin zonal dan meridional dalam m/s.

---

### 3.4 `RankedSource` (Peringkat Titik Panas Hulu Asap)

```json
{
  "frame_timestamp_utc": "2026-10-22T06:00:00Z",
  "hotspot_id": "hp_riau_20261022_001",
  "rank": 1,
  "score": 0.88,
  "factors": {
    "distance_to_upwind_edge_km": 4.2,
    "angle_difference_deg": 12.0,
    "hotspot_confidence": 0.85,
    "peat_factor": 1.2
  },
  "explanation": "Berada 4,2 km di sektor hulu arah angin dan bertepatan di lahan gambut berdaya tinggi (FRP 24,6 MW).",
  "method_version": "heuristik_v0.1",
  "is_mock": true
}
```

**Keterangan Lapangan Wajib:**
- `factors`: Objek rincian komponen faktor penentu skor (jarak hulu, selisih sudut, keyakinan hotspot, status gambut).
- `explanation`: Kalimat pendek berbahasa Indonesia yang jelas untuk relawan lapangan.
- `method_version`: Versi algoritma/metode penilaian.

---

### 3.5 `SystemStatus` (Status Sistem)

```json
{
  "last_processed_utc": "2026-10-22T06:25:12Z",
  "latest_frame_utc": "2026-10-22T06:00:00Z",
  "data_age_minutes": 25,
  "sources_status": {
    "himawari": "ok",
    "hotspot": "ok",
    "wind": "ok"
  },
  "night_no_smoke_update": false,
  "cloud_cover_high": false,
  "is_mock": true
}
```

---

## 4. Paket Data Per Bingkai (`FrameBundle`)

Untuk efisiensi pembacaan web dalam satu tarikan per timestamp (FR-W16: hemat data):
```json
{
  "frame": { /* Objek SmokeFrame */ },
  "hotspots": [ /* Array Objek Hotspot */ ],
  "wind": [ /* Array Objek WindSample */ ],
  "ranked_sources": [ /* Array Objek RankedSource */ ]
}
```
