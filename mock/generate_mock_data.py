"""
Generator Data Tiruan Upwind
Menghasilkan data tiruan sesuai kontrak data ARSITEKTUR.md Bagian 3 dan docs/KONTRAK_DATA.md.
Mencakup kasus sulit: malam hari, awan tebal, bingkai hilang, data basi, gerak asap tak terhitung, dan hari cerah.
Semua data membawa penanda `is_mock = True`.
"""

import os
import json
import zlib
import struct
import math
from datetime import datetime, timezone, timedelta

# KEPUTUSAN 2026-10-23: Ambang usia data basi ditetapkan 60 menit (PRD.md NFR1
# sasaran latensi < 60 menit pada siang hari). Konstanta tunggal dipakai
# generator; web memakai nilai sama di web/src/api.ts dan harus diubah serentak.
STALE_THRESHOLD_MINUTES = 60

def create_png_rgba(width, height, pixel_func):
    """
    Membuat file PNG RGBA murni tanpa pustaka pihak ketiga menggunakan zlib dan struct.
    pixel_func(x, y) mengembalikan tuple (r, g, b, a) di mana nilai 0-255.
    """
    raw_bytes = bytearray()
    for y in range(height):
        raw_bytes.append(0)  # filter type 0 (None)
        for x in range(width):
            r, g, b, a = pixel_func(x, y)
            raw_bytes.extend((r, g, b, a))

    def chunk(tag, data):
        crc = zlib.crc32(tag + data) & 0xffffffff
        return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', crc)

    png_header = b'\x89PNG\r\n\x1a\n'
    ihdr = struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0)
    idat = zlib.compress(bytes(raw_bytes), 9)

    return png_header + chunk(b'IHDR', ihdr) + chunk(b'IDAT', idat) + chunk(b'IEND', b'')

def generate_smoke_images(out_dir, has_smoke=True, center_pct=(0.5, 0.5), radius_pct=0.25):
    """
    Menghasilkan 3 overlay gambar PNG:
    - smoke_mask.png (warna abu-abu semi-transparan dengan batas halus)
    - smoke_prob.png (warna gradien kuning-oranye-merah)
    - smoke_unc.png (warna gradien ungu-biru ketidakpastian)
    """
    os.makedirs(out_dir, exist_ok=True)
    width, height = 256, 256
    cx = width * center_pct[0]
    cy = height * center_pct[1]
    max_r = width * radius_pct

    def mask_pixel(x, y):
        if not has_smoke:
            return (0, 0, 0, 0)
        # Distorsi elips dan gumpalan asap
        dx = (x - cx) * 1.2
        dy = (y - cy) * 0.8
        # Noise deterministik sederhana
        noise = math.sin(x * 0.1) * math.cos(y * 0.1) * 8.0
        dist = max(0.0, math.sqrt(dx * dx + dy * dy) + noise)
        if dist < max_r:
            ratio = max(0.0, min(1.0, dist / max_r))
            alpha = int(180 * (1.0 - ratio ** 1.5))
            alpha = max(0, min(200, alpha))
            return (120, 115, 110, alpha)
        return (0, 0, 0, 0)

    def prob_pixel(x, y):
        if not has_smoke:
            return (0, 0, 0, 0)
        dx = (x - cx) * 1.2
        dy = (y - cy) * 0.8
        dist = math.sqrt(dx * dx + dy * dy)
        if dist < max_r:
            prob = max(0.0, min(1.0, 1.0 - dist / max_r))
            alpha = int(prob * 190)
            # Gradien warna: Kuning -> Oranye -> Merah pekat
            r = 255
            g = int(220 * (1.0 - prob * 0.7))
            b = int(40 * (1.0 - prob))
            return (r, g, b, alpha)
        return (0, 0, 0, 0)

    def unc_pixel(x, y):
        if not has_smoke:
            return (0, 0, 0, 0)
        dx = (x - cx) * 1.2
        dy = (y - cy) * 0.8
        dist = math.sqrt(dx * dx + dy * dy)
        if dist < max_r * 1.15:
            # Ketidakpastian tertinggi di tepi gumpalan asap (boundary)
            edge_factor = math.sin((dist / (max_r * 1.15)) * math.pi)
            alpha = int(edge_factor * 175)
            # Warna ungu/cyan untuk ketidakpastian
            return (180, 70, 240, alpha)
        return (0, 0, 0, 0)

    with open(os.path.join(out_dir, "smoke_mask.png"), "wb") as f:
        f.write(create_png_rgba(width, height, mask_pixel))
    with open(os.path.join(out_dir, "smoke_prob.png"), "wb") as f:
        f.write(create_png_rgba(width, height, prob_pixel))
    with open(os.path.join(out_dir, "smoke_unc.png"), "wb") as f:
        f.write(create_png_rgba(width, height, unc_pixel))

def build_mock_dataset(target_data_dir, scenario="normal"):
    """
    Menghasilkan data tiruan lengkap untuk Riau dan Kalimantan Tengah.
    Mencakup semua skenario khusus: cerah, malam, awan tebal, bingkai hilang, data basi, gerak asap tak terhitung.
    Argumen scenario:
    - "normal": semua skenario ada, bingkai terbaru cerah, data segar.
    - "stale" : bingkai terbaru berumur 90 menit (melewati STALE_THRESHOLD_MINUTES);
                status.json melaporkan data basi. Riwayat lama tetap tampil.
    - "night" : bingkai terbaru berada di malam hari sehingga
                night_no_smoke_update pada status.json bernilai benar.
    Tidak ada bidang kontrak yang baru; perubahan hanya pada isi data.
    Semua keluaran tetap is_mock = True.
    """
    os.makedirs(target_data_dir, exist_ok=True)
    base_time = datetime(2026, 10, 22, 6, 0, 0, tzinfo=timezone.utc) # 13:00 WIB

    if scenario == "night":
        # 23:00 WIB: malam. Offset lama dipetakan ke offset baru agar dua
        # skenario malam menjadi paling baru dan riwayat cerah turun ke
        # pagi hari. Riwayat cerah hanya tersedia ~15 jam mundur (batas
        # matahari terbit 05:30 WIB), bukan 24 jam penuh - sudah jujur.
        base_time = datetime(2026, 10, 21, 16, 0, 0, tzinfo=timezone.utc) # 23:00 WIB
    # (penyesuaian daftar skenario dilakukan setelah daftar scenarios
    #  didefinisikan di bawah)

    regions = {
        "riau": {
            "name": "Riau",
            "bbox": [100.0, -1.1, 104.0, 2.5],
            "center": [0.7, 102.0],
            "smoke_center": [1.35, 101.8],
            "smoke_center_pct": (0.45, 0.35),
            "peat_zones": [[1.2, 101.4], [1.4, 101.9], [0.8, 102.4]]
        },
        "kalteng": {
            "name": "Kalimantan Tengah",
            "bbox": [111.0, -3.5, 115.5, 0.5],
            "center": [-1.5, 113.5],
            "smoke_center": [-2.2, 113.9],
            "smoke_center_pct": (0.64, 0.68),
            "peat_zones": [[-2.3, 114.1], [-2.0, 113.8], [-2.8, 113.5]]
        }
    }

    # Definisi 8 skenario waktu per wilayah dalam 24 jam terakhir
    scenarios = [
        {
            "offset_hours": 0.0, # 2026-10-22 06:00 UTC (13:00 WIB) - Cerah Normal Terkini
            "type": "clear_normal",
            "daylight": True,
            "cloud_cover_fraction": 0.22,
            "area_km2": 158.4,
            "has_smoke": True,
            "motion_quality": "good",
            "motion_deg": 52.0,
            "motion_speed": 14.5,
            "motion_text": "52° (Timur Laut) - 14.5 km/jam",
            "source_gap": False
        },
        {
            "offset_hours": 1.5, # 2026-10-22 04:30 UTC (11:30 WIB) - Bingkai hilang sebelumnya
            "type": "after_gap",
            "daylight": True,
            "cloud_cover_fraction": 0.35,
            "area_km2": 136.2,
            "has_smoke": True,
            "motion_quality": "moderate",
            "motion_deg": 48.0,
            "motion_speed": 12.0,
            "motion_text": "48° (Timur Laut) - 12.0 km/jam",
            "source_gap": True # Mengindikasikan frame perantara ada yang hilang
        },
        {
            "offset_hours": 3.0, # 2026-10-22 03:00 UTC (10:00 WIB) - Gerak Tak Terhitung
            "type": "uncomputable_motion",
            "daylight": True,
            "cloud_cover_fraction": 0.40,
            "area_km2": 95.0,
            "has_smoke": True,
            "motion_quality": "unavailable",
            "motion_deg": None,
            "motion_speed": None,
            "motion_text": "tidak dapat dihitung",
            "source_gap": False
        },
        {
            "offset_hours": 5.0, # 2026-10-22 01:00 UTC (08:00 WIB) - Pagi Hari Cerah Awal Terdeteksi
            "type": "morning_detect",
            "daylight": True,
            "cloud_cover_fraction": 0.28,
            "area_km2": 62.1,
            "has_smoke": True,
            "motion_quality": "poor",
            "motion_deg": 60.0,
            "motion_speed": 8.0,
            "motion_text": "60° (Timur Laut) - 8.0 km/jam (kualitas rendah)",
            "source_gap": False
        },
        {
            "offset_hours": 9.0, # 2026-10-21 21:00 UTC (04:00 WIB) - Malam Hari
            "type": "night",
            "daylight": False,
            "cloud_cover_fraction": 0.50,
            "area_km2": 0.0,
            "has_smoke": False,
            "motion_quality": "unavailable",
            "motion_deg": None,
            "motion_speed": None,
            "motion_text": "tidak dapat dihitung",
            "source_gap": False
        },
        {
            "offset_hours": 15.0, # 2026-10-21 15:00 UTC (22:00 WIB) - Malam Hari Larut
            "type": "night",
            "daylight": False,
            "cloud_cover_fraction": 0.30,
            "area_km2": 0.0,
            "has_smoke": False,
            "motion_quality": "unavailable",
            "motion_deg": None,
            "motion_speed": None,
            "motion_text": "tidak dapat dihitung",
            "source_gap": False
        },
        {
            "offset_hours": 21.0, # 2026-10-21 09:00 UTC (16:00 WIB kemarin) - Awan Tebal
            "type": "heavy_cloud",
            "daylight": True,
            "cloud_cover_fraction": 0.86, # > 0.70 pemicu awan tebal
            "area_km2": 110.8,
            "has_smoke": True,
            "motion_quality": "poor",
            "motion_deg": 40.0,
            "motion_speed": 10.0,
            "motion_text": "40° (Timur Laut) - 10.0 km/jam (terhalang awan)",
            "source_gap": False
        },
        {
            "offset_hours": 23.5, # 2026-10-21 06:30 UTC (13:30 WIB kemarin) - Siang Kemarin
            "type": "clear_yesterday",
            "daylight": True,
            "cloud_cover_fraction": 0.18,
            "area_km2": 182.0,
            "has_smoke": True,
            "motion_quality": "good",
            "motion_deg": 55.0,
            "motion_speed": 16.0,
            "motion_text": "55° (Timur Laut) - 16.0 km/jam",
            "source_gap": False
        }
    ]

    # Penyesuaian skenario terpilih: malam = dua scene malam jadi paling baru,
    # stale = buang scene terbaru
    if scenario == "night":
        NIGHT_OFFSETS = { # kunci: offset lama, isi: offset baru
            9.0: 0.0,    # night          -> 23:00 WIB (terbaru, malam)
            15.0: 1.0,   # night          -> 22:00 WIB (malam)
            21.0: 4.5,   # heavy_cloud    -> 18:30 WIB (batas senja)
            23.5: 5.5,   # clear_yesterday-> 17:30 WIB
            1.5: 9.0,    # after_gap      -> 14:00 WIB
            0.0: 11.5,   # clear_normal   -> 11:30 WIB
            3.0: 13.5,   # uncomputable   -> 09:30 WIB
            5.0: 15.0    # morning_detect -> 07:30 WIB
        }
        for s in scenarios:
            s["offset_hours"] = NIGHT_OFFSETS[s["offset_hours"]]
    elif scenario == "stale":
        # Buang bingkai terbaru (offset lama 0.0 -> alih 06:00 UTC). Bingkai
        # terakhir tersisa 04:30 UTC (11:30 WIB), diproses 04:44 UTC, dan
        # generator memandang "sekarang" = 06:14 UTC, maka usia data 90 menit
        # > STALE_THRESHOLD_MINUTES. Riwayat lebih lama tetap tampil.
        scenarios[:] = [s for s in scenarios if s["offset_hours"] > 0.0]

    for reg_id, reg_info in regions.items():
        reg_dir = os.path.join(target_data_dir, reg_id)
        os.makedirs(reg_dir, exist_ok=True)
        frame_index = []

        for scen in scenarios:
            frame_dt = base_time - timedelta(hours=scen["offset_hours"])
            ts_str = frame_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
            ts_safe = ts_str.replace(":", "-")

            overlay_dir_rel = f"overlays/{reg_id}/{ts_safe}"
            overlay_dir_abs = os.path.join(target_data_dir, overlay_dir_rel)

            # Buat file gambar overlay
            generate_smoke_images(
                overlay_dir_abs,
                has_smoke=scen["has_smoke"],
                center_pct=reg_info["smoke_center_pct"],
                radius_pct=0.22 if scen["type"] != "uncomputable_motion" else 0.14
            )

            # Menentukan source_frames (apakah ada gap / frame hilang)
            if scen["source_gap"]:
                # Mengindikasikan frame hilang dalam urutan Himawari (FR-D4)
                source_frames = [
                    (frame_dt - timedelta(minutes=40)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    # Selang 10 & 20 menit hilang
                    ts_str
                ]
            else:
                source_frames = [
                    (frame_dt - timedelta(minutes=20)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    (frame_dt - timedelta(minutes=10)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    ts_str
                ]

            # Objek SmokeFrame
            smoke_frame = {
                "timestamp_utc": ts_str,
                "processed_utc": (frame_dt + timedelta(minutes=14)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "region_id": reg_id,
                "bbox": reg_info["bbox"],
                "mask_overlay": f"/data/{overlay_dir_rel}/smoke_mask.png",
                "probability_overlay": f"/data/{overlay_dir_rel}/smoke_prob.png",
                "uncertainty_overlay": f"/data/{overlay_dir_rel}/smoke_unc.png",
                "area_km2": scen["area_km2"],
                "motion": {
                    "direction_deg": scen["motion_deg"],
                    "speed_kmh": scen["motion_speed"],
                    "quality": scen["motion_quality"],
                    "status_text": scen["motion_text"]
                },
                "source_frames": source_frames,
                "daylight": scen["daylight"],
                "cloud_cover_fraction": scen["cloud_cover_fraction"],
                "model_version": "unet_multiframe_v0.1_mock",
                "code_version": "upwind-p1-mock-2026.10",
                "is_mock": True
            }

            # Buat Hotspots
            smoke_lat, smoke_lon = reg_info["smoke_center"]
            hotspots = []
            if reg_id == "riau":
                hp_defs = [
                    {"id": f"hp_riau_{ts_safe}_01", "dlat": -0.08, "dlon": -0.15, "is_peat": True, "conf": 92, "frp": 38.5, "source": "VIIRS_NOAA20"},
                    {"id": f"hp_riau_{ts_safe}_02", "dlat": -0.14, "dlon": -0.22, "is_peat": True, "conf": 84, "frp": 22.0, "source": "VIIRS_SNPP"},
                    {"id": f"hp_riau_{ts_safe}_03", "dlat": 0.15, "dlon": 0.20, "is_peat": False, "conf": 65, "frp": 12.4, "source": "MODIS_Terra"},
                    {"id": f"hp_riau_{ts_safe}_04", "dlat": -0.30, "dlon": -0.05, "is_peat": True, "conf": 78, "frp": 19.8, "source": "VIIRS_NOAA20"},
                    {"id": f"hp_riau_{ts_safe}_05", "dlat": 0.25, "dlon": -0.30, "is_peat": False, "conf": 55, "frp": 8.2, "source": "VIIRS_SNPP"},
                ]
            else:
                hp_defs = [
                    {"id": f"hp_kt_{ts_safe}_01", "dlat": -0.10, "dlon": -0.12, "is_peat": True, "conf": 95, "frp": 54.0, "source": "VIIRS_NOAA20"},
                    {"id": f"hp_kt_{ts_safe}_02", "dlat": -0.18, "dlon": -0.18, "is_peat": True, "conf": 88, "frp": 31.5, "source": "VIIRS_SNPP"},
                    {"id": f"hp_kt_{ts_safe}_03", "dlat": -0.05, "dlon": 0.25, "is_peat": False, "conf": 60, "frp": 14.1, "source": "MODIS_Aqua"},
                    {"id": f"hp_kt_{ts_safe}_04", "dlat": -0.25, "dlon": -0.08, "is_peat": True, "conf": 82, "frp": 26.7, "source": "VIIRS_NOAA20"},
                    {"id": f"hp_kt_{ts_safe}_05", "dlat": 0.10, "dlon": -0.20, "is_peat": True, "conf": 71, "frp": 17.3, "source": "VIIRS_SNPP"},
                ]

            for h in hp_defs:
                hotspots.append({
                    "id": h["id"],
                    "time_utc": (frame_dt - timedelta(minutes=25)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "lat": round(smoke_lat + h["dlat"], 4),
                    "lon": round(smoke_lon + h["dlon"], 4),
                    "source": h["source"],
                    "confidence": h["conf"],
                    "frp": h["frp"],
                    "is_peat": h["is_peat"],
                    "is_mock": True
                })

            # Buat Sampel Angin
            wind_samples = []
            # Grid 3x3 di sekitar wilayah
            min_lon, min_lat, max_lon, max_lat = reg_info["bbox"]
            for i in range(3):
                w_lat = min_lat + (max_lat - min_lat) * (0.25 + i * 0.25)
                for j in range(3):
                    w_lon = min_lon + (max_lon - min_lon) * (0.25 + j * 0.25)
                    # Angin bertiup dari Barat Daya menuju Timur Laut (u positif, v positif)
                    u_val = 3.2 + math.sin(i + j) * 0.8
                    v_val = 2.8 + math.cos(i - j) * 0.6
                    wind_samples.append({
                        "time_utc": ts_str,
                        "lat": round(w_lat, 3),
                        "lon": round(w_lon, 3),
                        "u": round(u_val, 1),
                        "v": round(v_val, 1),
                        "height_m": 10,
                        "source": "ERA5_Land_10m_mock",
                        "is_mock": True
                    })

            # Buat Peringkat Titik Panas Hulu Asap (RankedSource)
            ranked_sources = []
            if scen["has_smoke"] and scen["motion_quality"] != "unavailable":
                # Titik 01 berada tepat di sektor hulu arah angin dan di lahan gambut
                ranked_sources.append({
                    "frame_timestamp_utc": ts_str,
                    "hotspot_id": hotspots[0]["id"],
                    "rank": 1,
                    "score": 0.94,
                    "factors": {
                        "distance_to_upwind_edge_km": 3.8,
                        "angle_difference_deg": 6.5,
                        "hotspot_confidence": hotspots[0]["confidence"] / 100.0,
                        "peat_factor": 1.2
                    },
                    "explanation": f"Sangat kuat: Berjarak 3,8 km di hulu angin (selisih sudut 6,5°) di lahan gambut berdaya api tinggi ({hotspots[0]['frp']} MW).",
                    "method_version": "heuristik_v0.1_mock",
                    "is_mock": True
                })
                ranked_sources.append({
                    "frame_timestamp_utc": ts_str,
                    "hotspot_id": hotspots[1]["id"],
                    "rank": 2,
                    "score": 0.82,
                    "factors": {
                        "distance_to_upwind_edge_km": 8.1,
                        "angle_difference_deg": 14.2,
                        "hotspot_confidence": hotspots[1]["confidence"] / 100.0,
                        "peat_factor": 1.2
                    },
                    "explanation": f"Kandidat sekunder: 8,1 km di sektor hulu di lahan gambut dengan kepercayaan {hotspots[1]['confidence']}%.",
                    "method_version": "heuristik_v0.1_mock",
                    "is_mock": True
                })
                ranked_sources.append({
                    "frame_timestamp_utc": ts_str,
                    "hotspot_id": hotspots[3]["id"],
                    "rank": 3,
                    "score": 0.65,
                    "factors": {
                        "distance_to_upwind_edge_km": 14.5,
                        "angle_difference_deg": 28.0,
                        "hotspot_confidence": hotspots[3]["confidence"] / 100.0,
                        "peat_factor": 1.2
                    },
                    "explanation": f"Kemungkinan lebih rendah: Berjarak 14,5 km dari batas hulu asap dengan deviasi sudut 28°.",
                    "method_version": "heuristik_v0.1_mock",
                    "is_mock": True
                })
                ranked_sources.append({
                    "frame_timestamp_utc": ts_str,
                    "hotspot_id": hotspots[2]["id"],
                    "rank": 4,
                    "score": 0.31,
                    "factors": {
                        "distance_to_upwind_edge_km": 21.0,
                        "angle_difference_deg": 165.0, # Berada di hilir, bukan hulu
                        "hotspot_confidence": hotspots[2]["confidence"] / 100.0,
                        "peat_factor": 1.0
                    },
                    "explanation": "Kemungkinan kecil: Posisi berada di hilir arah gerak asap dan bukan lahan gambut.",
                    "method_version": "heuristik_v0.1_mock",
                    "is_mock": True
                })
            elif scen["motion_quality"] == "unavailable":
                # Bila gerak asap tidak dapat dihitung
                for idx, hp in enumerate(hotspots[:3]):
                    ranked_sources.append({
                        "frame_timestamp_utc": ts_str,
                        "hotspot_id": hp["id"],
                        "rank": idx + 1,
                        "score": 0.50 - idx * 0.1,
                        "factors": {
                            "distance_to_upwind_edge_km": None,
                            "angle_difference_deg": None,
                            "hotspot_confidence": hp["confidence"] / 100.0,
                            "peat_factor": 1.2 if hp["is_peat"] else 1.0
                        },
                        "explanation": "Peringkat heuristik darurat: Gerak asap tidak dapat dihitung, estimasi hanya berdasarkan kedekatan pusat dan daya FRP.",
                        "method_version": "heuristik_v0.1_mock",
                        "is_mock": True
                    })

            # Bundel lengkap per frame
            bundle = {
                "frame": smoke_frame,
                "hotspots": hotspots,
                "wind": wind_samples,
                "ranked_sources": ranked_sources
            }

            frame_file_path = os.path.join(reg_dir, f"{ts_safe}.json")
            with open(frame_file_path, "w", encoding="utf-8") as f:
                json.dump(bundle, f, indent=2, ensure_ascii=False)

            frame_index.append({
                "timestamp_utc": ts_str,
                "timestamp_safe": ts_safe,
                "daylight": scen["daylight"],
                "cloud_cover_fraction": scen["cloud_cover_fraction"],
                "area_km2": scen["area_km2"],
                "has_smoke": scen["has_smoke"],
                "motion_quality": scen["motion_quality"],
                "scenario_type": scen["type"]
            })

        # Urutkan indeks secara kronologis (dari terlama ke terbaru)
        frame_index.sort(key=lambda x: x["timestamp_utc"])
        index_file_path = os.path.join(reg_dir, "index.json")
        with open(index_file_path, "w", encoding="utf-8") as f:
            json.dump(frame_index, f, indent=2, ensure_ascii=False)

    # Status Sistem Global, menurut skenario terpilih (tanpa bidang kontrak baru)
    if scenario == "stale":
        system_status = {
            "last_processed_utc": "2026-10-22T04:44:00Z",
            "latest_frame_utc": "2026-10-22T04:30:00Z",
            "data_age_minutes": 90, # >= STALE_THRESHOLD_MINUTES (60); "sekarang" generator = 06:14 UTC
            "sources_status": {
                "himawari": "ok",
                "hotspot": "ok",
                "wind": "ok"
            },
            "night_no_smoke_update": False,
            "cloud_cover_high": False,
            "is_mock": True,
            "note": "DATA CONTOH TIRUAN: skenario data basi (usia 90 menit, ambang %d menit)" % STALE_THRESHOLD_MINUTES
        }
    elif scenario == "night":
        system_status = {
            "last_processed_utc": (base_time + timedelta(minutes=14)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "latest_frame_utc": base_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "data_age_minutes": 24,
            "sources_status": {
                "himawari": "ok",
                "hotspot": "ok",
                "wind": "ok"
            },
            "night_no_smoke_update": True,
            "cloud_cover_high": False,
            "is_mock": True,
            "note": "DATA CONTOH TIRUAN: bingkai terbaru malam hari (23:00 WIB), tidak ada pembaruan asap"
        }
    else:
        system_status = {
            "last_processed_utc": (base_time + timedelta(minutes=14)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "latest_frame_utc": base_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "data_age_minutes": 24, # Masih dalam rentang aman normal < STALE_THRESHOLD_MINUTES
            "sources_status": {
                "himawari": "ok",
                "hotspot": "ok",
                "wind": "ok"
            },
            "night_no_smoke_update": False,
            "cloud_cover_high": False,
            "is_mock": True,
            "note": "DATA CONTOH TIRUAN untuk verifikasi FR-W dasbor Upwind"
        }
    with open(os.path.join(target_data_dir, "status.json"), "w", encoding="utf-8") as f:
        json.dump(system_status, f, indent=2, ensure_ascii=False)

    print(f"Berhasil menghasilkan data tiruan lengkap di {target_data_dir}")

if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..", "data")
    # Argumen kedua: skenario (normal | stale | night), bawaan normal
    scen = "normal"
    for a in sys.argv[2:]:
        if a in ("normal", "stale", "night"):
            scen = a
    build_mock_dataset(os.path.abspath(out), scenario=scen)
