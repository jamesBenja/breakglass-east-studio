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
    "W":   (10.51, 10.51, 0.15),   # scan label (overhead + front view 10.38)
    "D":   (7.86, 7.86, 0.15),     # scan label
    "ds":  (1.5, None, None),      # inset of beam/post line from side walls
    "hlo": (2.3, None, None),      # low side ceiling at the side wall
    "hbb": (2.2, None, None),      # underside of beam band (post tops)
    "hb":  (2.6, None, None),      # top of beam band = foot of sloped ceiling
    "hc":  (4.0, None, None),      # flat central ceiling
    "wc":  (4.5, None, None),      # width of flat central ceiling
    "ypl": (3.9, None, None),      # Y of post on X=ds line (shared across photos)
    "ypr": (3.9, None, None),      # Y of post on X=W-ds line
}
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
    json.dump(out, open(os.path.join(HERE, "solve_result.json"), "w"), indent=1)
    for n in names: print(f"{n:16s} {out['params'][n]['value']:9.3f}  ±{out['params'][n]['sigma']:.3f}")
    print("RMS px", out["rms_px"], "max", out["max_px"])
    for row in sorted(rows, key=lambda r: -r["err_px"])[:8]: print("  worst", row["photo"], row["id"], row["err_px"], row["desc"])

if __name__ == "__main__":
    main()
