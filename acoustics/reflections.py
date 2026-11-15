"""First-order specular reflections, RL 901K L/R -> listening position (image-source method).

    python3 acoustics/reflections.py  -> acoustics/out/first_reflections.json
Level = spherical-spreading only (no surface absorption, no loudspeaker directivity); the
off-axis angle of each departing ray is reported because the RL 901K's coaxial directivity
will attenuate wide-angle reflections by an UNKNOWN amount (no polar data in hand).
"""
import json, math, os
import numpy as np
from geometry import *
OUT = os.path.join(ROOT, "acoustics/out"); os.makedirs(OUT, exist_ok=True)
rows = []
for sk, S in SPK.items():
    axis = (EAR - S) / np.linalg.norm(EAR - S)
    direct = np.linalg.norm(EAR - S)
    for s in SURF:
        n, p0 = s["n"], s["p0"]
        dist = np.dot(S - p0, n)
        Simg = S - 2 * dist * n
        dvec = EAR - Simg; denom = np.dot(dvec, n)
        if abs(denom) < 1e-9: continue
        t = np.dot(p0 - Simg, n) / denom
        if not (0 < t < 1): continue
        Pt = Simg + t * dvec
        if not s["inside"](Pt): continue
        path = np.linalg.norm(EAR - Simg)
        out_dir = (Pt - S) / np.linalg.norm(Pt - S)
        off = math.degrees(math.acos(np.clip(np.dot(out_dir, axis), -1, 1)))
        blocked = seg_hits_box(S, Pt, CONSOLE_BOX) or seg_hits_box(Pt, EAR, CONSOLE_BOX)
        rows.append({"speaker": sk, "surface": s["name"], "point": [round(float(v), 2) for v in Pt],
                     "delay_ms": round((path - direct) / C_SOUND * 1000, 2), "level_dB_re_direct": round(20 * math.log10(direct / path), 1),
                     "off_axis_deg": round(off, 0), "lands_on": opening_at(s["name"], Pt) or "surface", "console_shadowed": bool(blocked),
                     "comb_first_notch_Hz": round(C_SOUND / (2 * (path - direct)), 0)})
rows.sort(key=lambda r: (r["delay_ms"]))
json.dump({"listening_position": EAR.tolist(), "speakers": {k: v.tolist() for k, v in SPK.items()}, "reflections": rows}, open(os.path.join(OUT, "first_reflections.json"), "w"), indent=1)
for r in rows: print(f'{r["speaker"]} {r["surface"]:30s} P={r["point"]}  +{r["delay_ms"]:5.1f} ms {r["level_dB_re_direct"]:6.1f} dB  off-axis {r["off_axis_deg"]:4.0f}  {r["lands_on"]:16s} {"CONSOLE-SHADOW" if r["console_shadowed"] else ""}')
