# -*- coding: utf-8 -*-
"""
Skrip Pengujian Dataset Tanpa Label P3a (Uji Kriteria Penerimaan FR-M1/P3a).
Memeriksa:
1. Jumlah potongan per adegan (target: 14 per adegan = 6 Kalteng + 8 Riau, total 112).
2. Kesetaraan bentuk tumpukan (shape) antara Himawari-8 2019 dan Himawari-9 2026:
   Harus sama persis (15, 256, 256) untuk fitur dan (256, 256) untuk mask awan dingin.
3. Statistik fraksi awan dingin per adegan dan per wilayah.
"""

import os
import sys
import json
import glob
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "pipeline")))
from config import DATA_ROOT

DATASET_DIR = os.path.join(DATA_ROOT, "dataset_p3a")

def uji_dataset():
    index_file = os.path.join(DATASET_DIR, "dataset_index.json")
    if not os.path.exists(index_file):
        raise FileNotFoundError(f"Indeks dataset belum ditemukan di: {index_file}")
        
    with open(index_file, "r", encoding="utf-8") as f:
        meta_list = json.load(f)
        
    print("=" * 75)
    print("HASIL PENGUJIAN DATASET TANPA LABEL (P3a)")
    print("=" * 75)
    print(f"Total potongan yang terdaftar di indeks: {len(meta_list)}")
    
    # Kelompokkan per adegan
    per_adegan = {}
    for m in meta_list:
        sid = m["scene_id"]
        per_adegan.setdefault(sid, []).append(m)
        
    print(f"Total adegan unik: {len(per_adegan)} adegan (harus 8 adegan pilot)\n")
    assert len(per_adegan) == 8, f"Jumlah adegan {len(per_adegan)} != 8!"
    
    print(f"{'No':<3} | {'Scene ID':<24} | {'Satelit':<5} | {'Kalteng':<7} | {'Riau':<5} | {'Total':<5} | {'Rata-rata Awan Dingin'}")
    print("-" * 75)
    
    h8_sample = None
    h9_sample = None
    
    total_kalteng = 0
    total_riau = 0
    semua_fraksi_awan = []
    
    for idx, (sid, patches) in enumerate(per_adegan.items(), start=1):
        sat = patches[0]["sat"]
        n_kalteng = sum(1 for p in patches if p["region"] == "kalteng")
        n_riau = sum(1 for p in patches if p["region"] == "riau")
        n_total = len(patches)
        
        total_kalteng += n_kalteng
        total_riau += n_riau
        
        c_fractions = [p["cloud_fraction"] for p in patches]
        semua_fraksi_awan.extend(c_fractions)
        avg_cloud = np.mean(c_fractions)
        
        sat_short = "H9" if "himawari9" in sat else "H8"
        print(f"{idx:<3} | {sid:<24} | {sat_short:<5} | {n_kalteng:<7} | {n_riau:<5} | {n_total:<5} | {avg_cloud*100:6.2f}% (min {min(c_fractions)*100:.1f}%, max {max(c_fractions)*100:.1f}%)")
        
        # Validasi jumlah potongan per adegan
        assert n_kalteng == 6, f"Adegan {sid} Kalteng memiliki {n_kalteng} potongan (harus 6)!"
        assert n_riau == 8, f"Adegan {sid} Riau memiliki {n_riau} potongan (harus 8)!"
        assert n_total == 14, f"Adegan {sid} memiliki {n_total} potongan (harus 14)!"
        
        # Ambil sampel H8 dan H9 untuk perbandingan shape langsung dari berkas npz
        for p in patches:
            npz_path = os.path.join(DATASET_DIR, f"{p['patch_id']}.npz")
            assert os.path.exists(npz_path), f"Berkas tidak ada: {npz_path}"
            
            data = np.load(npz_path)
            feat = data["features"]
            mask = data["cloud_mask"]
            
            assert feat.shape == (15, 256, 256), f"Bentuk fitur {feat.shape} salah pada {p['patch_id']}!"
            assert mask.shape == (256, 256), f"Bentuk mask {mask.shape} salah pada {p['patch_id']}!"
            assert feat.dtype == np.float32, f"Dtype fitur {feat.dtype} bukan float32!"
            assert mask.dtype == np.uint8, f"Dtype mask {mask.dtype} bukan uint8!"
            
            if sat_short == "H8" and h8_sample is None:
                h8_sample = (p['patch_id'], feat.shape, mask.shape, feat.dtype)
            elif sat_short == "H9" and h9_sample is None:
                h9_sample = (p['patch_id'], feat.shape, mask.shape, feat.dtype)
                
    print("-" * 75)
    print(f"Total Keseluruhan : {len(meta_list)} potongan (Kalteng: {total_kalteng}, Riau: {total_riau})")
    print(f"Rata-rata Fraksi Awan Dingin : {np.mean(semua_fraksi_awan)*100:.2f}% (keseluruhan dataset)")
    print("=" * 75)
    
    # 2. Uji Kesetaraan Bentuk Tumpukan Himawari-8 vs Himawari-9
    print("\nUJI KESETARAAN BENTUK TUMPUKAN HIMAWARI-8 (2019) vs HIMAWARI-9 (2026):")
    print(f"  Sampel H8 ({h8_sample[0]}):")
    print(f"    - Fitur shape : {h8_sample[1]}, dtype: {h8_sample[3]}")
    print(f"    - Mask shape  : {h8_sample[2]}")
    print(f"  Sampel H9 ({h9_sample[0]}):")
    print(f"    - Fitur shape : {h9_sample[1]}, dtype: {h9_sample[3]}")
    print(f"    - Mask shape  : {h9_sample[2]}")
    
    assert h8_sample[1] == h9_sample[1] == (15, 256, 256), "Bentuk tumpukan fitur H8 dan H9 TIDAK sama!"
    assert h8_sample[2] == h9_sample[2] == (256, 256), "Bentuk topeng awan H8 dan H9 TIDAK sama!"
    print("  => [SUKSES TERVERIFIKASI] Bentuk tumpukan fitur (15, 256, 256) dan mask (256, 256) IDENTIK 100% antara H8 dan H9!\n")

if __name__ == "__main__":
    uji_dataset()
