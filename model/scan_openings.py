"""Detect wall openings (windows/doors) in the control room from the native mesh.

Glass is invisible to LiDAR, so an opening appears as REVEAL surfaces lying beyond the
interior wall plane. Samples 0.06-1.2 m outside each wall plane are binned on the wall
(along-wall x height, 5 cm cells); connected regions >= 0.3 x 0.3 m are reported.
Output: model/scan_openings_control_room.json (numbers only). Room-local frame of
scan_measure_control_room.py: X from left wall, Y from gable wall, Z from control floor.
"""
import json, os, numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M = json.load(open(os.path.join(ROOT, "model/scan_control_room_measurements.json"))); F = M["frame"]
d = np.load(os.path.join(ROOT, "inputs/private/scan/samples.npz")); P = d["pts"].copy()
P[:, 2] -= F["floor_z_mesh"]
t = np.radians(F["ang_deg"]); c, s = np.cos(t), np.sin(t)
x, y = P[:, 0] - F["cx"], P[:, 1] - F["cy"]
X = c*x - s*y - F["xl"]; Y = s*x + c*y - F["yg"]; Z = P[:, 2]
W, D = M["width_wall_to_wall"], M["depth_gable_to_partition"]

def components(mask2d):
    lab = np.zeros(mask2d.shape, int); n = 0
    for i, j in zip(*np.nonzero(mask2d)):
        if lab[i, j]: continue
        n += 1; stack = [(i, j)]; lab[i, j] = n
        while stack:
            a, b = stack.pop()
            for da, db in ((1,0),(-1,0),(0,1),(0,-1)):
                u, v = a+da, b+db
                if 0 <= u < mask2d.shape[0] and 0 <= v < mask2d.shape[1] and mask2d[u, v] and not lab[u, v]:
                    lab[u, v] = n; stack.append((u, v))
    return lab, n

def find(name, beyond, along, lo, hi, cell=0.05, minpts=4):
    m = beyond & (Z > 0.05) & (Z < 4.2) & (along > lo) & (along < hi)
    nb_a = int((hi - lo) / cell) + 1; nb_z = int(4.2 / cell) + 1
    H = np.zeros((nb_a, nb_z)); np.add.at(H, (((along[m]-lo)/cell).astype(int), (Z[m]/cell).astype(int)), 1)
    lab, n = components(H >= minpts); out = []
    for k in range(1, n + 1):
        ii, jj = np.nonzero(lab == k)
        a0, a1, z0, z1 = lo + ii.min()*cell, lo + (ii.max()+1)*cell, jj.min()*cell, (jj.max()+1)*cell
        if (a1 - a0) >= 0.3 and (z1 - z0) >= 0.3:
            out.append({"wall": name, "along_from": round(a0, 2), "along_to": round(a1, 2), "z_from": round(z0, 2), "z_to": round(z1, 2),
                        "cells": int(len(ii))})
    return out

res = []
res += find("X=0 (left)",  (X < -0.06) & (X > -1.2), Y, 0.1, D - 0.1)
res += find("X=W (right)", (X > W + 0.06) & (X < W + 1.2), Y, 0.1, D - 0.1)
res += find("Y=0 (gable)", (Y < -0.06) & (Y > -1.2), X, 0.1, W - 0.1)
res += find("Y=D (partition)", (Y > D + 0.06) & (Y < D + 0.5), X, 0.1, W - 0.1)
json.dump({"method": __doc__.strip().splitlines()[0], "openings": res}, open(os.path.join(ROOT, "model/scan_openings_control_room.json"), "w"), indent=1)
for r in res: print(r)
