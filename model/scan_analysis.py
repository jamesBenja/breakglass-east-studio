"""Analyse the native Polycam LiDAR mesh (private input, never committed).

    python3 -I model/scan_analysis.py
Input : inputs/originals/scan/polycam_2022-10-24.glb   (glTF Y-up, metres)
Output: inputs/private/scan/*.png  height maps / slices (private review)
        model/scan_frame.json      transform mesh -> building frame (public: numbers only)
"""
import json, os, numpy as np, trimesh
from PIL import Image, ImageDraw
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GLB = os.path.join(ROOT, "inputs/originals/scan/polycam_2022-10-24.glb")
OUT = os.path.join(ROOT, "inputs/private/scan"); os.makedirs(OUT, exist_ok=True)

def load_building_frame(rot_deg=None):
    m = trimesh.load(GLB).to_geometry()
    V = m.vertices.copy()
    # mesh: x, y(up), z  -> building: X across, Y along, Z up
    P = np.c_[V[:, 0], -V[:, 2], V[:, 1]]   # proper rotation (det +1): keeps face normals valid
    if rot_deg is None:
        n = m.face_normals; a = m.area_faces; v = np.abs(n[:, 1]) < 0.2
        ang = np.degrees(np.arctan2(n[v, 2], n[v, 0])) % 90
        h, e = np.histogram(ang, bins=360, range=(0, 90), weights=a[v])
        rot_deg = e[np.argmax(h)] + 0.125
        if rot_deg > 45: rot_deg -= 90
    t = np.radians(rot_deg); R = np.array([[np.cos(t), np.sin(t)], [-np.sin(t), np.cos(t)]])
    P[:, :2] = P[:, :2] @ R.T
    m2 = trimesh.Trimesh(P, m.faces, process=False)
    return m2, rot_deg

def heightmaps(m, cell=0.05):
    tri = m.triangles; c = tri.mean(1); n = m.face_normals
    lo, hi = m.bounds[0], m.bounds[1]
    nx, ny = int((hi[0]-lo[0])/cell)+1, int((hi[1]-lo[1])/cell)+1
    floor = np.full((ny, nx), np.nan); ceil = np.full((ny, nx), np.nan)
    # dense sample points on faces for coverage
    pts, fi = trimesh.sample.sample_surface(m, 1_500_000, seed=1)
    nz = n[fi, 2]; ix = ((pts[:, 0]-lo[0])/cell).astype(int); iy = ((pts[:, 1]-lo[1])/cell).astype(int)
    up = nz > 0.8; dn = nz < -0.8
    for mask, arr, fn in ((up, floor, np.fmin), (dn, ceil, None)):
        pass
    order = np.argsort(pts[up, 2])[::-1]
    floor[iy[up][order], ix[up][order]] = pts[up, 2][order]          # keeps lowest up-facing
    return floor, ceil, lo, (nx, ny), pts, fi, nz, ix, iy

if __name__ == "__main__":
    m, rot = load_building_frame()
    print("rotation applied (deg):", round(rot, 3)); print("bounds", m.bounds.round(3))
    json.dump({"source": "polycam_2022-10-24.glb sha256 fcec5a61c341", "mesh_axes": "x,y(up),z",
               "building_axes": "X=mesh x, Y=-mesh z, Z=mesh y, then rotate about Z by deg",
               "rot_deg": float(rot)}, open(os.path.join(ROOT, "model/scan_frame.json"), "w"), indent=1)
