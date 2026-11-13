"""Shared control-room geometry for the v0.5 acoustic work (single source: model/*.json).

Surfaces are the real asymmetric tray section measured from the native scan and solved
from the photos (model/section.py), extruded along Y; openings from the v0.3/v0.4 solve.
Listening/speaker positions from model/monitoring_geometry.json (layout: fireside, v0.4).
"""
import json, math, os, sys
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "model"))
from section import geom
P = {k: v["value"] for k, v in json.load(open(os.path.join(ROOT, "model/solve_result.json")))["params"].items()}
G = geom(P)
MG = json.load(open(os.path.join(ROOT, "model/monitoring_geometry.json")))
W, D, AX = G["W"], G["D"], G["xf"]
C_SOUND = 343.0
ST = MG["stereo"]
EAR = np.array(ST["listening_position"])
SPK = {"L": np.array(ST["L"]), "R": np.array(ST["R"])}
CONSOLE = MG["inputs"]["console_tape"]; CON = ST["console"]

def plane(name, p0, n, inside):
    n = np.array(n, float); n /= np.linalg.norm(n)
    return {"name": name, "p0": np.array(p0, float), "n": n, "inside": inside}

xL, xR, xc1, xc2 = G["xL"], G["xR"], G["xc1"], G["xc2"]
def slope_n(xa, za, xb, zb):     # downward-facing normal of a sloped ceiling plane (Y-extruded)
    t = np.array([xb - xa, 0, zb - za]); n = np.cross(t, [0, 1, 0]); return n if n[2] < 0 else -n
SURF = [
    plane("floor", (0, 0, 0), (0, 0, 1), lambda p: 0 <= p[0] <= W and 0 <= p[1] <= D),
    plane("flat ceiling (4.11 m)", (0, 0, G["hc"]), (0, 0, -1), lambda p: xc1 <= p[0] <= xc2 and 0 <= p[1] <= D),
    plane("left sloped ceiling", (xL, 0, G["hbL"]), slope_n(xL, G["hbL"], xc1, G["hc"]), lambda p: xL <= p[0] <= xc1 and 0 <= p[1] <= D),
    plane("right sloped ceiling", (xR, 0, G["hbR"]), slope_n(xc2, G["hc"], xR, G["hbR"]), lambda p: xc2 <= p[0] <= xR and 0 <= p[1] <= D),
    plane("left low ceiling", (0, 0, G["hloL"]), (0, 0, -1), lambda p: 0 <= p[0] <= xL and 0 <= p[1] <= D),
    plane("right low ceiling", (0, 0, G["hloR"]), (0, 0, -1), lambda p: xR <= p[0] <= W and 0 <= p[1] <= D),
    plane("left side wall (X=0)", (0, 0, 0), (1, 0, 0), lambda p: 0 <= p[1] <= D and 0 <= p[2] <= G["hloL"]),
    plane("right side wall (X=W)", (W, 0, 0), (-1, 0, 0), lambda p: 0 <= p[1] <= D and 0 <= p[2] <= G["hloR"]),
    plane("front wall / partition (Y=D)", (0, D, 0), (0, -1, 0), lambda p: 0 <= p[0] <= W and 0 <= p[2] <= 4.2),
    plane("rear wall / gable (Y=0)", (0, 0, 0), (0, 1, 0), lambda p: 0 <= p[0] <= W and 0 <= p[2] <= 4.2),
]
OPENINGS = [  # (surface, a0, a1, z0, z1, label) a = along-wall coordinate (X for end walls, Y for side walls)
    ("rear", min(P["CR3.xe1"], P["CR3.xe2"]), max(P["CR3.xe1"], P["CR3.xe2"]), 0, P["CR3.he"], "entry door"),
    ("rear", min(P["CR3.xw1"], P["CR3.xw2"]), max(P["CR3.xw1"], P["CR3.xw2"]), P["CR3.hwb"], P["CR3.hwt"], "clerestory"),
    ("rear", min(P["g_xi1"], P["g_xi2"]), max(P["g_xi1"], P["g_xi2"]), 0, P["g_hi"], "interior door"),
    ("rear", min(P["CR3.gw1a"], P["CR3.gw1b"]), max(P["CR3.gw1a"], P["CR3.gw1b"]), P["CR3.gw1s"], P["CR3.gw1h"], "gable window E"),
    ("rear", min(P["CR3.gw2a"], P["CR3.gw2b"]), max(P["CR3.gw2a"], P["CR3.gw2b"]), P["CR3.gw2s"], P["CR3.gw2h"], "gable window W"),
    ("front", P["CR1.xd1"], P["CR1.xd2"], 0, P["CR1.hd"], "partition doorway"),
    ("right", 1.15, 4.35, P["CR1.wsill"], P["CR1.wh"], "right window 1"),
    ("right", 4.50, 7.95, P["CR1.wsill"], P["CR1.wh"], "right window 2"),
    ("left", 1.95, 2.90, P["CR1.wsill"], P["CR1.wh"], "left window 1"),
    ("left", 4.45, 8.05, P["CR1.wsill"], P["CR1.wh"], "left window 2"),
]
STOVE = {"x": P["g_xs"], "y": min(P["g_ys"], D - 0.35), "w": 0.56, "d": 0.50, "h": P["CR1.hs"]}

def opening_at(surface_name, p):
    key = {"rear wall / gable (Y=0)": "rear", "front wall / partition (Y=D)": "front", "left side wall (X=0)": "left", "right side wall (X=W)": "right"}.get(surface_name)
    if not key: return None
    a = p[0] if key in ("rear", "front") else p[1]
    for s, a0, a1, z0, z1, lab in OPENINGS:
        if s == key and a0 <= a <= a1 and z0 <= p[2] <= z1: return lab
    return None

def seg_hits_box(a, b, box):   # slab test, box = (x0,x1,y0,y1,z0,z1)
    d = b - a; t0, t1 = 0.0, 1.0
    for i, (lo, hi) in enumerate(((box[0], box[1]), (box[2], box[3]), (box[4], box[5]))):
        if abs(d[i]) < 1e-12:
            if a[i] < lo or a[i] > hi: return False
        else:
            ta, tb = (lo - a[i]) / d[i], (hi - a[i]) / d[i]
            t0, t1 = max(t0, min(ta, tb)), min(t1, max(ta, tb))
            if t0 > t1: return False
    return True
CONSOLE_BOX = (CON["x0"], CON["x1"], CON["front_edge_y"], CON["back_edge_y"], 0.0, CONSOLE["h_top"])
