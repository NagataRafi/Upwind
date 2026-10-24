# -*- coding: utf-8 -*-
"""
Skrip Pembantu Penyiapan Bahan Anotasi QGIS / Alat Anotasi.
Mengekstrak crop wilayah Riau dan Kalteng, menghasilkan gambar komposit beresolusi asli,
dan membuat kerangka GeoJSON untuk menggambar poligon label ground-truth.
"""

import os
import sys
import json
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kotak_fm1 import render_kotak, KOTAKS
from config import DATA_ROOT

def siapkan_template_geojson(output_path, region_id, label_kasus):
    """Membuat template berkas GeoJSON kosong dengan struktur atribut standar."""
    fitur_koleksi = {
        "type": "FeatureCollection",
        "name": f"label_asap_{region_id}_{label_kasus}",
        "crs": {
            "type": "name",
            "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}
        },
        "features": []
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(fitur_koleksi, f, indent=2, ensure_ascii=False)
    print(f"Template GeoJSON tersimpan: {output_path}")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_OUT = os.path.join(BASE_DIR, "docs", "anotasi")

def siapkan_bahan_anotasi(label_kasus, folder_raw, out_dir=DEFAULT_OUT):
    """
    Menyiapkan berkas gambar kotak wilayah dan template layer GeoJSON untuk QGIS.
    """
    os.makedirs(out_dir, exist_ok=True)
    for region_id in ("riau", "kalteng"):
        dir_reg = os.path.join(out_dir, region_id, label_kasus)
        os.makedirs(dir_reg, exist_ok=True)
        
        # Render panel visual bantuan
        try:
            render_kotak(label_kasus, folder_raw, region_id)
        except Exception as e:
            print(f"Gagal render kotak untuk anotasi: {e}")
            
        # Buat template GeoJSON
        path_geojson = os.path.join(dir_reg, f"anotasi_{region_id}_{label_kasus}.geojson")
        siapkan_template_geojson(path_geojson, region_id, label_kasus)
        
    print(f"Bahan anotasi untuk {label_kasus} siap di {out_dir}")

if __name__ == "__main__":
    folder_uji = os.path.join(DATA_ROOT, "noaa-himawari8", "asap_2019-09-14")
    if os.path.isdir(folder_uji):
        siapkan_bahan_anotasi("asap_2019-09-14", folder_uji)
