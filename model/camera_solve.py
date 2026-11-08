"""Camera-constrained solve of the existing control-room section (Assignment 01).

Joint least-squares over (a) a parametric control-room cross-section and
(b) one pinhole camera per photograph, from hand-annotated 2D control points.

Inputs : model/annotations/*.json  (pixel coords in the 1600 px-wide review
         preview of each private source photo; photos themselves are NOT in git)
Output : model/solve_result.json   (parameters, cameras, per-point residuals)

Model frame (metres, right-handed, see docs/COORDINATE_SYSTEM.md):
  X across the building (0 = control-room interior face of the side wall that is
    on your LEFT when standing in the gable-end entry door looking in),
  Y along the building (0 = interior face of the control-room gable wall,
    +Y towards the intermediate zone / live room),
  Z up (0 = existing control-room floor surface).

Scale comes ONLY from the scan-labelled room width W (10.51 m, prior sigma 0.15 m)
and depth D (7.86 m). Every height is therefore a derived, photo-inferred value.
Run:  python3 model/camera_solve.py
"""
import json, glob, os, math
import numpy as np
from scipy.optimize import least_squares

HERE = os.path.dirname(os.path.abspath(__file__))
IMG_W, IMG_H = 1600.0, 1200.0

# ---- parametric section ---------------------------------------------------
PARAMS = {  # name: (initial, prior_mean or None, prior_sigma)
    # v0.2: W and D priors come from the NATIVE Polycam LiDAR mesh (model/scan_control_room_measurements.json),
    # replacing the screenshot labels (10.51 was not a wall-to-wall measurement). All heights stay FREE so the
    # photo solve remains an independent check of the scan's ceiling levels.
    "W":   (11.25, 11.25, 0.05),
    "D":   (8.19, 8.19, 0.05),
    "dsL": (2.3, None, None),      # beam/post line inset from LEFT (X=0) wall
    "dsR": (2.0, None, None),      # beam/post line inset from RIGHT (X=W) wall
    "hloR": (2.3, None, None),     # low ceiling at the right wall (photo point k2)
    "hbbL": (2.1, None, None),     # beam underside / post top, left line
    "hbbR": (2.1, None, None),     # beam underside / post top, right line
    "hbL": (2.5, None, None),      # foot of left sloped ceiling
    "hbR": (2.4, None, None),      # foot of right sloped ceiling
    "hc":  (4.0, None, None),      # flat central ceiling (scan: 4.105, NOT used as prior)
    "wc":  (3.4, None, None),      # width of flat central ceiling
    "xf":  (5.9, None, None),      # X of flat-ceiling centreline (asymmetry allowed)
    "ypl": (4.3, None, None),
    "ypr": (4.3, None, None),
}
# MODE "scan_fixed" (default, v0.2): section geometry FIXED to the native-scan measurements
# (model/scan_control_room_measurements.json, read off its ceiling profile) and only cameras,
# post Y and opening positions are solved. The photos then TEST the scan-built model.
# MODE "photo_only": v0.1 behaviour (all heights free), kept for comparison.
MODE = os.environ.get("BG_SOLVE_MODE", "fused")
SCAN_SECTION = {   # metres, from scan ceiling profile measured from the left (X=0) wall; +/- ~0.03-0.05
    "W": 11.25, "D": 8.19, "hc": 4.105, "wc": 3.30, "xf": 5.90,
    "dsL": 2.50, "hbL": 2.55, "hbbL": 2.16,
    "dsR": 2.15, "hbR": 2.60, "hbbR": 2.23, "hloR": 2.30,
}
# sigma: 0.03 m for directly measured planes/walls; 0.10 m for breakpoints read off the
# smoothed, decimated mesh profile (beam steps, slope feet, flat-ceiling edges)
SCAN_SIGMA = {"W": 0.03, "D": 0.03, "hc": 0.03, "hloR": 0.07,
              "wc": 0.10, "xf": 0.10, "dsL": 0.10, "dsR": 0.10, "hbL": 0.10, "hbR": 0.10, "hbbL": 0.10, "hbbR": 0.10}
if MODE == "photo_only":
    # Truly scan-independent shape: no section priors at all. W is FIXED only as a gauge (any
    # value gives identical ratios). Compare RATIOS (h/W, D/W, ...) with the scan - absolute
    # metres from this mode are not independent evidence. (Review finding G1-02.)
    PARAMS["W"] = (11.25, 11.25, 1e-4)
    PARAMS["D"] = (8.19, None, None)
elif MODE == "scan_fixed":
    for k, v in SCAN_SECTION.items(): PARAMS[k] = (v, v, 0.005)
elif MODE == "fused":
    for k, v in SCAN_SECTION.items(): PARAMS[k] = (v, v, SCAN_SIGMA[k])
PNAMES = list(PARAMS)

def rot(rx, ry, rz):
    cx, sx, cy, sy, cz, sz = map(lambda f: f, (math.cos(rx), math.sin(rx), math.cos(ry), math.sin(ry), math.cos(rz), math.sin(rz)))
    Rx = np.array([[1,0,0],[0,cx,-sx],[0,sx,cx]]); Ry = np.array([[cy,0,sy],[0,1,0],[-sy,0,cy]])
    Rz = np.array([[cz,-sz,0],[sz,cz,0],[0,0,1]])
    return Rz @ Ry @ Rx

def project(cam, P):
    """cam = [tx,ty,tz, yaw, pitch, roll, f_px]. Camera looks along +Y_world at yaw=0."""
    t = np.array(cam[:3]); yaw, pitch, roll, f = cam[3:7]
    # world->camera: camera axes (x right, y down, z forward)
    R_wc = rot(pitch, 0, 0) @ rot(0, 0, 0)  # placeholder, replaced below
    cy_, sy_ = math.cos(yaw), math.sin(yaw)
    fwd = np.array([math.sin(yaw)*math.cos(pitch), math.cos(yaw)*math.cos(pitch), math.sin(pitch)])
    right0 = np.array([cy_, -sy_, 0.0])
    up0 = np.cross(right0, fwd)
    cr, sr = math.cos(roll), math.sin(roll)
    right = cr*right0 + sr*up0; up = -sr*right0 + cr*up0
    d = np.asarray(P) - t
    xc, yc, zc = d @ right, -(d @ up), d @ fwd
    return np.array([IMG_W/2 + f*xc/zc, IMG_H/2 + f*yc/zc]), zc

def f35_to_px(f35):  # 35 mm-equivalent defined on the 43.27 mm diagonal
    return f35 / 43.27 * math.hypot(IMG_W, IMG_H)

def evaluate(expr, p, extra):
    env = dict(p); env.update(extra); return [eval(e, {"math": math}, env) for e in expr]

def load():
    anns = []
    for fn in sorted(glob.glob(os.path.join(HERE, "annotations", "*.json"))):
        a = json.load(open(fn))
        if a.get("exclude"):
            print(f"[excluded] {a['id']}: {a.get('exclude_reason','')}"); continue
        anns.append(a)
    return anns

def build(anns):
    names = list(PNAMES); x0 = [PARAMS[n][0] for n in PNAMES]
    for a in anns:
        for k, v in a["camera_init"].items():
            if k == "f":  # one focal length per physical lens (same 35mm-equiv EXIF)
                k_lens = f"lens{a['exif_f35']}.f"
                if k_lens not in names: names.append(k_lens); x0.append(v)
                continue
            names.append(f"{a['id']}.{k}"); x0.append(v)
        for k, v in a.get("nuisance", {}).items():
            nm = k if k.startswith("g_") else f"{a['id']}.{k}"   # g_* = shared across photos
            if nm not in names: names.append(nm); x0.append(v)
    return names, np.array(x0, float)

def residuals(x, names, anns, detail=False):
    v = dict(zip(names, x)); p = {n: v[n] for n in PNAMES}
    res, rows = [], []
    for a in anns:
        cid = a["id"]
        cam = [v[f"{cid}.{k}"] for k in ("tx","ty","tz","yaw","pitch","roll")] + [v[f"lens{a['exif_f35']}.f"]]
        extra = {k: v[k if k.startswith("g_") else f"{cid}.{k}"] for k in a.get("nuisance", {})}
        for pt in a["points"]:
            P = evaluate(pt["xyz"], p, extra)
            uv, depth = project(cam, P)
            r = (uv - np.array(pt["uv"])) / pt.get("sigma_px", 4.0)
            res += list(r)
            rows.append({"photo": cid, "id": pt["id"], "desc": pt["desc"], "obs": pt["uv"],
                         "pred": [round(float(uv[0]),1), round(float(uv[1]),1)],
                         "err_px": round(float(np.linalg.norm(uv-np.array(pt["uv"]))),1)})
        # focal prior (EXIF 35 mm equivalent, +/-6 %)
        f0 = f35_to_px(a["exif_f35"]); res.append((cam[6]-f0)/(a.get("focal_sigma_frac", 0.06)*f0))
    for n in PNAMES:
        _, m, s = PARAMS[n]
        if m is not None: res.append((p[n]-m)/s)
    return (np.array(res), rows) if detail else np.array(res)

def main():
    anns = load(); names, x0 = build(anns)
    sol = least_squares(residuals, x0, args=(names, anns), loss="soft_l1", f_scale=2.0)
    r, rows = residuals(sol.x, names, anns, detail=True)
    # covariance -> 1-sigma parameter uncertainty (only meaningful as a relative indicator)
    J = sol.jac; dof = max(1, len(r) - len(sol.x))
    s2 = float(r @ r) / dof
    try:
        cov = np.linalg.pinv(J.T @ J) * s2; sig = np.sqrt(np.clip(np.diag(cov), 0, None))
    except Exception:
        sig = np.full(len(sol.x), np.nan)
    out = {"params": {n: {"value": round(float(sol.x[i]),3), "sigma": round(float(sig[i]),3)} for i, n in enumerate(names)},
           "rms_px": round(float(np.sqrt(np.mean([row["err_px"]**2 for row in rows]))),2),
           "max_px": max(row["err_px"] for row in rows), "points": rows, "status": sol.message}
    out["mode"] = MODE
    json.dump(out, open(os.path.join(HERE, "solve_result.json" if MODE == "fused" else f"solve_result_{MODE}.json"), "w"), indent=1)
    for n in names: print(f"{n:16s} {out['params'][n]['value']:9.3f}  ±{out['params'][n]['sigma']:.3f}")
    print("RMS px", out["rms_px"], "max", out["max_px"])
    for row in sorted(rows, key=lambda r: -r["err_px"])[:8]: print("  worst", row["photo"], row["id"], row["err_px"], row["desc"])

if __name__ == "__main__":
    main()
