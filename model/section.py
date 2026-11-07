"""Single definition of the existing control-room section (v0.2, asymmetric).

Used by build_existing_shell.py, make_drawings.py and make_comparisons.py so the Blender
model, drawings and photo overlays can never disagree.
Values: fused photo+scan solve (model/solve_result.json) + hloL measured directly from the
native scan (model/scan_control_room_measurements.json; not observable in the photos).
"""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))

def geom(P):
    scan = json.load(open(os.path.join(HERE, "scan_control_room_measurements.json")))
    W, D, hc, wc, xf = P["W"], P["D"], P["hc"], P["wc"], P["xf"]
    g = dict(W=W, D=D, hc=hc, wc=wc, xf=xf,
             hloL=round(scan["low_ceiling_left"], 3), hloR=P["hloR"],
             xL=P["dsL"], xR=W - P["dsR"],                 # beam / post lines
             hbbL=P["hbbL"], hbbR=P["hbbR"], hbL=P["hbL"], hbR=P["hbR"],
             xc1=xf - wc / 2, xc2=xf + wc / 2)
    # ceiling polyline across the room (X, Z), left wall -> right wall
    g["ceil"] = [(0, g["hloL"]), (g["xL"], g["hloL"]), (g["xL"], g["hbL"]), (g["xc1"], hc),
                 (g["xc2"], hc), (g["xR"], g["hbR"]), (g["xR"], g["hloR"]), (W, g["hloR"])]
    g["section"] = [(0, 0), (W, 0)] + g["ceil"][::-1]   # closed end-wall outline
    return g
