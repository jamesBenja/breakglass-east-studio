"""Whole-building measurements from the native mesh (live room, middle zone, loft).

    python3 -I model/scan_measure_building.py -> model/scan_building_measurements.json
Global scan frame (scan_analysis.py), Z relative to the CONTROL-ROOM floor.
Per-zone values use local histogram peaks; accuracy as for the control room
(fit scatter few cm; systematic phone-LiDAR scale/drift ~1-2 %, see ledger X6).
"""
import json, os, numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = np.load(os.path.join(ROOT, "inputs/private/scan/samples.npz")); P = d["pts"]; nz = d["nz"]
X, Y, Z = P[:, 0], P[:, 1], P[:, 2] + 2.335
def pk(v, rng, b=0.01):
    if len(v) == 0: return None
    h, e = np.histogram(v, bins=np.arange(rng[0], rng[1], b)); return round(float(e[np.argmax(h)] + b/2), 3)
def prof(ymin, ymax, kind, xr=(-7, 7), step=0.25, zr=(-1, 6)):
    out = []
    for x in np.arange(xr[0], xr[1], step):
        m = (Y > ymin) & (Y < ymax) & (X >= x) & (X < x + step) & (Z > zr[0]) & (Z < zr[1])
        m &= (nz > 0.7) if kind == "up" else (nz < -0.7)
        if m.sum() > 20: out.append([round(float(x + step/2), 2), round(float(np.percentile(Z[m], 50)), 2)])
    return out
R = {}
R["live_floor"] = pk(Z[(Y > 9) & (Y < 14) & (nz > 0.9)], (-1, 1))
R["live_flat_ceiling"] = pk(Z[(Y > 9) & (Y < 14) & (nz < -0.9) & (np.abs(X) < 1)], (2.5, 5))
R["live_low_ceiling_left"] = pk(Z[(Y > 9) & (Y < 14) & (nz < -0.9) & (X < -4.5) & (X > -5.8)], (1.5, 3.5))
R["live_low_ceiling_right"] = pk(Z[(Y > 9) & (Y < 14) & (nz < -0.9) & (X > 3.5) & (X < 5.2)], (1.5, 3.5))
m = (Y > 9.5) & (Y < 13.5) & (Z - R["live_floor"] > 1.5) & (Z - R["live_floor"] < 1.9) & (np.abs(nz) < 0.2)
R["live_wall_left_x"] = pk(X[m & (X < -5)], (-7, -5)); R["live_wall_right_x"] = pk(X[m & (X > 4.5)], (4.5, 7))
m = (np.abs(X) < 2) & (Z > R["live_floor"] + 2.5) & (Z < R["live_floor"] + 4) & (np.abs(nz) < 0.2)
R["live_gable_y"] = pk(Y[m & (Y > 14)], (14, 16.5))
R["underloft_ceiling"] = pk(Z[(Y > 2) & (Y < 7) & (nz < -0.9) & (np.abs(X) < 2.5)], (1.8, 3.4))
R["middle_floor"] = pk(Z[(Y > -6) & (Y < 0) & (nz > 0.9) & (np.abs(X) < 0.6)], (-1, 1))
R["middle_ceiling_corridor"] = pk(Z[(Y > -6) & (Y < 0) & (nz < -0.9) & (np.abs(X) < 0.6)], (1.8, 3.4))
R["loft_deck"] = pk(Z[(Y > -5) & (Y < 6) & (nz > 0.9) & (X > -2) & (X < 3)], (2.2, 3.6))
R["loft_transverse_y0_deck"] = prof(-1, 1, "up", zr=(2.2, 6))
R["loft_transverse_y0_roof"] = prof(-1, 1, "down", zr=(2.7, 6.5))
R["live_transverse_y11_ceiling"] = prof(10.5, 11.5, "down", zr=(1.5, 5))
# garage door: reveal / void beyond live gable plane
g = R["live_gable_y"]; m = (Y > g + 0.06) & (Y < g + 1.5) & (Z > R["live_floor"] + 0.05) & (Z < R["live_floor"] + 4.5)
if m.sum():
    H, xe, ze = np.histogram2d(X[m], Z[m], bins=[np.arange(-7, 7, 0.1), np.arange(-1, 5, 0.1)])
    occ = H > 3; xs = np.nonzero(occ.any(1))[0]; zs = np.nonzero(occ.any(0))[0]
    R["beyond_live_gable_extent"] = {"x": [round(xe[xs.min()], 2), round(xe[xs.max()+1], 2)], "z": [round(ze[zs.min()], 2), round(ze[zs.max()+1], 2)], "note": "samples beyond the gable plane: garage opening reveal / exterior apron captured through the open door"}
json.dump(R, open(os.path.join(ROOT, "model/scan_building_measurements.json"), "w"), indent=1)
for k, v in R.items():
    print(k, v if not isinstance(v, list) else v[::2])
