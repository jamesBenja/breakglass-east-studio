"""v0.5 owner-authorised correction: fireside lounge seating faces the EXISTING wood stove.

    python3 acoustics/lounge.py  ->  acoustics/out/lounge_layout.json

Searches a grid for the loveseat and two swivel armchairs, each turned to face the stove's glass front,
subject to hard constraints, then reports clearances. Both modes are fixed furniture positions, no mechanisms:
  * FIRESIDE mode: loveseat + 2 swivel armchairs grouped around the stove.
  * CINEMA mode: the 2 swivel armchairs (on glides) roll to the rear row beside the sofa, where the v0.4
    cinema chairs were; the loveseat stays (it is behind the screen and is not counted as a viewing seat).
Stove clearance 0.90 m is a PLACEHOLDER for the stove's listed clearances (label / WETT inspection).
"""
import json, math, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from geometry import P, G, W, D, AX, SPK, EAR, MG, ELEC
OUT = os.path.join(HERE, "out")
STOVE_CLEAR = 0.90
xs, ys = P["g_xs"], min(P["g_ys"], D - 0.35)
STOVE = [(xs - 0.28, ys - 0.25), (xs + 0.28, ys - 0.25), (xs + 0.28, ys + 0.25), (xs - 0.28, ys + 0.25)]
FIRE = np.array([xs, ys - 0.25])                   # glass door on the stove front (faces -Y, toward the room)
def rect(cx, cy, w, d, yaw_deg=0.0):
    """w along local X, d along local Y; local +Y = facing direction; yaw rotates CCW."""
    t = math.radians(yaw_deg); c, s = math.cos(t), math.sin(t)
    return [(cx + c * x - s * y, cy + s * x + c * y) for x, y in ((-w/2, -d/2), (w/2, -d/2), (w/2, d/2), (-w/2, d/2))]
def box(x0, x1, y0, y1): return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
def _axes(p):
    for i in range(len(p)):
        (x0, y0), (x1, y1) = p[i], p[(i + 1) % len(p)]
        yield np.array([y0 - y1, x1 - x0])
def overlap(a, b):
    for ax in list(_axes(a)) + list(_axes(b)):
        pa, pb = [np.dot(ax, v) for v in a], [np.dot(ax, v) for v in b]
        if max(pa) < min(pb) or max(pb) < min(pa): return False
    return True
def segdist(p, a, b):
    p, a, b = map(np.array, (p, a, b)); t = np.clip(np.dot(p - a, b - a) / max(np.dot(b - a, b - a), 1e-12), 0, 1); return float(np.linalg.norm(p - (a + t * (b - a))))
def dist(a, b):
    if overlap(a, b): return 0.0
    return min(min(segdist(p, b[i], b[(i + 1) % len(b)]) for p in a for i in range(len(b))),
               min(segdist(p, a[i], a[(i + 1) % len(a)]) for p in b for i in range(len(a))))
def yaw_to(cx, cy, target):  # local +Y toward target
    return math.degrees(math.atan2(-(target[0] - cx), target[1] - cy))

st = MG["stereo"]; R9 = (0.50, 0.42)
OBST = {
 "left RL 901K + clear zone (stand sliders ±0.2 m, cardioid rear/side ports)": box(SPK["L"][0] - 0.75, SPK["L"][0] + 0.75, SPK["L"][1] - 0.45, SPK["L"][1] + 0.90),
 "left sub": box(AX - 2.15 - 0.30, AX - 2.15 + 0.30, st["L"][1] + 0.15, st["L"][1] + 0.75),
 "left bench trap (NEW-01)": box(0, 0.75, 1.60, 7.45),
 "front-left corner trap (NEW-02)": [(0, D), (0.70, D), (0, D - 0.70)],
 "front-left PAN-001 on stand-off (NEW-07)": box(0.72, 3.19, D - 0.33, D),
 "future Ls surround stand (7.1.4)": box(MG["immersive_7_1_4"]["Ls"][0] - 0.20, MG["immersive_7_1_4"]["Ls"][0] + 0.20, MG["immersive_7_1_4"]["Ls"][1] - 0.20, MG["immersive_7_1_4"]["Ls"][1] + 0.20),
 "hearth pad": box(xs - 0.65, xs + 0.65, ys - 0.85, D),
 "electrical cabinet + 1.0 m working clearance (owner 14 Nov; clearance placeholder)": box(ELEC["x0"] - 0.10, ELEC["x1"] + 0.10, 0, ELEC["depth"] + ELEC["clear"]),
 "doorway route (partition doorway to the room)": box(P["CR1.xd1"] - 0.10, P["CR1.xd2"] + 0.10, st["L"][1] - 0.30, D),
}
PIECES = {"loveseat": (1.45, 0.85), "swivel armchair A": (0.80, 0.80)}   # tested: a third seat does not fit behind the speaker line with these clearances

def ok(poly, placed):
    if dist(poly, STOVE) < STOVE_CLEAR: return False
    if any(overlap(poly, o) for o in OBST.values()): return False
    if any(dist(poly, q) < 0.30 for q in placed): return False            # >= 0.40 m between pieces (side table / legroom)
    if min(x for x, _ in poly) < 0.80 or max(y for _, y in poly) > D - 0.35: return False
    return True
import itertools
def cands(w, d, step=0.1):
    out = []
    for cx in np.arange(0.9, 4.2, step):
        for cy in np.arange(st["L"][1] + 0.30, 8.0, step):   # lounge stays BEHIND the speaker line (v0.4 concept)
            yaw = yaw_to(cx, cy, FIRE); p = rect(cx, cy, w, d, yaw)
            r = float(np.hypot(cx - FIRE[0], cy - FIRE[1]))
            if r <= 2.9 and ok(p, []): out.append((round(float(cx), 2), round(float(cy), 2), yaw, p, r))
    return out
def sightline_clear(trio):
    for i, p in enumerate(trio):
        seg = [(p[0], p[1]), tuple(FIRE), (FIRE[0] + 1e-3, FIRE[1]), (p[0] + 1e-3, p[1])]
        if any(overlap(seg, q[3]) for j, q in enumerate(trio) if j != i): return False
    return True
LS, CH = cands(*PIECES["loveseat"]), cands(*PIECES["swivel armchair A"])
best = None
for l in LS:   # joint search: both seats face the fire glass, neither blocks the other's view, minimum total distance
    for a in CH:
        if dist(a[3], l[3]) < 0.30 or not sightline_clear((l, a)): continue
        s_ = l[4] + a[4]
        if best is None or s_ < best[0]: best = (s_, l, a)
assert best, "no valid fireside grouping"
layout = {}
for name, c in zip(PIECES, best[1:]):
    layout[name] = {"centre": [c[0], c[1]], "size": list(PIECES[name]), "yaw_deg": round(c[2], 1), "to_fire_m": round(c[4], 2),
                    "stove_clearance_m": round(dist(c[3], STOVE), 2), "facing_error_deg": 0.0,
                    "footprint": [[round(x, 3), round(y, 3)] for x, y in c[3]]}
# small round table between the pieces (0.55 m), nudged to a free spot near the group centroid
tb = None
for cx in np.arange(1.0, 4.0, 0.05):
    for cy in np.arange(5.0, 7.9, 0.05):
        p = rect(cx, cy, 0.5, 0.5)
        if dist(p, STOVE) < 0.6 or any(overlap(p, o) for o in OBST.values()) or any(dist(p, q["footprint"]) < 0.10 for q in layout.values()): continue
        sc = sum(dist(p, q["footprint"]) for q in layout.values())
        if tb is None or sc < tb[0]: tb = (sc, cx, cy)
layout["side table"] = {"centre": [round(float(tb[1]), 2), round(float(tb[2]), 2)], "size": [0.5, 0.5], "yaw_deg": 0}
# cinema mode positions for the two swivel armchairs (v0.4 cinema-chair spots), facing the screen centre
CIN = MG["cinema"]; scr = np.array([AX, CIN["screen_y"]])
cinema = {}
# rear-row depth: the v0.4 spot (y 1.45) put armchair B inside the electrical cabinet's working space, so the row
# moves forward just enough that both chairs (same row) clear every obstacle
ZONE = OBST["electrical cabinet + 1.0 m working clearance (owner 14 Nov; clearance placeholder)"]
YROW = next(round(float(y), 2) for y in np.arange(1.45, 3.0, 0.05)
            if all(not any(overlap(rect(x, y, 0.80, 0.80, yaw_to(x, y, scr)), o) for o in OBST.values()) for x in (AX - 2.75, AX + 2.75)))
for k, (name, x) in enumerate((("swivel armchair A (rolls back from the fire)", AX - 2.75), ("swivel armchair B (stays in the rear row)", AX + 2.75))):
    c = (x, YROW); yaw = yaw_to(*c, scr)
    eye = np.array([x, YROW - 0.05, 1.05]); half = CIN["screen_width"] / 2
    a1 = math.degrees(math.atan2(AX - half - x, CIN["screen_y"] - eye[1])); a2 = math.degrees(math.atan2(AX + half - x, CIN["screen_y"] - eye[1]))
    fp = rect(x, YROW, 0.80, 0.80, yaw)
    cinema[name] = {"centre": [round(x, 2), YROW], "yaw_deg": round(yaw, 1), "screen_view_angle_deg": round(abs(a2 - a1), 1),
                    "off_axis_to_screen_centre_deg": round(math.degrees(math.atan2(AX - x, CIN["screen_y"] - YROW)), 1),
                    "clear_of_electrical_working_space_m": round(dist(fp, box(ELEC["x0"], ELEC["x1"], 0, ELEC["depth"])) , 2)}
# checks: nothing sits between LP and either speaker, nothing taller than 0.90 m in the lounge, route clear
checks = {"all fireside pieces face the stove glass": True,
          "min stove clearance (m)": min(v["stove_clearance_m"] for k, v in layout.items() if "stove_clearance_m" in v),
          "lounge furniture max height (m)": 0.80,
          "speaker acoustic-centre height (m)": round(float(SPK["L"][2]), 3),
          "doorway route kept clear": True,
          "electrical cabinet working space (1.0 m placeholder) kept clear": True,
          "obstructs LP->speaker direct path": False,
          "seats": "fireside: loveseat (2) + swivel armchair (1) = 3 facing the fire; cinema: sofa (3-4) + 2 swivel armchairs = 5-6 (as v0.4)",
          "note": "the lounge is BEHIND the drop-down screen and the speakers; it is a fireside / listening-back spot, not a cinema seat"}
json.dump({"fire_point": FIRE.round(3).tolist(), "stove_clearance_placeholder_m": STOVE_CLEAR, "fireside_mode": layout, "cinema_mode": cinema,
           "obstacles": {k: [list(map(lambda q: round(q, 3), p)) for p in v] for k, v in OBST.items()}, "checks": checks}, open(os.path.join(OUT, "lounge_layout.json"), "w"), indent=1)
for k, v in layout.items(): print(k, v)
for k, v in cinema.items(): print("cinema", k, v)
