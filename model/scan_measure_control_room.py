"""Measure the control room directly from the native Polycam mesh samples (private input).

    python3 -I model/scan_analysis.py             # frame
    python3 -I model/scan_measure_control_room.py # needs inputs/private/scan/samples.npz
Writes model/scan_control_room_measurements.json (numbers only -> public-safe).
Method: room-local alignment from both side walls (least squares, Z 1.9-2.15 m band above
clutter), plane levels by histogram peaks of horizontal facets, ceiling profile by X bins,
posts by vertical-facet density away from walls.
"""
import json, os, numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = np.load(os.path.join(ROOT, "inputs/private/scan/samples.npz")); P = d["pts"].copy(); nz = d["nz"]
FZ = float(np.median(P[(P[:, 1] < -7) & (P[:, 1] > -14) & (nz > 0.9), 2])); P[:, 2] -= FZ
CR = (P[:, 1] > -15.7) & (P[:, 1] < -6.3)

def wallfit(xr):
    m = CR & (P[:, 2] > 1.9) & (P[:, 2] < 2.15) & (P[:, 0] > xr[0]) & (P[:, 0] < xr[1]) & (np.abs(nz) < 0.2) & (P[:, 1] > -14.8) & (P[:, 1] < -7.4)
    k, b = np.linalg.lstsq(np.c_[P[m, 1], np.ones(m.sum())], P[m, 0], rcond=None)[0]
    return k, b, float(np.std(P[m, 0] - (k*P[m, 1] + b))), int(m.sum())
kR, bR, sdR, nR = wallfit((5.5, 6.6)); kL, bL, sdL, nL = wallfit((-5.4, -4.4))
ang = float(np.degrees(np.arctan((kR + kL) / 2)))        # wall direction vs global Y
t = np.radians(ang); c, s = np.cos(t), np.sin(t)
cx, cy = 0.6, -11.1
x, y = P[:, 0] - cx, P[:, 1] - cy
X = c*x - s*y; Y = s*x + c*y; Z = P[:, 2]               # rotate by -ang -> walls parallel to Y
def pk(v, rng, b=0.01):
    h, e = np.histogram(v, bins=np.arange(rng[0], rng[1], b)); return float(e[np.argmax(h)] + b/2)
band = CR & (Z > 1.9) & (Z < 2.15) & (np.abs(nz) < 0.2) & (Y > -3.7) & (Y < 3.7)
xl = pk(X[band & (X < -4)], (-6.5, -4)); xr = pk(X[band & (X > 4)], (4, 7))
m2 = CR & (Z > 2.5) & (Z < 3.6) & (np.abs(nz) < 0.2) & (np.abs(X) < 1.5)
yg = pk(Y[m2 & (Y < -3)], (-4.8, -3)); yp = pk(Y[m2 & (Y > 3)], (3, 5))
# horizontal levels
def level(xr_, rng=(1.8, 4.6)):
    m = CR & (nz < -0.9) & (X > xl + xr_[0]) & (X < xl + xr_[1]) & (Y > yg + 0.6) & (Y < yp - 0.6)
    return pk(Z[m], rng)
mm = CR & (nz < -0.3) & (Y > yg + 1.5) & (Y < yp - 1.5)
prof = []
for xx in np.arange(xl, xr, 0.1):
    sl = mm & (X >= xx) & (X < xx + 0.1)
    if sl.sum() > 15:
        zz = Z[sl]; zz = zz[zz > 1.8]                     # ignore clutter tops below 1.8 m
        if len(zz) > 10: prof.append([round(float(xx + 0.05 - xl), 2), round(float(np.percentile(zz, 15)), 3)])
# posts
m = CR & (Z > 0.3) & (Z < 1.9) & (np.abs(nz) < 0.35) & (X > xl + 0.7) & (X < xr - 0.7) & (Y > yg + 0.7) & (Y < yp - 0.7)
H, xe, ye = np.histogram2d(X[m], Y[m], bins=[np.arange(xl, xr, 0.1), np.arange(yg, yp, 0.1)])
cols = []
for i in np.argsort(H.ravel())[::-1][:60]:
    a, b = np.unravel_index(i, H.shape); px, py = xe[a] + .05, ye[b] + .05
    if any(abs(px - q["x"]) < 0.6 and abs(py - q["y"]) < 0.6 for q in cols): continue
    col = m & (np.abs(X - px) < 0.1) & (np.abs(Y - py) < 0.1)
    cols.append({"x": float(px), "y": float(py), "x_from_left": round(float(px - xl), 2), "y_from_gable": round(float(py - yg), 2),
                 "n": int(H[a, b]), "z_min": round(float(Z[col].min()), 2), "z_max": round(float(Z[col].max()), 2)})
    if len(cols) >= 10: break
out = {"source": "native Polycam LiDAR mesh 2022-10-24 (sha256 fcec5a61c341...), 2.5M surface samples",
       "floor_z_mesh": round(FZ, 3), "local_alignment_deg": round(ang, 2),
       "wall_fit_sd_m": {"right": round(sdR, 3), "left": round(sdL, 3)},
       "width_wall_to_wall": round(xr - xl, 3), "depth_gable_to_partition": round(yp - yg, 3),
       "flat_ceiling": level((4.5, 7.5)), "low_ceiling_left": level((0.5, 1.8)), "low_ceiling_right": level((xr - xl - 1.6, xr - xl - 0.3)),
       "ceiling_profile_from_left_wall": prof, "vertical_columns": cols}
json.dump(out, open(os.path.join(ROOT, "model/scan_control_room_measurements.json"), "w"), indent=1)
for k, v in out.items():
    if k not in ("ceiling_profile_from_left_wall", "vertical_columns"): print(k, v)
for c_ in cols: print(c_)
