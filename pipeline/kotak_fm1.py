# -*- coding: utf-8 -*-
"""Render kotak Riau / Kalimantan Tengah resolusi asli + pantai + kisi 1 derajat."""
import os, re, math, json, numpy as np
from PIL import Image, ImageDraw, ImageFont
from olah_himawari_fm1 import baca_hsd, tb_ir, selip, inv_px, potong_lalo, OUT

PANTAI = None   # cache garis pantai

def muat_pantai(path="data/coast_ne10m.geojson"):
    global PANTAI
    if PANTAI is not None:
        return PANTAI
    if not os.path.exists(path):
        print("  (pantai: berkas tidak ada, lewati)")
        PANTAI = []
        return PANTAI
    g = json.load(open(path, encoding="utf8"))
    fitur = []
    for f in g.get("features", []):
        geom = f["geometry"]
        if geom["type"] == "LineString":
            fitur.append(geom["coordinates"])
        elif geom["type"] == "MultiLineString":
            fitur += geom["coordinates"]
    PANTAI = fitur
    return fitur

KOTAKS = {
    "riau":    (2.4, -2.6, 97.5, 106.5),     # latN, latS, lonBarat, lonTimur
    "kalteng": (-0.2, -4.8, 109.8, 116.2),
}

def gambar_kisi_lay(info, box, pw2, ph2, scale, kotak):
    """Layer RGBA: kisi lat/lon 1 derajat + garis pantai utk panel dgn geometri 'info'."""
    ltu, lsl, loB, loT = kotak
    l0, _, c0, _ = box
    lay = Image.new("RGBA", (pw2, ph2), (0, 0, 0, 0))
    dl = ImageDraw.Draw(lay)
    try:
        f = ImageFont.truetype("consola.ttf", 12)
    except Exception:
        f = ImageFont.load_default()
    for la in range(int(math.ceil(lsl)), int(math.floor(ltu)) + 1):
        rr, _ = inv_px(info, la, (loB + loT) / 2.0)
        y = (rr - l0) * scale
        if 0 <= y <= ph2:
            dl.line([0, y, pw2, y], fill=(255, 210, 100, 200), width=1)
            dl.text((2, y + 1), "%d" % la, fill=(255, 210, 100), font=f)
    for lo in range(int(math.ceil(loB)), int(math.floor(loT)) + 1):
        _, cc = inv_px(info, (ltu + lsl) / 2.0, lo)
        x = (cc - c0) * scale
        if 0 <= x <= pw2:
            dl.line([x, 0, x, ph2], fill=(255, 210, 100, 200), width=1)
            dl.text((x + 2, 1), "%d" % lo, fill=(255, 210, 100), font=f)
    for seg in muat_pantai():
        pts = []
        for slo, sla in seg:
            if not (loB - 1.0 <= slo <= loT + 1.0 and lsl - 1.0 <= sla <= ltu + 1.0):
                if len(pts) > 1:
                    dl.line(pts, fill=(255, 170, 60, 255), width=1)
                pts = []
                continue
            rr, cc = inv_px(info, sla, slo)
            xp, yp = (cc - c0) * scale, (rr - l0) * scale
            if -3 <= xp <= pw2 + 3 and -3 <= yp <= ph2 + 3:
                pts.append((xp, yp))
            else:
                if len(pts) > 1:
                    dl.line(pts, fill=(255, 170, 60, 255), width=1)
                pts = []
        if len(pts) > 1:
            dl.line(pts, fill=(255, 170, 60, 255), width=1)
    return lay

def render_kotak(label, folder, nm_kotak):
    kotak = KOTAKS[nm_kotak]
    ltu, lsl, loB, loT = kotak
    print(">> kotak[%s] %s %s" % (nm_kotak, label, folder))
    bands = {}
    for band in (1, 2, 3, 4, 7, 13):
        paths = [os.path.join(folder, f) for f in os.listdir(folder)
                 if re.search(r"_B%02d_FLDK_[RR]\d\d_S\d+\.DAT\.bz2$" % band, f)]
        if not paths:
            continue
        try:
            # pilih satu resolusi per band (folder bisa berisi R05 & R10 campuran):
            byres = {}
            for p in paths:
                m = re.search(r"_B%02d_FLDK_(R\d\d)_S\d+\.DAT\.bz2$" % band, p)
                byres.setdefault(m.group(1), []).append(p)
            res = max(byres, key=lambda r: len(byres[r]))
            paths = byres[res]
            infos, tiles = [], []
            for p in paths:
                i, a = baca_hsd(p)
                infos.append(i); tiles.append((int(i["seg_first_line"] or 0), a))
            tiles.sort(key=lambda t: t[0])
            info = dict(infos[0])
            info["line0"] = (tiles[0][0] - 1) if int(info["seg_total"] or 1) > 1 else None
            info["lines"] = sum(t[1].shape[0] for t in tiles)
            plane = tiles[0][1] if len(tiles) == 1 else np.vstack([t[1] for t in tiles])
            box, sub = potong_lalo(info, plane, ltu, lsl, loB, loT)
            bands[band] = (info, sub, box)
        except Exception:
            import traceback; traceback.print_exc()
            print("  B%02d GAGAL (kotak)" % band)
    if 13 not in bands or 3 not in bands:
        print("  ! kotak butuh B03 dan B13 minimal")
        return None
    info13, b13, box13 = bands[13]
    tb13 = tb_ir(info13, b13)
    tb7 = tb_ir(*bands[7][:2]) if 7 in bands else tb13
    ta13 = (np.clip((tb13 - 250) / 70.0, 0, 1) * 255).astype(np.uint8)
    ta07 = (np.clip((tb7 - 240) / 120.0, 0, 1) * 255).astype(np.uint8)
    topeng = (tb13 < 265).astype(np.uint8) * 255
    vis = [b for b in (1, 2, 3) if b in bands]
    th = max(bands[b][1].shape[0] for b in vis)
    tc = max(bands[b][1].shape[1] for b in vis)
    def ke_grid(item):
        bx, arr = item[2], item[1]
        if arr.shape == (th, tc):
            return np.asarray(arr, dtype=np.float64), bx
        s = float(arr.shape[1]) / tc
        l0, _, c0, _ = bx
        bx2 = (int(round(l0 / s)), int(round(l0 / s + (th - 1))),
               int(round(c0 / s)), int(round(c0 / s + (tc - 1))))
        return np.asarray(Image.fromarray(arr).resize((tc, th), Image.BILINEAR), dtype=np.float64), bx2
    chs = {b: ke_grid(bands[b]) for b in vis}
    komposit = None
    if 1 in chs and 2 in chs and 3 in chs:
        ch1, bx1 = chs[1]; ch2, _ = chs[2]; ch3, _ = chs[3]
        semua = np.concatenate([ch1.ravel(), ch2.ravel(), ch3.ravel()])
        lo, hi = np.nanpercentile(semua, 2), np.nanpercentile(semua, 98)
        komposit = (np.clip((np.dstack([ch3, ch2, ch1]) - lo) / (hi - lo), 0, 1) * 255).astype(np.uint8)
        info_k, box_k = bands[1][0], bx1
    elif 3 in chs:
        komposit = (selip(bands[3][1]) * 255).astype(np.uint8)
        info_k, box_k = bands[3][0], bands[3][2]
    pan = []
    judul_tc = "True color B03/B02/B01 (peregangan bersama)" if (1 in chs and 2 in chs) else "B03 saja (B01/B02 belum ada)"
    if komposit is not None:
        pan.append((judul_tc, komposit, info_k, box_k))
    b3info, b3arr, b3box = bands[3]
    pan.append(("B03 0.64u (2-98%)", (selip(b3arr) * 255).astype(np.uint8), b3info, b3box))
    pan.append(("B13 10.8u TB (250-320 K)", ta13, info13, box13))
    pan.append(("topeng awan dingin: TB13 < 265 K", topeng, info13, box13))
    if 7 in bands:
        pan.append(("B07 3.9u TB (240-360 K; SIANG tercemar surya)", ta07, bands[7][0], bands[7][2]))
    if 4 in bands:
        pan.append(("B04 0.86u NIR (2-98%)", (selip(bands[4][1]) * 255).astype(np.uint8), bands[4][0], bands[4][2]))
    tile = 620
    W = 1380
    Himg = 92 + ((len(pan) + 1) // 2) * (tile + 34)
    im = Image.new("RGB", (W, Himg), (16, 18, 26))
    dr = ImageDraw.Draw(im)
    try:
        f = ImageFont.truetype("consola.ttf", 14)
        fb = ImageFont.truetype("consolab.ttf", 18)
    except Exception:
        f = fb = ImageFont.load_default()
    dr.text((10, 4), "%s - kotak %s (lat %+.1f .. %+.1f, lon %.1f .. %.1f)" % (label, nm_kotak, ltu, lsl, loB, loT), fill=(240, 238, 225), font=fb)
    dr.text((10, 26), "Jam 03:00 UTC = 10:00 WIB. Kisi kuning tiap 1 derajat; pantai garis oranye.", font=f, fill=(200, 205, 215))
    for idx, (judul, arr, binfo, bbox) in enumerate(pan):
        r, c8 = divmod(idx, 2)
        x, y0 = 10 + c8 * (tile + 70), 52 + r * (tile + 34)
        dr.text((x, y0), judul, fill=(225, 228, 235), font=f)
        ph, pw = arr.shape[:2]
        scale = tile / max(pw, ph)
        pw2, ph2 = max(1, int(pw * scale)), max(1, int(ph * scale))
        pil = Image.fromarray(arr).resize((pw2, ph2))
        dr.rectangle([x - 1, y0 + 20, x + 1 + pw2, y0 + 22 + ph2], outline=(90, 95, 105))
        im.paste(pil.convert("RGB"), (x, y0 + 20))
        lay = gambar_kisi_lay(binfo, bbox, pw2, ph2, scale, kotak)
        im.paste(lay, (x, y0 + 20), lay)
    nama = os.path.join(OUT, "fm1_%s_%s.png" % (label, nm_kotak))
    im.save(nama)
    print("  ->", nama)
    return nama
