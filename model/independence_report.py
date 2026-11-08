"""Scale-free comparison: photo-only solve (no scan priors) vs native scan (review G1-02).

    python3 model/independence_report.py  -> model/independence_report.json
Ratios to room width W are independent of the chosen gauge, so they are the only fair
photo-vs-scan comparison. Also reports a held-out test: with the section frozen to the
scan, each camera is fitted on half of its points and scored on the other half.
"""
import json, os, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
po = {k: v["value"] for k, v in json.load(open(os.path.join(HERE, "solve_result_photo_only.json")))["params"].items()}
sc = json.load(open(os.path.join(HERE, "scan_control_room_measurements.json")))
scan = {"D": sc["depth_gable_to_partition"], "hc": sc["flat_ceiling"], "hloR": sc["low_ceiling_right"], "W": sc["width_wall_to_wall"]}
rows = []
for k in ("D", "hc", "hloR"):
    rp, rs = po[k] / po["W"], scan[k] / scan["W"]
    rows.append({"ratio": f"{k}/W", "photo_only": round(rp, 4), "scan": round(rs, 4), "diff_pct": round(100 * (rp - rs) / rs, 1)})
# held-out test
import importlib.util, sys
os.environ["BG_SOLVE_MODE"] = "scan_fixed"; sys.path.insert(0, HERE)
import camera_solve as cs
from scipy.optimize import least_squares
anns = cs.load(); base = {k: v[0] for k, v in cs.PARAMS.items()}
hold = []
for a in anns:
    pts = a["points"]; nkeys = set(a.get("nuisance", {}))
    pure = [p for p in pts if not any(n in e for e in p["xyz"] for n in nkeys) and "ypl" not in str(p["xyz"]) and "ypr" not in str(p["xyz"])]
    test = pure[1::2]; fit = [p for p in pts if p not in test]   # hold out every 2nd pure-geometry point
    keys = ["tx", "ty", "tz", "yaw", "pitch", "roll"]; nk = list(a.get("nuisance", {}).keys())
    x0 = [a["camera_init"][k] for k in keys] + [a["nuisance"][k] for k in nk]
    f = cs.f35_to_px(a["exif_f35"])
    def res(x, subset):
        cam = list(x[:6]) + [f]; extra = dict(zip(nk, x[6:])); r = []
        for p in subset:
            P = cs.evaluate(p["xyz"], base, extra); uv, _ = cs.project(cam, P); r += list(uv - np.array(p["uv"]))
        return np.array(r)
    sol = least_squares(lambda x: res(x, fit), x0, loss="soft_l1", f_scale=4)
    # nuisance-only points in the test set use values fitted on the fit set (if seen) else are uninformative
    e = res(sol.x, test).reshape(-1, 2); err = np.linalg.norm(e, axis=1)
    hold.append({"photo": a["id"], "fit_points": len(fit), "test_points": len(test),
                 "test_rms_px": round(float(np.sqrt(np.mean(err**2))), 1), "test_median_px": round(float(np.median(err)), 1)})
out = {"scale_free_photo_only_vs_scan": rows, "holdout_scan_geometry": hold,
       "note": "Holdout: section frozen to scan breakpoints (scan_fixed); camera (and opening nuisances) fitted on all points except every 2nd point that depends ONLY on the scan section (walls/ceiling/beam corners); those held-out points are then predicted. Small samples - indicative only."}
json.dump(out, open(os.path.join(HERE, "independence_report.json"), "w"), indent=1)
print(json.dumps(out, indent=1))
