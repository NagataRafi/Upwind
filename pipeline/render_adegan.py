# -*- coding: utf-8 -*-
"""
Render Komposit Warna Bingkai Kunci 8 Adegan Pilot ke docs/adegan/.
Dioptimasi:
1. Dekompresi band HSD hanya SEKALI per adegan, lalu dipotong untuk kedua kotak (Kalteng & Riau).
2. Filter garis pantai Natural Earth disaring ke wilayah Indonesia/Asia Tenggara untuk kecepatan tinggi.
3. Menampilkan komposit True Color (B03/B02/B01), B03, B13 (IR), dan Topeng Awan Dingin
   dilengkapi kisi lat/lon 1 derajat dan garis pantai Natural Earth 10m.
"""

import os
import sys
import re
import math
import json
import time
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import DATA_ROOT
from unduh_pilot_8_adegan import PILOT_SCENES
from olah_himawari_fm1 import baca_hsd, tb_ir, selip, inv_px, potong_lalo

PROJ_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT_DIR = os.path.join(PROJ_ROOT, "docs", "adegan")
PANTAI_PATH = os.path.join(PROJ_ROOT, "data", "coast_ne10m.geojson")

KOTAKS = {
    "riau":    (2.4, -2.6, 97.5, 106.5),     # latN, latS, lonBarat, lonTimur
    "kalteng": (-0.2, -4.8, 109.8, 116.2),
}

_PANTAI_REGIONAL = None

def muat_pantai_regional():
    """Memuat dan menyaring garis pantai hanya di kawasan regional (Sumatra & Kalimantan)."""
    global _PANTAI_REGIONAL
    if _PANTAI_REGIONAL is not None:
        return _PANTAI_REGIONAL
        
    if not os.path.exists(PANTAI_PATH):
        _PANTAI_REGIONAL = []
        return _PANTAI_REGIONAL
        
    try:
        with open(PANTAI_PATH, "r", encoding="utf-8") as f:
            g = json.load(f)
            
        fitur = []
        for feat in g.get("features", []):
            geom = feat.get("geometry", {})
            t = geom.get("type")
            coords = geom.get("coordinates", [])
            if t == "LineString":
                fitur.append(coords)
            elif t == "MultiLineString":
                fitur.extend(coords)
                
        # Filter segmen yang berada dalam cakupan Sumatra & Kalimantan (-6 s/d +4 lat, 96 s/d 118 lon)
        regional = []
        for seg in fitur:
            # Jika ada setidaknya 1 titik dalam kotak besar Indonesia barat, simpan segmennya
            ada = any((95.0 <= p[0] <= 118.0 and -6.0 <= p[1] <= 4.0) for p in seg)
            if ada:
                regional.append(seg)
                
        _PANTAI_REGIONAL = regional
        print(f"  [Garis Pantai] Berhasil memuat {len(regional)} segmen pantai regional.", flush=True)
        return _PANTAI_REGIONAL
    except Exception as e:
        print(f"  Peringatan muat pantai: {e}", flush=True)
        _PANTAI_REGIONAL = []
        return _PANTAI_REGIONAL

def buat_layer_kisi(info, box, pw2, ph2, scale, kotak):
    ltu, lsl, loB, loT = kotak
    l0, _, c0, _ = box
    lay = Image.new("RGBA", (pw2, ph2), (0, 0, 0, 0))
    dl = ImageDraw.Draw(lay)
    try:
        f = ImageFont.truetype("consola.ttf", 12)
    except Exception:
        f = ImageFont.load_default()
        
    # Garis lintang (latitude)
    for la in range(int(math.ceil(lsl)), int(math.floor(ltu)) + 1):
        rr, _ = inv_px(info, la, (loB + loT) / 2.0)
        y = (rr - l0) * scale
        if 0 <= y <= ph2:
            dl.line([0, y, pw2, y], fill=(255, 215, 80, 210), width=1)
            dl.text((2, y + 1), f"{la}°", fill=(255, 215, 80), font=f)
            
    # Garis bujur (longitude)
    for lo in range(int(math.ceil(loB)), int(math.floor(loT)) + 1):
        _, cc = inv_px(info, (ltu + lsl) / 2.0, lo)
        x = (cc - c0) * scale
        if 0 <= x <= pw2:
            dl.line([x, 0, x, ph2], fill=(255, 215, 80, 210), width=1)
            dl.text((x + 2, 1), f"{lo}°", fill=(255, 215, 80), font=f)
            
    # Garis pantai regional
    for seg in muat_pantai_regional():
        pts = []
        for slo, sla in seg:
            if not (loB - 0.5 <= slo <= loT + 0.5 and lsl - 0.5 <= sla <= ltu + 0.5):
                if len(pts) > 1:
                    dl.line(pts, fill=(255, 160, 40, 255), width=1)
                pts = []
                continue
            rr, cc = inv_px(info, sla, slo)
            xp, yp = (cc - c0) * scale, (rr - l0) * scale
            if -3 <= xp <= pw2 + 3 and -3 <= yp <= ph2 + 3:
                pts.append((xp, yp))
            else:
                if len(pts) > 1:
                    dl.line(pts, fill=(255, 160, 40, 255), width=1)
                pts = []
        if len(pts) > 1:
            dl.line(pts, fill=(255, 160, 40, 255), width=1)
    return lay

def proses_satu_adegan(sc, no_adegan):
    sid = sc["id"]
    sat = sc["sat"]
    folder = os.path.join(DATA_ROOT, sat, sid)
    kt = sc["key_time"]
    date_str = sc["date"].replace("/", "-")
    hh, mm = int(kt[:2]), int(kt[2:])
    hh_wib = (hh + 7) % 24
    waktu_str = f"{date_str} {hh:02d}:{mm:02d} UTC ({hh_wib:02d}:{mm:02d} WIB)"
    
    print(f"\n[{no_adegan}/8] Memproses Adegan: {sid} ({waktu_str})", flush=True)
    t0 = time.time()
    
    # 1. Baca semua band kunci ke memori sekali saja
    raw_bands = {}
    for band in (1, 2, 3, 4, 7, 13):
        pola = rf"_B{band:02d}_FLDK_[RR]\d\d_S\d+\.DAT\.bz2$"
        paths = [
            os.path.join(folder, f) for f in os.listdir(folder)
            if re.search(pola, f) and f"_{kt}_" in f
        ]
        if not paths:
            continue
            
        byres = {}
        for p in paths:
            m = re.search(rf"_B{band:02d}_FLDK_(R\d\d)_S\d+\.DAT\.bz2$", p)
            if m:
                byres.setdefault(m.group(1), []).append(p)
        if not byres:
            continue
            
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
        raw_bands[band] = (info, plane)
        
    print(f"  Band terbaca ke memori: {sorted(raw_bands.keys())} dalam {time.time() - t0:.1f} detik.", flush=True)
    
    if 3 not in raw_bands or 13 not in raw_bands:
        print(f"  ! Adegan {sid} kekurangan B03 atau B13. Dilewati.", flush=True)
        return []

    hasil_adegan = []
    
    # 2. Render untuk masing-masing kotak (Kalteng dan Riau) dari array yang sama di memori
    for nm_kotak in ("kalteng", "riau"):
        kotak = KOTAKS[nm_kotak]
        ltu, lsl, loB, loT = kotak
        
        # Potong area kotak untuk tiap band
        bands_crop = {}
        for b, (info, plane) in raw_bands.items():
            try:
                box, sub = potong_lalo(info, plane, ltu, lsl, loB, loT)
                bands_crop[b] = (info, sub, box)
            except Exception as e:
                print(f"    Gagal potong B{b:02d} {nm_kotak}: {e}", flush=True)
                
        info13, b13, box13 = bands_crop[13]
        tb13 = tb_ir(info13, b13)
        ta13 = (np.clip((tb13 - 250) / 70.0, 0, 1) * 255).astype(np.uint8)
        topeng_awan = (tb13 < 265).astype(np.uint8) * 255
        
        # Penyetaraan kisi optik B01, B02, B03
        vis = [b for b in (1, 2, 3) if b in bands_crop]
        th = max(bands_crop[b][1].shape[0] for b in vis)
        tc = max(bands_crop[b][1].shape[1] for b in vis)
        
        def ke_grid(item):
            bx, arr, binfo = item[2], item[1], item[0]
            if arr.shape == (th, tc):
                return np.asarray(arr, dtype=np.float64), bx, binfo
            s = float(arr.shape[1]) / float(tc)
            l0, _, c0, _ = bx
            bx2 = (
                int(round(l0 / s)),
                int(round(l0 / s + (th - 1))),
                int(round(c0 / s)),
                int(round(c0 / s + (tc - 1)))
            )
            binfo2 = dict(binfo)
            binfo2["cfac"] = binfo["cfac"] / s
            pil_resized = Image.fromarray(arr).resize((tc, th), Image.BILINEAR)
            return np.asarray(pil_resized, dtype=np.float64), bx2, binfo2

        chs = {b: ke_grid(bands_crop[b]) for b in vis}
        komposit = None
        if 1 in chs and 2 in chs and 3 in chs:
            ch1, bx1, in1 = chs[1]
            ch2, _, _ = chs[2]
            ch3, _, _ = chs[3]
            semua = np.concatenate([ch1.ravel(), ch2.ravel(), ch3.ravel()])
            lo, hi = np.nanpercentile(semua, 2), np.nanpercentile(semua, 98)
            if hi > lo:
                komposit = (np.clip((np.dstack([ch3, ch2, ch1]) - lo) / (hi - lo), 0, 1) * 255).astype(np.uint8)
            else:
                komposit = np.zeros((th, tc, 3), dtype=np.uint8)
            b_finest = max(vis, key=lambda b: bands_crop[b][1].shape[1])
            info_k, box_k = chs[b_finest][2], chs[b_finest][1]
        elif 3 in chs:
            komposit = (selip(bands_crop[3][1]) * 255).astype(np.uint8)
            info_k, box_k = bands_crop[3][0], bands_crop[3][2]
            
        pan = []
        judul_tc = "1. Komposit True Color (B03/B02/B01)" if (1 in chs and 2 in chs) else "1. B03 Saja"
        if komposit is not None:
            pan.append((judul_tc, komposit, info_k, box_k))
            
        b3info, b3arr, b3box = bands_crop[3]
        pan.append(("2. Reflektansi B03 Merah (0.64 µm)", (selip(b3arr) * 255).astype(np.uint8), b3info, b3box))
        pan.append(("3. Suhu Kecerahan TB13 (10.4 µm, 250-320 K)", ta13, info13, box13))
        pan.append(("4. Topeng Awan Dingin (TB13 < 265 K)", topeng_awan, info13, box13))
        
        tile = 600
        W = 1320
        Himg = 100 + ((len(pan) + 1) // 2) * (tile + 40)
        im = Image.new("RGB", (W, Himg), (15, 18, 25))
        dr = ImageDraw.Draw(im)
        
        try:
            f = ImageFont.truetype("consola.ttf", 13)
            fb = ImageFont.truetype("consolab.ttf", 18)
        except Exception:
            f = fb = ImageFont.load_default()
            
        nm_daerah = "Kalimantan Tengah" if nm_kotak == "kalteng" else "Riau & Sekitarnya"
        dr.text((15, 10), f"Adegan {no_adegan}: {sid} — Kotak {nm_daerah}", fill=(245, 245, 240), font=fb)
        dr.text((15, 36), f"Waktu: {waktu_str} | Satelit: {sat.upper()} | Resolusi Asli", fill=(210, 215, 225), font=f)
        dr.text((15, 54), f"BBox: Lat [{lsl:.1f} .. {ltu:.1f}], Lon [{loB:.1f} .. {loT:.1f}] | Kisi Kuning 1°, Pantai Oranye | Perkiraan, bukan jaminan", fill=(170, 180, 195), font=f)
        
        # Buat layer kisi/pantai sekali per geometri
        lay_dict = {}
        for idx_p, (judul, arr, binfo, bbox) in enumerate(pan):
            r, c8 = divmod(idx_p, 2)
            x = 15 + c8 * (tile + 50)
            y0 = 85 + r * (tile + 40)
            dr.text((x, y0), judul, fill=(230, 235, 245), font=f)
            
            ph, pw = arr.shape[:2]
            scale = tile / max(pw, ph)
            pw2, ph2 = max(1, int(pw * scale)), max(1, int(ph * scale))
            
            pil_arr = Image.fromarray(arr).resize((pw2, ph2))
            dr.rectangle([x - 1, y0 + 19, x + 1 + pw2, y0 + 21 + ph2], outline=(70, 75, 90))
            im.paste(pil_arr.convert("RGB"), (x, y0 + 20))
            
            # Cache layer kisi berdasarkan cfac/dimensi agar tidak hitung ulang inv_px
            geo_key = (binfo.get("cfac"), binfo.get("loff"), pw2, ph2)
            if geo_key not in lay_dict:
                lay_dict[geo_key] = buat_layer_kisi(binfo, bbox, pw2, ph2, scale, kotak)
            lay = lay_dict[geo_key]
            im.paste(lay, (x, y0 + 20), lay)
            
        out_name = f"adegan_{no_adegan}_{sid}_{nm_kotak}.png"
        out_path = os.path.join(OUT_DIR, out_name)
        im.save(out_path)
        print(f"    -> Tersimpan: {out_name}", flush=True)
        hasil_adegan.append(out_path)
        
    return hasil_adegan

def render_semua():
    os.makedirs(OUT_DIR, exist_ok=True)
    print(f"=== MEMULAI PERENDERAN 8 ADEGAN PILOT KE {OUT_DIR} ===", flush=True)
    muat_pantai_regional()
    total_berkas = []
    t_start = time.time()
    
    for idx, sc in enumerate(PILOT_SCENES, start=1):
        res = proses_satu_adegan(sc, idx)
        total_berkas.extend(res)
        
    durasi_total = time.time() - t_start
    print(f"\n=== SELESAI RENDER {len(total_berkas)} GAMBAR DALAM {durasi_total:.1f} DETIK ({durasi_total/60:.2f} MENIT) ===", flush=True)

if __name__ == "__main__":
    render_semua()
