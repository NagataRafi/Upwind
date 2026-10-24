# -*- coding: utf-8 -*-
"""
Konfigurasi Terpusat Upwind (Membaca .env dan Variabel Lingkungan).
JANGAN PERNAH menanam kunci atau jalur rahasia langsung di kode.
"""
import os
from dotenv import dotenv_values

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_env_path = os.path.join(_root, ".env")
_env = dotenv_values(_env_path) if os.path.exists(_env_path) else {}

# DATA_ROOT untuk berkas mentah dan data besar di partisi D:
DATA_ROOT = os.getenv("DATA_ROOT") or _env.get("DATA_ROOT") or r"D:\upwind_data"

# FIRMS MAP_KEY untuk akses titik panas NASA FIRMS
def get_firms_map_key():
    return os.getenv("FIRMS_MAP_KEY") or _env.get("FIRMS_MAP_KEY") or ""
