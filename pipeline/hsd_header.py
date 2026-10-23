# -*- coding: utf-8 -*-
# Pembaca header HSD mini (disalin struktur dari satpy/readers/ahi_hsd.py, silakan cek satpy MIT/Apache-2.0)
import urllib.request, bz2, numpy as np, datetime, json, sys

BASIC = np.dtype([("hblock_number","u1"),("blocklength","<u2"),("total_number_of_hblocks","<u2"),("byte_order","u1"),("satellite","S16"),("proc_center_name","S16"),("observation_area","S4"),("other_observation_info","S2"),("observation_timeline","<u2"),("observation_start_time","f8"),("observation_end_time","f8"),("file_creation_time","f8"),("total_header_length","<u4"),("total_data_length","<u4"),("quality_flag1","u1"),("quality_flag2","u1"),("quality_flag3","u1"),("quality_flag4","u1"),("file_format_version","S32"),("file_name","S128"),("spare","S40")])
DATA = np.dtype([("hblock_number","u1"),("blocklength","<u2"),("number_of_bits_per_pixel","<u2"),("number_of_columns","<u2"),("number_of_lines","<u2"),("compression_flag_for_data","u1"),("spare","S40")])
PROJ = np.dtype([("hblock_number","u1"),("blocklength","<u2"),("sub_lon","f8"),("CFAC","<u4"),("LFAC","<u4"),("COFF","f4"),("LOFF","f4"),("distance_from_earth_center","f8"),("earth_equatorial_radius","f8"),("earth_polar_radius","f8"),("req2_rpol2_req2","f8"),("rpol2_req2","f8"),("req2_rpol2","f8"),("coeff_for_sd","f8"),("resampling_types","<i2"),("resampling_size","<i2"),("spare","S40")])
NAV = np.dtype([("hblock_number","u1"),("blocklength","<u2"),("navigation_info_time","f8"),("SSP_longitude","f8"),("SSP_latitude","f8"),("distance_earth_center_to_satellite","f8"),("nadir_longitude","f8"),("nadir_latitude","f8"),("sun_position","f8",(3,)),("moon_position","f8",(3,)),("spare","S40")])
CALB = np.dtype([("hblock_number","u1"),("blocklength","<u2"),("band_number","<u2"),("central_wave_length","f8"),("valid_number_of_bits_per_pixel","<u2"),("count_value_error_pixels","<u2"),("count_value_outside_scan_pixels","<u2"),("gain_count2rad_conversion","f8"),("offset_count2rad_conversion","f8")])
IRCAL = np.dtype([("c0_rad2tb_conversion","f8"),("c1_rad2tb_conversion","f8"),("c2_rad2tb_conversion","f8"),("c0_tb2rad_conversion","f8"),("c1_tb2rad_conversion","f8"),("c2_tb2rad_conversion","f8"),("speed_of_light","f8"),("planck_constant","f8"),("boltzmann_constant","f8"),("spare","S40")])
VISCAL = np.dtype([("coeff_rad2albedo_conversion","f8"),("coeff_update_time","f8"),("cali_gain_count2rad_conversion","f8"),("cali_offset_count2rad_conversion","f8"),("spare","S80")])
SEG = np.dtype([("hblock_number","u1"),("blocklength","<u2"),("total_number_of_segments","u1"),("segment_sequence_number","u1"),("first_line_number_of_image_segment","u2"),("spare","S40")])

def parse_header_full(b, upto=None):
    """Parsing bertahap (urutan blok menurut satpy ahi_hsd.py)."""
    buf = np.frombuffer(b, dtype=np.uint8)
    pos = 0
    b1 = np.frombuffer(b[pos:pos+BASIC.itemsize], dtype=BASIC)[0]; pos += int(b1["blocklength"]); h1 = b1
    b2 = np.frombuffer(b[pos:pos+DATA.itemsize], dtype=DATA)[0]
    hdl = int(b1["total_header_length"])
    b2l = int(b2["blocklength"]); pos += b2l
    if upto is None or upto < hdl:
        b3 = np.frombuffer(b[pos:pos+PROJ.itemsize], dtype=PROJ)[0]; pos += int(b3["blocklength"])
        b4 = np.frombuffer(b[pos:pos+NAV.itemsize], dtype=NAV)[0]; pos += int(b4["blocklength"])
        b5 = np.frombuffer(b[pos:pos+CALB.itemsize], dtype=CALB)[0]; pos += int(b5["blocklength"])
        band = int(b5["band_number"])
        if band < 7:
            cal = np.frombuffer(b[pos:pos+VISCAL.itemsize], dtype=VISCAL)[0]; pos += int(VISCAL.itemsize)
        else:
            cal = np.frombuffer(b[pos:pos+IRCAL.itemsize], dtype=IRCAL)[0]; pos += int(IRCAL.itemsize)
        # blok 6 intercalibrasi
        b6 = np.frombuffer(b[pos:pos+1], dtype=np.uint8)[0]
        if int(b6) == 6:
            b6h = np.dtype([("hblock_number","u1"),("blocklength","<u2")])
            blen = int(np.frombuffer(b[pos:pos+3], dtype=b6h)[0]["blocklength"])
            pos += blen
        else:
            pos -= 1
        # blok 7 informasi segmen
        seg = None
        if buf[pos] == 7:
            seg = np.frombuffer(b[pos:pos+SEG.itemsize], dtype=SEG)[0]
            pos += int(seg["blocklength"])
        else:
            # blok 7 tidak ada (2019: satu segmen utuh) - lewati gabung
            while pos < hdl and buf[pos] != 7:
                pos += 1
            if pos < hdl:
                seg = np.frombuffer(b[pos:pos+SEG.itemsize], dtype=SEG)[0]
                pos += int(seg["blocklength"])
        seg_extra = None
        if seg is not None and int(seg["total_number_of_segments"]) == 0:
            # beberapa arsip tidak memakai blok segmen; tangani offline
            pass
    info = dict(
        block1_len=int(h1["blocklength"]), block2_len=int(b2["blocklength"]),
        cols=int(b2["number_of_columns"]), lines=int(b2["number_of_lines"]),
        bits=int(b2["number_of_bits_per_pixel"]), compression=int(b2["compression_flag_for_data"]),
        proj_sub_lon=float(b3["sub_lon"]), cfac=int(b3["CFAC"]), lfac=int(b3["LFAC"]),
        coff=float(b3["COFF"]), loff=float(b3["LOFF"]),
        dist_center=float(b3["distance_from_earth_center"]), a=float(b3["earth_equatorial_radius"]), b=float(b3["earth_polar_radius"]),
        band=int(b5["band_number"]), cwl=float(b5["central_wave_length"]),
        gain=float(b5["gain_count2rad_conversion"]), off=float(b5["offset_count2rad_conversion"]),
        count_err=int(b5["count_value_error_pixels"]), count_out=int(b5["count_value_outside_scan_pixels"]),
        total_header=int(h1["total_header_length"]), total_data=int(h1["total_data_length"]),
        header_pos=pos,
        seg_total=(int(seg["total_number_of_segments"]) if seg is not None else None),
        seg_seq=(int(seg["segment_sequence_number"]) if seg is not None else None),
        seg_first_line=(int(seg["first_line_number_of_image_segment"]) if seg is not None else None),
    )
    return info

def fetch_head(url, nbytes=120000):
    r = urllib.request.Request(url, headers={"Range": "bytes=0-%d" % nbytes})
    raw = urllib.request.urlopen(r, timeout=120).read()
    d = bz2.BZ2Decompressor()
    out = b""
    try:
        out = d.decompress(raw)
    except Exception as e:
        out = d.decompress(raw)
    return out

if __name__ == "__main__":
    for url in sys.argv[1:]:
        try:
            out = fetch_head(url)
            info = parse_header_full(out[:4000])
            print(url.split("/")[-1])
            for k, v in info.items():
                print("  ", k, v)
        except Exception as e:
            print(url, "ERROR", repr(e))
