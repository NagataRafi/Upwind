import sys, os
sys.path.insert(0, r'C:\Users\ADMIN\upwind_proj\pipeline')
import kotak_fm1 as K
import olah_himawari_fm1 as O

CASES = [
    ("asap_2019-09-14", r"D:\upwind_raw\noaa-himawari8\asap_2019-09-14"),
    ("bersih_2019-10-15", r"D:\upwind_raw\noaa-himawari8\bersih_2019-10-15"),
    ("awan_2019-01-15", r"D:\upwind_raw\noaa-himawari8\awan_2019-01-15"),
    ("terkini_2026-10-23", r"D:\upwind_raw\noaa-himawari9\terkini_2026-10-23"),
]
for label, folder in CASES:
    if not os.path.isdir(folder):
        continue
    for nm in ("riau", "kalteng"):
        try:
            K.render_kotak(label, folder, nm)
        except Exception as e:
            import traceback; traceback.print_exc()
    O.render_kasus(label, folder)
print("SEMUA_KOTAK_OK")
