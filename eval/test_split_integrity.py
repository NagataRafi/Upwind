# -*- coding: utf-8 -*-
"""
Uji Integritas Aturan Pembagian Dataset (Train/Test Split Integrity Test).
Sesuai aturan PRD P3a:
- Pembagian data HARUS per HARI (kalender), bukan per adegan atau per potongan.
- Semua adegan pada tanggal yang sama wajib berada di sisi yang sama (mencegah data leakage).
- Uji ini harus GAGAL bila ada tanggal yang muncul di kedua sisi.
"""

import sys

def ekstrak_tanggal_dari_adegan(scene_id_or_date):
    """Mengekstrak string tanggal 'YYYY-MM-DD' dari scene_id atau objek patch."""
    import re
    m = re.search(r"(\d{4}[-/]\d{2}[-/]\d{2})", str(scene_id_or_date))
    if not m:
        raise ValueError(f"Tidak dapat mengekstrak tanggal dari: {scene_id_or_date}")
    return m.group(1).replace("/", "-")

def verifikasi_integritas_split(train_items, test_items):
    """
    Memeriksa bahwa tidak ada tanggal yang tumpang tindih antara set latih dan set uji.
    Menerima daftar scene_id, nama berkas patch, atau string tanggal.
    Mengembalikan (train_dates, test_dates) jika valid.
    Melempar AssertionError jika terjadi kebocoran tanggal (data leakage).
    """
    train_dates = set(ekstrak_tanggal_dari_adegan(item) for item in train_items)
    test_dates = set(ekstrak_tanggal_dari_adegan(item) for item in test_items)
    
    kebocoran = train_dates.intersection(test_dates)
    if kebocoran:
        raise AssertionError(
            f"[DATA_LEAKAGE_GAGAL] Pelanggaran aturan pembagian per HARI! "
            f"Tanggal berikut muncul di set latih DAN set uji: {sorted(kebocoran)}"
        )
        
    return train_dates, test_dates

def test_split_rule():
    print("Menjalankan uji integritas aturan pembagian dataset (per hari)...")
    
    # 1. Kasus Valid (Split per Hari Murni)
    train_valid = [
        "asap_2019-09-12",
        "asap_2019-09-14",
        "asap_2019-09-14_0400",
        "asap_2019-09-14_0600",
        "awan_2019-01-15"
    ]
    test_valid = [
        "asap_2019-09-05",
        "bersih_2019-10-15",
        "terkini_2026-10-23"
    ]
    tr_d, te_d = verifikasi_integritas_split(train_valid, test_valid)
    print(f"  [OK] Kasus valid lolos: Train={sorted(tr_d)}, Test={sorted(te_d)}")
    
    # 2. Kasus Bocor (Leakage: tanggal 2019-09-14 terbelah di kedua sisi)
    train_leaky = [
        "asap_2019-09-14",       # 14 September 2019
        "asap_2019-09-12"
    ]
    test_leaky = [
        "asap_2019-09-14_0600",  # 14 September 2019 (bocor ke test!)
        "bersih_2019-10-15"
    ]
    try:
        verifikasi_integritas_split(train_leaky, test_leaky)
        print("  [GAGAL] Uji kebocoran seharusnya melempar AssertionError tetapi lolos!")
        sys.exit(1)
    except AssertionError as e:
        print(f"  [OK] Uji deteksi kebocoran berhasil mendeteksi pelanggaran: {e}")
        
    print("\nSEMUA UJI ATURAN PEMBAGIAN LOLOS DENGAN BENAR.")

if __name__ == "__main__":
    test_split_rule()
