# -*- coding: utf-8 -*-
"""
Skrip Pengambilan dan Analisis Hari Kandidat Asap Karhutla (P3b).
Menggunakan FIRMS VIIRS (S-NPP dan NOAA-20) untuk wilayah Riau dan Kalteng.
Hasil disimpan ke cache lokal di D:\\upwind_data\\firms_cache\\ agar tidak mengulang panggilan API.
JANGAN PERNAH mencetak atau mengekspos MAP_KEY.
"""

import os
import sys
import csv
import io
import time
import urllib.request
from collections import defaultdict, Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import get_firms_map_key, DATA_ROOT
from unduh_hotspot_firms import BBOX_AREAS

CACHE_DIR = os.path.join(DATA_ROOT, "firms_cache")
os.makedirs(CACHE_DIR, exist_ok=True)

def fetch_firms_cached(region, source, date_str, days=5):
    """
    Mengunduh data FIRMS dengan caching lokal.
    Jika berkas cache sudah ada, langsung baca dari disk.
    """
    cache_file = os.path.join(CACHE_DIR, f"{region}_{source}_{date_str}_{days}d.csv")
    if os.path.exists(cache_file):
        with open(cache_file, "r", encoding="utf-8") as f:
            text = f.read()
    else:
        key = get_firms_map_key()
        if not key:
            raise ValueError("MAP_KEY tidak ditemukan")
        area = BBOX_AREAS[region]
        url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{key}/{source}/{area}/{days}/{date_str}"
        req = urllib.request.Request(url, headers={"User-Agent": "Upwind/0.1"})
        print(f"Mengunduh FIRMS: {region} {source} {date_str} ({days} hari)...")
        with urllib.request.urlopen(req, timeout=120) as resp:
            text = resp.read().decode("utf-8")
        with open(cache_file, "w", encoding="utf-8") as f:
            f.write(text)
        time.sleep(1.0) # Jeda sopan antar-panggilan API
        
    reader = csv.DictReader(io.StringIO(text))
    rows = list(reader)
    return rows

def main():
    # Daftar jendela waktu yang diperiksa
    # 2019: Agustus (Riau), September-Oktober (Kalteng & Riau), Januari (musim hujan)
    # 2023: September-Oktober (Kalteng & Riau, H9)
    # 2015: September-Oktober (Kalteng & Riau, H8)
    
    windows = [
        # (region, source, date_str, days)
        # 2019 Riau & Kalteng
        ("riau", "VIIRS_SNPP_SP", "2019-08-08", 5),
        ("riau", "VIIRS_SNPP_SP", "2019-08-20", 5),
        ("riau", "VIIRS_SNPP_SP", "2019-09-12", 5),
        ("riau", "VIIRS_SNPP_SP", "2019-10-14", 5),
        ("riau", "VIIRS_SNPP_SP", "2019-01-14", 5),
        ("kalteng", "VIIRS_SNPP_SP", "2019-08-10", 5),
        ("kalteng", "VIIRS_SNPP_SP", "2019-09-04", 5),
        ("kalteng", "VIIRS_SNPP_SP", "2019-09-12", 5),
        ("kalteng", "VIIRS_SNPP_SP", "2019-09-22", 5),
        ("kalteng", "VIIRS_SNPP_SP", "2019-10-01", 5),
        ("kalteng", "VIIRS_SNPP_SP", "2019-10-14", 5),
        ("kalteng", "VIIRS_SNPP_SP", "2019-01-14", 5),
        
        # 2023 Kalteng (El Nino 2023, H9)
        ("kalteng", "VIIRS_SNPP_SP", "2023-09-28", 5),
        ("kalteng", "VIIRS_SNPP_SP", "2023-10-03", 5),
        
        # 2015 Kalteng (Puncak El Nino 2015, H8)
        ("kalteng", "VIIRS_SNPP_SP", "2015-09-22", 5),
        ("kalteng", "VIIRS_SNPP_SP", "2015-10-14", 5),
    ]
    
    counts_by_date_region = defaultdict(lambda: Counter())
    
    for reg, src, dt, d in windows:
        try:
            rows = fetch_firms_cached(reg, src, dt, days=d)
            for r in rows:
                acq_d = r.get("acq_date")
                if acq_d:
                    counts_by_date_region[reg][acq_d] += 1
        except Exception as e:
            print(f"Error {reg} {dt}: {e}")
            
    print("\n" + "=" * 60)
    print("RINGKASAN TITIK PANAS PER HARI (HASIL CACHE FIRMS)")
    print("=" * 60)
    
    for reg in ("riau", "kalteng"):
        print(f"\n--- Wilayah: {reg.upper()} ---")
        for dt in sorted(counts_by_date_region[reg]):
            cnt = counts_by_date_region[reg][dt]
            print(f"  {dt}: {cnt:5d} titik panas")
            
if __name__ == "__main__":
    main()
