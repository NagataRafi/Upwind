# -*- coding: utf-8 -*-
"""Unduh subset Himawari untuk pemeriksaan kelayakan FR-M1.

Sumber [Literatur] pemilihan tanggal (satu kalimat):
- Wikipedia "2019 Southeast Asian haze": 12 Sep 1.188 hotspot Kalimantan + 431 Sumatra; hujan mulai 24-25 Sep.
- PMC11531407 (Kalimantan): tanpa hujan 2-19 Sep, PM2.5 puncak 14-16 Sep; hujan tetap mulai 12 Okt.
Tanggal dipilih:
- asap: 2019-09-05, 2019-09-12, 2019-09-14 (puncak)
- kontrol bersih: 2019-10-15 (setelah hujan stabil)
- awan tebal tanpa asap: 2019-01-15 (musim hujan)
- terkini H9: 2026-10-23
Jam: 03:00 UTC (10:00 WIB).
"""
import os, sys, re, time, urllib.request, urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import DATA_ROOT
RAW = DATA_ROOT

def s3list(bkt, pfx, delim="/"):
    u = "https://%s.s3.amazonaws.com/?list-type=2&prefix=%s&max-keys=300" % (bkt, urllib.parse.quote(pfx))
    if delim:
        u += "&delimiter=/&delimiter1=/"
    t = None
    while True:
        r = urllib.request.urlopen(u, timeout=120)
        x = r.read().decode()
        return re.findall(r"<Key>([^<]+)</Key>", x)

def download(url, dest):
    if os.path.exists(dest):
        return "ada"
    t0 = time.time()
    r = urllib.request.urlopen(url, timeout=600)
    n = 0
    with open(dest + ".part", "wb") as f:
        while True:
            b = r.read(1 << 20)
            if not b:
                break
            f.write(b)
            n += len(b)
    os.rename(dest + ".part", dest)
    return "%.1f MB %d detik" % (n / 1e6, time.time() - t0)

CASES = [
    ("asap_2019-09-05",  "noaa-himawari8", "AHI-L1b-FLDK/2019/09/05/0300/"),
    ("asap_2019-09-12",  "noaa-himawari8", "AHI-L1b-FLDK/2019/09/12/0300/"),
    ("asap_2019-09-14",  "noaa-himawari8", "AHI-L1b-FLDK/2019/09/14/0300/"),
    ("bersih_2019-10-15","noaa-himawari8", "AHI-L1b-FLDK/2019/10/15/0300/"),
    ("awan_2019-01-15",  "noaa-himawari8", "AHI-L1b-FLDK/2019/01/15/0300/"),
    ("terkini_2026-10-23","noaa-himawari9", "AHI-L1b-FLDK/2026/10/23/0300/"),
]

def pilih(nama, tanggal2019):
    """Pilih berkas band/segmen. Kembalikan daftar (band, pilihan berkas)."""
    pt = [k for k in nama if "_B0" in k or "_B1" in k]
    def cari(bx, rr=None, seg=None):
        c = [k for k in pt if re.search(r"_B%02d_FLDK_(R\d\d)_([S\d]+)\.DAT\.bz2" % bx, k)]
        if rr:
            c = [k for k in c if "_%s_" % rr in k]
        if seg:
            c = [k for k in c if seg in k]
        return sorted(c)
    hasil = []
    for bx in (1, 2, 4):
        k = cari(bx, rr="R05" if not tanggal2019 else None) or cari(bx)
        if tanggal2019:
            k = sorted(cari(bx))
        else:
            # 2026: pilih segmen 5 & 6 (lat 6S-7N)
            k = cari(bx, seg="S05") + cari(bx, seg="S06")
        if not k:
            print("MAKAN KOSONG B%02d" % bx)
        hasil += k
    # B03: 2019 pakai R20 (kecil); 2026 0.5km segmen 5-6
    if tanggal2019:
        hasil += cari(3, rr="R20")
    else:
        k = cari(3, rr="R05", seg="S05") + cari(3, rr="R05", seg="S06")
        hasil += (k or cari(3, seg="S05") + cari(3, seg="S06"))
    hasil += cari(7, rr="R20", seg=None if tanggal2019 else "S05") + cari(7, rr="R20", seg="S06" if not tanggal2019 else None)
    hasil += cari(13, rr="R20", seg=None if tanggal2019 else "S05") + cari(13, rr="R20", seg="S06" if not tanggal2019 else None)
    unik = []
    for k in hasil:
        if k not in unik:
            unik.append(k)
    return unik

if __name__ == "__main__":
    for label, bkt, pfx in CASES:
        target = os.path.join(RAW, bkt, label)
        os.makedirs(target, exist_ok=True)
        tgl2019 = bkt.endswith("8")
        ks = s3list(bkt, pfx)
        k = pilih(ks, tgl2019)
        print("==", label, len(k), "berkas")
        for kk in k:
            d = os.path.join(target, kk.split("/")[-1])
            s = download("https://%s.s3.amazonaws.com/%s" % (bkt, kk), d)
            print("   ", kk.split("/")[-1], s)
        sys.stdout.flush()
    print("SELESAI")
