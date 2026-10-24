# -*- coding: utf-8 -*-
"""
Modul Pengambilan Titik Panas NASA FIRMS (VIIRS / MODIS).
Sesuai ARSITEKTUR.md Bagian 3 dan docs/KONTRAK_DATA.md.
JANGAN PERNAH mengekspos API key ke log atau keluaran konsol.
"""

import os
import sys
import csv
import io
import urllib.request
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import get_firms_map_key, DATA_ROOT

# Bounding box wilayah [min_lon, min_lat, max_lon, max_lat]
BBOX_AREAS = {
    "riau": "100.0,-1.1,104.0,2.5",
    "kalteng": "111.0,-3.5,116.0,0.8"
}

def unduh_hotspot_firms(region_id, date_str, source=None, days=1, out_dir=None):
    """
    Mengunduh titik panas dari NASA FIRMS API dan mengonversi ke format kontrak data Hotspot.
    date_str: 'YYYY-MM-DD'
    source: jika None, otomatis memilih VIIRS_SNPP_SP untuk data lama (<2025) atau VIIRS_SNPP_NRT untuk data baru.
    """
    key = get_firms_map_key()
    if not key:
        raise ValueError("FIRMS_MAP_KEY tidak ditemukan di environment / .env")
        
    area = BBOX_AREAS.get(region_id)
    if not area:
        raise ValueError(f"Wilayah tidak dikenal: {region_id}")
        
    # Deteksi arsip (Standard Processing) vs NRT (Near-Real-Time)
    thn = int(date_str.split("-")[0])
    if source is None:
        source = "VIIRS_SNPP_SP" if thn < 2025 else "VIIRS_SNPP_NRT"
        
    url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{key}/{source}/{area}/{days}/{date_str}"
    req = urllib.request.Request(url, headers={"User-Agent": "Upwind/0.1"})
    
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            text = resp.read().decode("utf-8")
    except Exception as e:
        # Sanitasi pesan error agar key tidak bocor
        sanitized = str(e).replace(key, "***KEY***")
        raise RuntimeError(f"Gagal mengunduh data FIRMS: {sanitized}")
        
    reader = csv.DictReader(io.StringIO(text))
    rows = list(reader)
    
    hotspots = []
    for idx, r in enumerate(rows):
        acq_date = r.get("acq_date", date_str)
        acq_time = r.get("acq_time", "0000").zfill(4)
        hh, mm = acq_time[:2], acq_time[2:]
        time_utc = f"{acq_date}T{hh}:{mm}:00Z"
        # Normalisasi nama satelit ('N' = Suomi-NPP di VIIRS NRT)
        sat_code = r.get("satellite", "SNPP")
        sat_name = "SNPP" if sat_code in ("N", "SNPP") else sat_code
        
        # Normalisasi confidence (VIIRS NRT: 'l', 'n', 'h')
        raw_conf = r.get("confidence", "nominal")
        conf_map = {"l": "low", "n": "nominal", "h": "high"}
        conf = conf_map.get(raw_conf.lower(), raw_conf)
        
        hp = {
            "id": f"hp_{region_id}_{sat_name}_{acq_date.replace('-', '')}_{acq_time}_{idx:04d}",
            "time_utc": time_utc,
            "lat": round(float(r["latitude"]), 5),
            "lon": round(float(r["longitude"]), 5),
            "source": f"NASA_FIRMS_{source}",
            "confidence": conf,
            "frp": float(r.get("frp", 0.0) or 0.0),
            "is_peat": False,
            "is_mock": False
        }
        hotspots.append(hp)
        
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
        out_file = os.path.join(out_dir, f"hotspot_{region_id}_{date_str}.json")
        with open(out_file, "w", encoding="utf-8") as f:
            import json
            json.dump(hotspots, f, indent=2, ensure_ascii=False)
            
    return hotspots

if __name__ == "__main__":
    for reg in ("riau", "kalteng"):
        hps_19 = unduh_hotspot_firms(reg, "2019-09-14")
        print(f"[{reg}] 2019-09-14: {len(hps_19)} titik panas")
        hps_26 = unduh_hotspot_firms(reg, "2026-10-23")
        print(f"[{reg}] 2026-10-23: {len(hps_26)} titik panas")
