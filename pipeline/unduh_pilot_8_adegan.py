# -*- coding: utf-8 -*-
"""
Skrip Perencanaan & Unduhan Bertingkat untuk 8 Adegan Pilot Himawari.
Sesuai PRD.md P2 dan arahan efisiensi data:
- Bingkai Kunci (t0): Band lengkap (B01-B04, B07, B13) untuk komposit warna & anotasi ground-truth.
- Bingkai Konteks (t-10m, t-20m, t-30m / t-40m bila maintenance 02:40): Band ringkas (B03, B04, B13).
- Resume didukung menggunakan curl -C -.
"""
import os
import sys
import subprocess
from config import DATA_ROOT

# Definisi 8 Adegan Pilot
# Catatan: Pada jam 02:40 UTC, Himawari melakukan housekeeping rutin harian (file tidak tersedia).
# Maka konteks 3-bingkai sebelum 03:00 UTC menggunakan: 02:20, 02:30, 02:50 UTC.
PILOT_SCENES = [
    # 1. Puncak asap Kalimantan & Sumatra (Training)
    {
        "id": "asap_2019-09-14",
        "sat": "noaa-himawari8",
        "date": "2019/09/14",
        "key_time": "0300",
        "context_times": ["0220", "0230", "0250"]
    },
    # 2. Eskalasi kebakaran awal Riau/Kalteng (Training)
    {
        "id": "asap_2019-09-12",
        "sat": "noaa-himawari8",
        "date": "2019/09/12",
        "key_time": "0300",
        "context_times": ["0220", "0230", "0250"]
    },
    # 3. Variasi siang/sore 13:00 WIB (Training)
    {
        "id": "asap_2019-09-14_0600",
        "sat": "noaa-himawari8",
        "date": "2019/09/14",
        "key_time": "0600",
        "context_times": ["0530", "0540", "0550"]
    },
    # 4. Kontrol bersih pasca-hujan (Training)
    {
        "id": "bersih_2019-10-15",
        "sat": "noaa-himawari8",
        "date": "2019/10/15",
        "key_time": "0300",
        "context_times": ["0220", "0230", "0250"]
    },
    # 5. Kontrol awan tebal musim hujan (Training)
    {
        "id": "awan_2019-01-15",
        "sat": "noaa-himawari8",
        "date": "2019/01/15",
        "key_time": "0300",
        "context_times": ["0220", "0230", "0250"]
    },
    # 6. Awal kemunculan kabut asap (Test / Baseline)
    {
        "id": "asap_2019-09-05",
        "sat": "noaa-himawari8",
        "date": "2019/09/05",
        "key_time": "0300",
        "context_times": ["0220", "0230", "0250"]
    },
    # 7. Uji temporal tracking (Test / Baseline)
    {
        "id": "asap_2019-09-14_0400",
        "sat": "noaa-himawari8",
        "date": "2019/09/14",
        "key_time": "0400",
        "context_times": ["0330", "0340", "0350"]
    },
    # 8. Himawari-9 terkini (Test / In-Situ)
    {
        "id": "terkini_2026-10-23",
        "sat": "noaa-himawari9",
        "date": "2026/10/23",
        "key_time": "0300",
        "context_times": ["0220", "0230", "0250"]
    }
]

def buat_daftar_unduhan():
    items = []
    for sc in PILOT_SCENES:
        sat = sc["sat"]
        date_slash = sc["date"]
        date_clean = date_slash.replace("/", "")
        scene_id = sc["id"]
        out_dir = os.path.join(DATA_ROOT, sat, scene_id)
        
        is_h9 = (sat == "noaa-himawari9")
        
        # 1. Key frame (B01-B04, B07, B13)
        kt = sc["key_time"]
        pfx_k = f"AHI-L1b-FLDK/{date_slash}/{kt}/"
        if not is_h9:
            # H8: FLDK penuh 1 berkas per band
            bands_key = [
                ("B01", "R10", "S0101"),
                ("B02", "R10", "S0101"),
                ("B03", "R10", "S0101"),
                ("B04", "R20", "S0101"),
                ("B07", "R20", "S0101"),
                ("B13", "R20", "S0101")
            ]
            for b, r, s in bands_key:
                fn = f"HS_H08_{date_clean}_{kt}_{b}_FLDK_{r}_{s}.DAT.bz2"
                url = f"https://{sat}.s3.amazonaws.com/{pfx_k}{fn}"
                items.append((url, os.path.join(out_dir, fn), b, True))
        else:
            # H9: S05 dan S06 (Sumatra & Kalimantan)
            # B03 hanya ada R05
            bands_key = [
                ("B01", "R10"),
                ("B02", "R10"),
                ("B03", "R05"),
                ("B04", "R10"),
                ("B07", "R20"),
                ("B13", "R20")
            ]
            for b, r in bands_key:
                for s in ("S0510", "S0610"):
                    fn = f"HS_H09_{date_clean}_{kt}_{b}_FLDK_{r}_{s}.DAT.bz2"
                    url = f"https://{sat}.s3.amazonaws.com/{pfx_k}{fn}"
                    items.append((url, os.path.join(out_dir, fn), b, True))
                    
        # 2. Context frames (B03, B04, B13)
        for ct in sc["context_times"]:
            pfx_c = f"AHI-L1b-FLDK/{date_slash}/{ct}/"
            if not is_h9:
                bands_ctx = [
                    ("B03", "R20", "S0101"),
                    ("B04", "R20", "S0101"),
                    ("B13", "R20", "S0101")
                ]
                for b, r, s in bands_ctx:
                    fn = f"HS_H08_{date_clean}_{ct}_{b}_FLDK_{r}_{s}.DAT.bz2"
                    url = f"https://{sat}.s3.amazonaws.com/{pfx_c}{fn}"
                    items.append((url, os.path.join(out_dir, fn), b, False))
            else:
                bands_ctx = [
                    ("B03", "R05"),
                    ("B04", "R10"),
                    ("B13", "R20")
                ]
                for b, r in bands_ctx:
                    for s in ("S0510", "S0610"):
                        fn = f"HS_H09_{date_clean}_{ct}_{b}_FLDK_{r}_{s}.DAT.bz2"
                        url = f"https://{sat}.s3.amazonaws.com/{pfx_c}{fn}"
                        items.append((url, os.path.join(out_dir, fn), b, False))
    return items

def unduh_semua(dry_run=False):
    items = buat_daftar_unduhan()
    print(f"Total berkas yang direncanakan: {len(items)}")
    
    sudah_ada = 0
    belum_ada = []
    for url, dest, b, is_key in items:
        if os.path.exists(dest) and os.path.getsize(dest) > 1000:
            sudah_ada += 1
        else:
            belum_ada.append((url, dest))
            
    print(f"Sudah ada di disk: {sudah_ada} berkas")
    print(f"Perlu diunduh: {len(belum_ada)} berkas")
    
    if dry_run:
        return
        
    for idx, (url, dest) in enumerate(belum_ada):
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        print(f"[{idx+1}/{len(belum_ada)}] Mengunduh: {os.path.basename(dest)}")
        cmd = ["curl", "-s", "-f", "-C", "-", "-o", dest, url]
        res = subprocess.run(cmd)
        if res.returncode != 0:
            print(f"  PERINGATAN: curl returncode {res.returncode} untuk {url}")

if __name__ == "__main__":
    is_dry = "--run" not in sys.argv
    unduh_semua(dry_run=is_dry)
