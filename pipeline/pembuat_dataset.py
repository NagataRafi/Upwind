# -*- coding: utf-8 -*-
"""
Modul Pembuat Dataset Tanpa Label (P3a) untuk Model Segmentasi Asap Himawari.
Sesuai PRD.md P3a dan kebijakan grid di Changelog.md:
1. Resampling semua band ke grid bersama 1 km (0.01 derajat):
   - Band kasar 2 km (R20): Bilinear
   - Band halus 0.5 km (R05, B03 Himawari-9): Area-averaging (BOX)
   - Band 1 km (R10): Bilinear
2. Tumpukan 15 kanal fitur satelit:
   - t0 (6 band): B01 (Biru), B02 (Hijau), B03 (Merah), B04 (NIR), B07 (SWIR/TB), B13 (TIR/TB)
   - t-10m (3 band): B03, B04, B13
   - t-30m (3 band): B03, B04, B13
   - t-40m (3 band): B03, B04, B13
3. Penanda tambahan:
   - Topeng awan dingin (TB13 < 265 K pada t0)
   - Penanda siang/malam (daylight)
   - Fraksi awan dingin per potongan
4. Pemotongan ke ukuran 256x256 untuk kotak Riau dan Kalimantan Tengah.
5. Tersimpan di D:\\upwind_data\\dataset_p3a\\ sebagai berkas .npz berkecepatan tinggi.
"""

import os
import sys
import re
import math
import json
import time
import numpy as np
from PIL import Image
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import DATA_ROOT
from unduh_pilot_8_adegan import PILOT_SCENES
from olah_himawari_fm1 import baca_hsd, tb_ir, selip, potong_lalo

DATASET_DIR = os.path.join(DATA_ROOT, "dataset_p3a")

# Definisi kotak dan ukuran grid bersama 1 km (0.01 derajat per piksel)
KOTAK_GRID = {
    "kalteng": {
        "bbox": (-0.2, -4.8, 109.8, 116.2), # latN, latS, lonW, lonE (4.6 deg x 6.4 deg)
        "grid_shape": (460, 640),            # (H, W) pada 0.01 deg/px (~1 km)
        "slices": [
            # 2 baris x 3 kolom = 6 potongan 256x256 mencakup seluruh wilayah
            (0, 256, 0, 256),
            (0, 256, 192, 448),
            (0, 256, 384, 640),
            (204, 460, 0, 256),
            (204, 460, 192, 448),
            (204, 460, 384, 640),
        ]
    },
    "riau": {
        "bbox": (2.4, -2.6, 97.5, 106.5),   # latN, latS, lonW, lonE (5.0 deg x 9.0 deg)
        "grid_shape": (500, 900),            # (H, W) pada 0.01 deg/px (~1 km)
        "slices": [
            # 2 baris x 4 kolom = 8 potongan 256x256 mencakup seluruh wilayah
            (0, 256, 0, 256),
            (0, 256, 214, 470),
            (0, 256, 428, 684),
            (0, 256, 644, 900),
            (244, 500, 0, 256),
            (244, 500, 214, 470),
            (244, 500, 428, 684),
            (244, 500, 644, 900),
        ]
    }
}

KANAL_DESKRIPSI = [
    "t0_B01_albedo",
    "t0_B02_albedo",
    "t0_B03_albedo",
    "t0_B04_albedo",
    "t0_B07_TB_kelvin",
    "t0_B13_TB_kelvin",
    "tm10_B03_albedo",
    "tm10_B04_albedo",
    "tm10_B13_TB_kelvin",
    "tm30_B03_albedo",
    "tm30_B04_albedo",
    "tm30_B13_TB_kelvin",
    "tm40_B03_albedo",
    "tm40_B04_albedo",
    "tm40_B13_TB_kelvin",
]

def muat_satu_berkas_band(arg):
    folder, time_str, band = arg
    pola = rf"_B{band:02d}_FLDK_[RR]\d\d_S\d+\.DAT\.bz2$"
    paths = [
        os.path.join(folder, f) for f in os.listdir(folder)
        if re.search(pola, f) and f"_{time_str}_" in f
    ]
    if not paths:
        return (time_str, band, None, None, None)
        
    byres = {}
    for p in paths:
        m = re.search(rf"_B{band:02d}_FLDK_(R\d\d)_S\d+\.DAT\.bz2$", p)
        if m:
            byres.setdefault(m.group(1), []).append(p)
    if not byres:
        return (time_str, band, None, None, None)
        
    # Pilih resolusi terbanyak (misal R05/R10)
    res = max(byres, key=lambda r: len(byres[r]))
    paths = byres[res]
    
    infos, tiles = [], []
    for p in paths:
        i, a = baca_hsd(p)
        infos.append(i)
        tiles.append((int(i["seg_first_line"] or 0), a))
    tiles.sort(key=lambda t: t[0])
    
    info = dict(infos[0])
    info["line0"] = (tiles[0][0] - 1) if int(info["seg_total"] or 1) > 1 else None
    info["lines"] = sum(t[1].shape[0] for t in tiles)
    plane = tiles[0][1] if len(tiles) == 1 else np.vstack([t[1] for t in tiles])
    
    return (time_str, band, info, plane, res)

def proses_satu_adegan(sc, out_dir):
    sid = sc["id"]
    sat = sc["sat"]
    folder = os.path.join(DATA_ROOT, sat, sid)
    kt = sc["key_time"]
    ctx_times = sc["context_times"] # [t-40, t-30, t-10]
    date_str = sc["date"].replace("/", "-")
    
    # Pemetaan waktu
    t_0 = kt
    t_m40 = ctx_times[0]
    t_m30 = ctx_times[1]
    t_m10 = ctx_times[2]
    
    t0_benchmark = time.time()
    print(f"\nMemproses ekstraksi dataset adegan: {sid} ({date_str} {kt} UTC)...", flush=True)
    
    # Siapkan daftar target pemuatan band
    pekerjaan_muat = []
    # 6 band t0
    for b in (1, 2, 3, 4, 7, 13):
        pekerjaan_muat.append((folder, t_0, b))
    # 3 band t-10
    for b in (3, 4, 13):
        pekerjaan_muat.append((folder, t_m10, b))
    # 3 band t-30
    for b in (3, 4, 13):
        pekerjaan_muat.append((folder, t_m30, b))
    # 3 band t-40
    for b in (3, 4, 13):
        pekerjaan_muat.append((folder, t_m40, b))
        
    loaded_bands = {}
    with ThreadPoolExecutor(max_workers=6) as ex:
        for t_str, b, info, plane, res in ex.map(muat_satu_berkas_band, pekerjaan_muat):
            if info is not None:
                loaded_bands[(t_str, b)] = (info, plane, res)
                
    print(f"  Pemuatan {len(loaded_bands)}/15 band selesai dalam {time.time() - t0_benchmark:.1f}s", flush=True)
    if len(loaded_bands) < 15:
        print(f"  ! PERINGATAN: Adegan {sid} kekurangan band! Hanya {len(loaded_bands)} band.", flush=True)
        return []
        
    hasil_patches = []
    
    # Urutan 15 kanal yang baku
    urutan_kanal = [
        (t_0, 1), (t_0, 2), (t_0, 3), (t_0, 4), (t_0, 7), (t_0, 13),
        (t_m10, 3), (t_m10, 4), (t_m10, 13),
        (t_m30, 3), (t_m30, 4), (t_m30, 13),
        (t_m40, 3), (t_m40, 4), (t_m40, 13),
    ]
    
    for reg_id, g_info in KOTAK_GRID.items():
        ltu, lsl, loB, loT = g_info["bbox"]
        H_target, W_target = g_info["grid_shape"]
        
        # Resampling 15 kanal ke grid bersama 1 km (H_target, W_target)
        kanals_resampled = []
        info_t0_b13 = None
        crop_t0_b13 = None
        
        for t_str, b in urutan_kanal:
            info, plane, res = loaded_bands[(t_str, b)]
            box, sub = potong_lalo(info, plane, ltu, lsl, loB, loT)
            
            # Konversi nilai fisik
            if b in (1, 2, 3, 4):
                # Reflektansi albedo [0.0 .. 1.0]
                val_arr = selip(sub).astype(np.float32)
            else:
                # Suhu kecerahan Kelvin [180 .. 340 K]
                val_arr = tb_ir(info, sub).astype(np.float32)
                
            if (t_str, b) == (t_0, 13):
                info_t0_b13 = info
                crop_t0_b13 = val_arr
                
            # Pemilihan algoritma resampling sesuai aturan kebijakan grid di Changelog:
            # - R05 (0.5 km) -> BOX (Area averaging)
            # - R20 (2.0 km) -> BILINEAR
            # - R10 (1.0 km) -> BILINEAR
            pil_mode = Image.Resampling.BOX if res == "R05" else Image.Resampling.BILINEAR
            pil_img = Image.fromarray(val_arr).resize((W_target, H_target), pil_mode)
            kanals_resampled.append(np.asarray(pil_img, dtype=np.float32))
            
        stack_penuh = np.stack(kanals_resampled, axis=0) # Shape: (15, H_target, W_target)
        
        # Hitung topeng awan dingin pada t0 kanal 13 (TB13 < 265 K)
        # Resampling TB13 ke grid bersama
        pil_tb13 = Image.fromarray(crop_t0_b13).resize((W_target, H_target), Image.Resampling.BILINEAR)
        tb13_grid = np.asarray(pil_tb13, dtype=np.float32)
        topeng_awan_penuh = (tb13_grid < 265.0).astype(np.uint8) # Shape: (H_target, W_target)
        
        # Pemotongan ke ukuran 256x256
        for p_idx, (r0, r1, c0, c1) in enumerate(g_info["slices"]):
            patch_feat = stack_penuh[:, r0:r1, c0:c1].copy() # Shape: (15, 256, 256)
            patch_mask = topeng_awan_penuh[r0:r1, c0:c1].copy() # Shape: (256, 256)
            
            cloud_fraction = float(np.mean(patch_mask))
            
            # Hitung lat/lon bounding box potongan
            dlat = (ltu - lsl) / H_target
            dlon = (loT - loB) / W_target
            patch_lat_n = round(ltu - r0 * dlat, 4)
            patch_lat_s = round(ltu - r1 * dlat, 4)
            patch_lon_w = round(loB + c0 * dlon, 4)
            patch_lon_e = round(loB + c1 * dlon, 4)
            
            patch_id = f"patch_{sid}_{reg_id}_p{p_idx:02d}"
            out_file = os.path.join(out_dir, f"{patch_id}.npz")
            
            meta = {
                "patch_id": patch_id,
                "scene_id": sid,
                "sat": sat,
                "date": date_str,
                "key_time_utc": kt,
                "region": reg_id,
                "patch_idx": p_idx,
                "row_slice": [r0, r1],
                "col_slice": [c0, c1],
                "bbox": [patch_lon_w, patch_lat_s, patch_lon_e, patch_lat_n],
                "cloud_fraction": round(cloud_fraction, 4),
                "daylight": True,
                "shape": list(patch_feat.shape),
                "channels": KANAL_DESKRIPSI
            }
            
            np.savez_compressed(
                out_file,
                features=patch_feat,
                cloud_mask=patch_mask,
                meta=json.dumps(meta)
            )
            
            hasil_patches.append(meta)
            
    print(f"  -> Berhasil menghasilkan {len(hasil_patches)} potongan 256x256 untuk adegan {sid}.", flush=True)
    return hasil_patches

def bangun_dataset_p3a():
    os.makedirs(DATASET_DIR, exist_ok=True)
    print("=" * 70, flush=True)
    print("MEMULAI PEMBUATAN DATASET TANPA LABEL (P3a)", flush=True)
    print(f"Direktori output: {DATASET_DIR}", flush=True)
    print("=" * 70, flush=True)
    
    t_global = time.time()
    semua_meta = []
    
    for idx, sc in enumerate(PILOT_SCENES, start=1):
        res = proses_satu_adegan(sc, DATASET_DIR)
        semua_meta.extend(res)
        
    index_file = os.path.join(DATASET_DIR, "dataset_index.json")
    with open(index_file, "w", encoding="utf-8") as f:
        json.dump(semua_meta, f, indent=2)
        
    durasi = time.time() - t_global
    print("\n" + "=" * 70, flush=True)
    print(f"SELESAI MEMBUAT DATASET: {len(semua_meta)} potongan dalam {durasi/60:.2f} menit.", flush=True)
    print(f"Indeks tersimpan di: {index_file}", flush=True)
    print("=" * 70, flush=True)
    return semua_meta

if __name__ == "__main__":
    bangun_dataset_p3a()
