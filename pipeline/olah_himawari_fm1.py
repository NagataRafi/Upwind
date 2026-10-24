# -*- coding: utf-8 -*-
"""Olah Himawari HSD -> gambar FR-M1. Basis struktur header: satpy ahi_hsd.py
(Apache-2.0). Pemetaan lat/lon approx bola; untuk bingkai citra FR-M1 saja.
"""
import os, re, bz2, sys, math, numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hsd_header import parse_header_full

from config import DATA_ROOT
RAW = DATA_ROOT
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "fm1")
os.makedirs(OUT, exist_ok=True)

LAT_MIN, LAT_MAX = -8.5, 10.5
LON_MIN, LON_MAX = 92.0, 123.0

def baca_hsd(path):
    raw = open(path, "rb").read()
    data = bz2.decompress(raw)
    info = parse_header_full(data[:4000])
    start = int(info["total_header"])
    cols, lines = info["cols"], info["lines"]
    arr = np.frombuffer(data, dtype="<u2", offset=start, count=cols * lines)
    return info, arr.reshape(lines, cols)

def buat_px(info):
    """Fungsi (line, col) -> (lat, lon). Kerangka satelit: X_e=timur@ekuator,
    Y_e=utara, Z_e=ke arah bumi (sublon). u = (cos b·sin a, sin b, -cos a·cos b)."""
    H = info["dist_center"] * 1000.0
    R = info["a"] * 1000.0
    l0 = math.radians(info["proj_sub_lon"])
    dpp = 65536.0 / info["cfac"]   # derajat sudut sapu per piksel
    coff, loff = info["coff"], info["loff"]
    line0 = int(info.get("line0", 0) or 0)   # indeks 0-based baris pertama dalam plane (multi-segmen)
    def px(line, col):
        a = math.radians((col + 1.0 - coff) * dpp)
        b = math.radians((loff - (line0 + line) - 1.0) * dpp)  # CGMS: y = (LOFF-line-1); baris 0 = paling utara
        ux = math.cos(b) * math.sin(a)
        uy = math.sin(b)
        uz = -math.cos(a) * math.cos(b)
        S = np.array([0.0, 0.0, H])
        u = np.array([ux, uy, uz])
        Sdu = S @ u
        disc = Sdu * Sdu - (S @ S - R * R)
        if disc < 0:
            return (None, None)
        t = -Sdu - math.sqrt(disc)
        P = S + t * u
        norm = np.linalg.norm(P)
        lat = math.degrees(math.asin(max(-1.0, min(1.0, P[1] / norm))))
        lon = math.degrees(l0 + math.atan2(P[0], P[2]))
        return (lat, lon)
    return px

def box_potong(info, px):
    """Cari indeks (line_top, line_bot, col_left, col_right), dan apakah data
    disimpan utara-dulu (flip kartografis). Ambang pakai banding terhadap target."""
    lines, cols = info["lines"], info["cols"]
    step = max(1, lines // 300)
    lat_at = {}
    for l in range(0, lines, step):
        la, _ = px(l, int(info["coff"]))
        if la is not None:
            lat_at[l] = la
    if not lat_at:
        return None
    ls = sorted(lat_at)
    naik = lat_at[ls[-1]] > lat_at[ls[0]]   # lat naik bersama indeks line?
    def terdekat(dict_, target):
        k = min(dict_, key=lambda i: abs(dict_[i] - target))
        return k
    l_top = terdekat(lat_at, LAT_MAX)
    l_bot = terdekat(lat_at, LAT_MIN)
    lc = min(lines - 1, int(info["loff"]))
    lon_at = {}
    stepc = max(1, cols // 300)
    for c in range(0, cols, stepc):
        _, lo = px(lc, c)
        if lo is not None:
            lon_at[c] = lo
    c_l = terdekat(lon_at, LON_MIN)
    c_r = terdekat(lon_at, LON_MAX)
    return (min(l_top, l_bot), max(l_top, l_bot), min(c_l, c_r), max(c_l, c_r), naik)

def potong(info, plane):
    px = buat_px(info)
    box = box_potong(info, px)
    l0, l1, c0, c1, naik = box
    sub = plane[l0:l1 + 1, c0:c1 + 1]
    if not naik:
        sub = sub[::-1, :]
    grid = buat_grid(info, px, box)
    return sub.copy(), box, grid

def buat_grid(info, px, box):
    """Baris kolom indeks (di dalam crop) utk garis kisi tiap 5 derajat."""
    l0, l1, c0, c1, naik = box
    lebar, tinggi = c1 - c0 + 1, l1 - l0 + 1
    hlat, hlon = [], []
    step = max(1, (l1 - l0) // 120)
    lmid = (l0 + l1) // 2
    for la in (-5, 0, 5, 10):
        best = None
        for l in range(max(0, l0 - step), min(info["lines"], l1 + step), step):
            v, _ = px(l, int(info["coff"]))
            if v is None:
                continue
            if best is None or abs(v - la) < abs(px(best, int(info["coff"]))[0] - la if best else 999):
                best = l
        if best is not None:
            delnominal = best if naik else (l1 - (best - l0))
            k2 = (best - l0) if naik else (l1 - best)
            if 0 <= k2 < tinggi:
                hlat.append((k2, la))
    stepc = max(1, (c1 - c0) // 120)
    for lo in (95, 100, 105, 110, 115, 120):
        best = None
        for c in range(max(0, c0 - stepc), min(info["cols"], c1 + stepc), stepc):
            _, v = px(min(info["lines"] - 1, lmid), c)
            if v is None:
                continue
            if best is None or abs(v - lo) < abs(px(min(info["lines"] - 1, lmid), best)[1] - lo if best else 999):
                best = c
        if best is not None:
            k2 = best - c0
            if 0 <= k2 < lebar:
                hlon.append((k2, lo))
    return dict(lat=hlat, lon=hlon)

def tb_ir(info, plane):
    gain, off = info["gain"], info["off"]
    rad = plane.astype(np.float64) * gain + off  # W/(m2 sr um)
    cwl = info["cwl"] * 1e-6
    h = 6.62607015e-34; c = 299792458.0; k = 1.380649e-23
    a1 = h * c / k / cwl
    b1 = (2 * h * c * c) / (cwl ** 5)
    return a1 / np.log(b1 / np.maximum(rad, 1e-12) * 1e-6 + 1.0)

def selip(a):
    lo, hi = np.nanpercentile(a, 2), np.nanpercentile(a, 98)
    return np.clip((a - lo) / (hi - lo + 1e-9), 0, 1)

def render_kasus(label, folder):
    print(">>", label, folder)
    bands = {}
    for band in (1, 2, 3, 4, 7, 13):
        paths = [os.path.join(folder, f) for f in os.listdir(folder)
                 if re.search(r"_B%02d_FLDK_[RR]\d\d_S\d+\.DAT\.bz2$" % band, f)]
        if not paths:
            continue
        try:
            infos, tiles = [], []
            for p in paths:
                i, a = baca_hsd(p)
                infos.append(i); tiles.append((int(i["seg_first_line"] or 0), a, p))
            tiles.sort(key=lambda t: t[0])
            info = dict(infos[0])
            info["line0"] = (tiles[0][0] - 1) if int(info["seg_total"] or 1) > 1 else None
            if int(info["seg_total"] or 1) > 1:
                plane = np.vstack([a for _, a, _ in tiles])
                info = dict(info); info["lines"] = sum(inf["lines"] for inf in infos)
            else:
                plane = tiles[0][1]
            sub, box, grid = potong(info, plane)
            bands[band] = (info, sub)
            print("  B%02d grid %dx%d -> %s box=%s kisi=%d/%d" % (
                band, info["cols"], info["lines"], sub.shape, box[:4], len(grid["lat"]), len(grid["lon"])))
        except Exception as e:
            import traceback; traceback.print_exc()
            print("  B%02d GAGAL" % band)
    if any(b not in bands for b in (3, 7, 13)):
        print("  ! band pokok kurang")
        return None
    info13, b13 = bands[13]
    tb13 = tb_ir(info13, b13)
    tables = {}
    for band in (1, 2, 3, 4):
        if band in bands:
            inf, pl = bands[band]
            tables[band] = selip(pl)
    tb7 = tb_ir(bands[7][0], bands[7][1])
    tile = 440
    # LAYER API DIHAPUS (TEMUAN): Tb7-Tb13 siang hari tercemar pantulan surya (CIMSS/Literatur);
    # titik panas nanti memakai produk AHI-L2WLF JAXA (registrasi P-Tree diperlukan).
    ta13 = np.clip((tb13 - 250) / 70.0, 0, 1)
    # topeng awan dingin B13 (pemisah awan tinggi dari asap)
    topeng_awand = (tb13 < 265).astype(np.uint8) * 255
    ta07 = np.clip((tb7 - 240) / 120.0, 0, 1)
    W = 950
    nrows = (len(panels_poss := None) or 3) if False else 3
    Himg = 64 + nrows * (tile + 24)
    im = Image.new("RGB", (W, Himg), (16, 18, 26))
    dr = ImageDraw.Draw(im)
    try:
        f = ImageFont.truetype("consola.ttf", 14)
        fb = ImageFont.truetype("consolab.ttf", 16)
    except Exception:
        f = fb = ImageFont.load_default()
    dr.text((10, 4), label, fill=(240, 238, 225), font=fb)
    dr.text((10, 24), "Citra jam 03:00 UTC = 10:00 WIB. Garis kisi lat/lon tiap 5 derajat (label kecil).", fill=(200, 205, 215), font=f)
    # susun panel: (judul, aktor(PIL atau uint8w), info grid untuk kisi)
    grid13 = buat_grid(bands[13][0], px13 := buat_px(bands[13][0]), (0, bands[13][1].shape[0] - 1, 0, bands[13][1].shape[1] - 1, True))
    panels = []
    gambar_tc = None
    # komposit warna: samakan grid dulu (B03 2026 = grid 2x lebih halus daripada B01/B02),
    # lalu satu peregangan bersama utk ketiga kanal (bukan peregangan per band)
    if 3 in tables and 1 in tables and 2 in tables:
        th = max(bands[b][1].shape[0] for b in (1, 2, 3))
        tc = max(bands[b][1].shape[1] for b in (1, 2, 3))
        def ke_grid(arr):
            if arr.shape == (th, tc):
                return arr
            return np.asarray(Image.fromarray(arr).resize((tc, th), Image.BILINEAR))
        ch1 = np.asarray(ke_grid(bands[1][1]), dtype=np.float64)
        ch2 = np.asarray(ke_grid(bands[2][1]), dtype=np.float64)
        ch3 = np.asarray(ke_grid(bands[3][1]), dtype=np.float64)
        semua = np.concatenate([ch1.ravel(), ch2.ravel(), ch3.ravel()])
        lo, hi = np.nanpercentile(semua, 2), np.nanpercentile(semua, 98)
        arr_tc = np.clip((np.dstack([ch3, ch2, ch1]) - lo) / (hi - lo), 0, 1)
        arr_tc = (arr_tc * 255).astype(np.uint8)
        gambar_tc = ("True color: B03 merah / B02 hijau / B01 biru, satu peregangan bersama", arr_tc)
        panels.append(gambar_tc)
        panels.append(("B03 0.64u peregangan 2-98%", (selip(bands[3][1]) * 255)))
    elif 3 in tables:
        panels.append(("B03 0.64u peregangan 2-98% (tanpa B01/B02: tanpa warna asli)", (selip(bands[3][1]) * 255)))
    panels.append(("B13 10.8u TB (skala 250-320 K, makin terang = makin hangat)", (ta13 * 255).astype(np.uint8)))
    panels.append(("topeng awan dingin: TB13 < 265 K (deteksi B13)", topeng_awand))
    panels.append(("B07 3.9u TB (skala 240-360 K, SIANG: tercemar surya!)", (ta07 * 255).astype(np.uint8)))
    if 4 in tables:
        panels.append(("B04 0.86u peregangan 2-98%", (tables[4] * 255).astype(np.uint8)))
    yy = 54
    for idx, (judul, arr) in enumerate(panels):
        if arr is None:
            continue
        r, c8 = divmod(idx, 2)
        x = 10 + c8 * (tile + 15)
        yyr = yy + r * (tile + 26)
        dr.text((x, yyr), judul, fill=(225, 228, 235), font=f)
        ph, pw = arr.shape[0], arr.shape[1]
        scale = tile / max(pw, ph)
        pw2, ph2 = int(pw * scale), int(ph * scale)
        pil = Image.fromarray(arr).resize((pw2, ph2))
        dr.rectangle([x - 1, yyr + 20, x + 1 + pw2, yyr + 22 + ph2], outline=(90, 95, 105))
        # kisi untuk panel IR/lain memakai grid13 bila bentuk sama persis sumber TB13
        try:
            if (arr.shape[0] == th_ref and arr.shape[1] == tw_ref):
                for k2, la in grid13["lat"]:
                    yyz = int(k2 * scale)
                    dr.line([x, yyr + 21 + yyz, x + pw2, yyr + 21 + yyz], fill=(255, 210, 100), width=1)
                    dr.text((x + 2, yyr + 21 + yyz + 1), "%d" % la, fill=(255, 210, 100), font=f)
                for k2, lo in grid13["lon"]:
                    xxz = int(k2 * scale)
                    dr.line([x + xxz, yyr + 21, x + xxz, yyr + 21 + ph2], fill=(255, 210, 100), width=1)
                    dr.text((x + xxz + 2, yyr + 23), "%d" % lo, fill=(255, 210, 100), font=f)
        except Exception:
            pass
        im.paste(pil.convert("RGB"), (x, yyr + 21))
    nama = os.path.join(OUT, "fm1_%s.png" % label)
    im.save(nama)
    print("  ->", nama)
    return nama

def inv_px(info, la, lo):
    """lat/lon (geodetik) -> indeks (line, col) — kebalikan buat_px"""
    a = info["a"] * 1000.0
    e2 = 1.0 - (info["b"] * 1000.0 / a) ** 2
    gct = math.atan((1.0 - e2) * math.tan(math.radians(la)))  # geosentrik (aproks)
    dl = math.radians(lo - info["proj_sub_lon"])
    P = np.array([a * math.cos(gct) * math.sin(dl), a * math.sin(gct), a * math.cos(gct) * math.cos(dl)])
    S = np.array([0.0, 0.0, info["dist_center"] * 1000.0])
    d = P - S
    nrm = float(np.linalg.norm(d))
    ang = math.degrees(math.atan2(float(d[0]), float(-d[2])))
    bb = math.degrees(math.asin(max(-1.0, min(1.0, float(d[1]) / nrm))))
    dpp = 65536.0 / info["cfac"]
    col = ang / dpp + info["coff"] - 1.0
    line = info["loff"] - 1.0 - (float(info.get("line0", 0) or 0)) - bb / dpp
    return line, col

def potong_lalo(info, plane, ltu, lsl, loB, loT):
    """Potong plane ke kotak lat/lon; kembalikan (box, sub). box=(l0,l1,c0,c1)."""
    la, ca = inv_px(info, ltu, loB)
    lb, cb = inv_px(info, lsl, loT)
    l0, l1 = sorted((int(la), int(lb)))
    c0, c1 = sorted((int(ca), int(cb)))
    l0, l1 = max(0, l0), min(info["lines"] - 1, l1)
    c0, c1 = max(0, c0), min(info["cols"] - 1, c1)
    if l1 - l0 < 2 or c1 - c0 < 2:
        raise ValueError("kotak di luar bidang")
    return (l0, l1, c0, c1), plane[l0:l1 + 1, c0:c1 + 1].copy()

CASES = [
    ("asap_2019-09-05", "noaa-himawari8", "asap_2019-09-05"),
    ("asap_2019-09-12", "noaa-himawari8", "asap_2019-09-12"),
    ("asap_2019-09-14", "noaa-himawari8", "asap_2019-09-14"),
    ("bersih_2019-10-15", "noaa-himawari8", "bersih_2019-10-15"),
    ("awan_2019-01-15", "noaa-himawari8", "awan_2019-01-15"),
    ("terkini_2026-10-23", "noaa-himawari9", "terkini_2026-10-23"),
]

if __name__ == "__main__":
    for label, bkt, sub in CASES:
        folder = os.path.join(RAW, bkt, sub)
        if os.path.isdir(folder):
            render_kasus(label, folder)
    print("SELESAI RENDER")
