# -*- coding: utf-8 -*-
"""
Skrip Perencanaan & Unduhan Bertingkat untuk 8 Adegan Pilot Himawari.
Sesuai PRD.md P2 dan arahan efisiensi data (Pilihan A):
- Per adegan: 1 Bingkai Kunci (t0) band lengkap (B01-B04, B07, B13) untuk anotasi & komposit warna.
- Per adegan: 3 Bingkai Konteks band ringkas (B03, B04, B13).
- B03 Himawari-9 tetap R05 (0,5 km).
- Jadwal 02:40 UTC adalah jendela housekeeping JMA (HTTP 404), konteks disesuaikan ke 02:20, 02:30, 02:50 UTC.
- Aturan unduhan:
  1. Satu pemanggilan curl per berkas.
  2. Resume didukung dengan flag -C -.
  3. 4 koneksi paralel (ThreadPoolExecutor).
  4. Pencatatan log ke D:\\upwind_data\\unduh.log.
  5. Verifikasi ukuran akhir berkas terhadap Content-Length dari HTTP HEAD.
  6. Berkas lengkap tidak diunduh ulang dan tidak dihapus.
  7. Berkas gagal verifikasi dilaporkan (bukan dihapus diam-diam).
"""

import os
import sys
import json
import time
import subprocess
import urllib.request
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor
import threading

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import DATA_ROOT

MAX_PARALEL = 4
LOG_PATH = os.path.join(DATA_ROOT, "unduh.log")
CACHE_HEAD_PATH = os.path.join(DATA_ROOT, "pilot_head_cache.json")
log_lock = threading.Lock()

# 8 Adegan Pilot
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
    # 7. Uji temporal tracking 1 jam pasca frame kunci (Test / Baseline)
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

def catat_log(pesan, juga_ke_layar=True):
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    baris = f"[{now_str}] {pesan}"
    if juga_ke_layar:
        print(baris, flush=True)
    with log_lock:
        try:
            os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
            with open(LOG_PATH, "a", encoding="utf-8") as f:
                f.write(baris + "\n")
        except Exception as e:
            if juga_ke_layar:
                print(f"  (Gagal menulis ke unduh.log: {e})", flush=True)

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
                items.append({
                    "scene_id": scene_id,
                    "url": url,
                    "dest": os.path.join(out_dir, fn),
                    "filename": fn,
                    "band": b,
                    "is_key": True,
                    "time_str": kt
                })
        else:
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
                    items.append({
                        "scene_id": scene_id,
                        "url": url,
                        "dest": os.path.join(out_dir, fn),
                        "filename": fn,
                        "band": b,
                        "is_key": True,
                        "time_str": kt
                    })
                    
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
                    items.append({
                        "scene_id": scene_id,
                        "url": url,
                        "dest": os.path.join(out_dir, fn),
                        "filename": fn,
                        "band": b,
                        "is_key": False,
                        "time_str": ct
                    })
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
                        items.append({
                            "scene_id": scene_id,
                            "url": url,
                            "dest": os.path.join(out_dir, fn),
                            "filename": fn,
                            "band": b,
                            "is_key": False,
                            "time_str": ct
                        })
    return items

def ambil_ukuran_server_head(url):
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "Upwind/0.1"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            sz = resp.headers.get("Content-Length")
            return int(sz) if sz else None
    except Exception as e:
        return None

def muat_atau_ambil_cache_head(items):
    cache = {}
    if os.path.exists(CACHE_HEAD_PATH):
        try:
            with open(CACHE_HEAD_PATH, "r", encoding="utf-8") as f:
                cache = json.load(f)
        except Exception:
            cache = {}
            
    belum_ada_head = [it["url"] for it in items if it["url"] not in cache or cache[it["url"]] is None]
    if belum_ada_head:
        print(f"Mengambil metadata Content-Length (HEAD) untuk {len(belum_ada_head)} berkas...", flush=True)
        def query_head(u):
            return u, ambil_ukuran_server_head(u)
        with ThreadPoolExecutor(max_workers=8) as ex:
            for u, sz in ex.map(query_head, belum_ada_head):
                cache[u] = sz
        try:
            with open(CACHE_HEAD_PATH, "w", encoding="utf-8") as f:
                json.dump(cache, f, indent=2)
        except Exception:
            pass
    return cache

def unduh_dan_verifikasi_satu(item, server_size, index, total):
    url = item["url"]
    dest = item["dest"]
    fn = item["filename"]
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    
    local_before = os.path.getsize(dest) if os.path.exists(dest) else 0
    if server_size and local_before == server_size:
        catat_log(f"[{index}/{total}] SUDAH_LENGKAP: {fn} ({local_before / 1e6:.1f} MB)")
        return "SUDAH_LENGKAP", fn, 0, local_before
        
    resume_flag = f"(resume dari {local_before / 1e6:.1f} MB)" if local_before > 0 else "(unduh baru)"
    catat_log(f"[{index}/{total}] MULAI: {fn} {resume_flag}")
    
    # Satu pemanggilan curl dengan resume -C -
    cmd = ["curl", "-s", "-f", "-C", "-", "-o", dest, url]
    t0 = time.time()
    res = subprocess.run(cmd)
    durasi = time.time() - t0
    rc = res.returncode
    
    local_after = os.path.getsize(dest) if os.path.exists(dest) else 0
    
    if rc != 0:
        catat_log(f"[{index}/{total}] GAGAL_CURL: {fn} returncode={rc} setelah {durasi:.1f}s")
        return "GAGAL_CURL", fn, rc, local_after
        
    if server_size is not None:
        if local_after == server_size:
            catat_log(f"[{index}/{total}] VERIFIKASI_OK: {fn} ({local_after / 1e6:.1f} MB) dalam {durasi:.1f}s")
            return "VERIFIKASI_OK", fn, 0, local_after
        else:
            selisih = server_size - local_after
            catat_log(f"[{index}/{total}] PERINGATAN_GAGAL_VERIFIKASI: {fn} lokal={local_after} server={server_size} selisih={selisih} bytes")
            return "GAGAL_VERIFIKASI", fn, rc, local_after
    else:
        catat_log(f"[{index}/{total}] UNDUH_SELESAI_TANPA_HEAD: {fn} ({local_after / 1e6:.1f} MB)")
        return "SELESAI_NO_HEAD", fn, 0, local_after

def jalankan_unduhan():
    catat_log("=== MEMULAI SESI UNDUHAN 8 ADEGAN PILOT ===")
    items = buat_daftar_unduhan()
    head_cache = muat_atau_ambil_cache_head(items)
    
    antrean = []
    lengkap = 0
    bytes_lengkap = 0
    
    for it in items:
        u = it["url"]
        dest = it["dest"]
        sz = head_cache.get(u)
        local_sz = os.path.getsize(dest) if os.path.exists(dest) else 0
        if sz and local_sz == sz:
            lengkap += 1
            bytes_lengkap += local_sz
        else:
            antrean.append((it, sz))
            
    catat_log(f"Total berkas: {len(items)} ({sum(head_cache.values()) / 1e9:.2f} GB)")
    catat_log(f"Sudah lengkap di disk: {lengkap} berkas ({bytes_lengkap / 1e9:.2f} GB)")
    catat_log(f"Antrean yang akan diunduh/resume: {len(antrean)} berkas")
    
    if not antrean:
        catat_log("Semua berkas telah lengkap dan terverifikasi!")
        return
        
    selesai_hitung = 0
    total_antrean = len(antrean)
    
    def worker(job):
        idx, (it, s_sz) = job
        return unduh_dan_verifikasi_satu(it, s_sz, idx + 1, total_antrean)
        
    pekerjaan = list(enumerate(antrean))
    with ThreadPoolExecutor(max_workers=MAX_PARALEL) as ex:
        for status, fn, rc, l_sz in ex.map(worker, pekerjaan):
            selesai_hitung += 1
            
    catat_log(f"=== SESI UNDUHAN SELESAI ({selesai_hitung}/{total_antrean} berkas diproses) ===")

def mode_simulasi():
    items = buat_daftar_unduhan()
    head_cache = muat_atau_ambil_cache_head(items)
    
    lengkap_list = []
    parsial_list = []
    belum_list = []
    lebih_list = []
    
    total_server_bytes = 0
    total_local_bytes = 0
    
    for it in items:
        u = it["url"]
        dest = it["dest"]
        fn = it["filename"]
        sz = head_cache.get(u)
        if sz:
            total_server_bytes += sz
            
        if os.path.exists(dest):
            l_sz = os.path.getsize(dest)
            total_local_bytes += l_sz
            if sz is not None:
                if l_sz == sz:
                    lengkap_list.append((fn, l_sz, sz))
                elif l_sz < sz:
                    parsial_list.append((fn, l_sz, sz))
                else:
                    lebih_list.append((fn, l_sz, sz))
            else:
                lengkap_list.append((fn, l_sz, l_sz))
        else:
            belum_list.append((fn, 0, sz or 0))
            
    print("\n" + "=" * 70)
    print("HASIL SIMULASI PERENCANAAN UNDUHAN 8 ADEGAN PILOT (PILIHAN A)")
    print("=" * 70)
    print(f"Total berkas yang direncanakan : {len(items)} berkas")
    print(f"Total ukuran server (Content-L) : {total_server_bytes / 1e9:.2f} GB ({total_server_bytes:,} bytes)")
    print(f"Total tersimpan di disk lokal   : {total_local_bytes / 1e9:.2f} GB ({total_local_bytes:,} bytes)")
    print("-" * 70)
    print(f"1. Berkas Lengkap & Terverifikasi: {len(lengkap_list):3d} berkas ({sum(x[1] for x in lengkap_list) / 1e9:.2f} GB)")
    print(f"2. Berkas Parsial (akan di-resume): {len(parsial_list):3d} berkas (lokal {sum(x[1] for x in parsial_list) / 1e6:.1f} MB dari {sum(x[2] for x in parsial_list) / 1e6:.1f} MB)")
    print(f"3. Berkas Belum Ada (unduh baru) : {len(belum_list):3d} berkas ({sum(x[2] for x in belum_list) / 1e9:.2f} GB)")
    if lebih_list:
        print(f"4. Berkas Melebihi Ukuran Server: {len(lebih_list):3d} berkas")
    print("-" * 70)
    
    sisa_bytes = total_server_bytes - total_local_bytes
    est_detik = sisa_bytes / (540 * 1024)
    print(f"Sisa bytes yang perlu diunduh   : {sisa_bytes / 1e9:.2f} GB ({sisa_bytes:,} bytes)")
    print(f"Estimasi waktu unduh (~540 KB/s): {est_detik / 60:.1f} menit ({est_detik / 3600:.2f} jam)")
    print(f"Log akan disimpan di            : {LOG_PATH}")
    print("=" * 70 + "\n")
    
    if parsial_list:
        print("Daftar Berkas Parsial yang Memerlukan Resume:")
        for fn, l_sz, sz in parsial_list:
            print(f"  - {fn}: lokal {l_sz / 1e6:.2f} MB / server {sz / 1e6:.2f} MB (sisa {(sz - l_sz) / 1e6:.2f} MB)")
        print()

if __name__ == "__main__":
    if "--run" in sys.argv:
        jalankan_unduhan()
    else:
        mode_simulasi()
