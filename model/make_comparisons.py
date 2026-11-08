"""Camera-match comparison panels: PHOTO | BLENDER RENDER | PHOTO + MODEL EDGES + RESIDUALS.

    python3 model/make_comparisons.py

Model edges are projected with exactly the same camera model the solver used
(independent of Blender's camera conversion, so the Blender panel is a cross-check).
Panels that contain owner photographs are written to inputs/private/comparisons/
(gitignored). A public-safe edges-only panel is written to renders/qa/.
"""
import json, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from camera_solve import project  # same projection as the solve

SOL = json.load(open(os.path.join(HERE, "solve_result.json")))
P = {k: v["value"] for k, v in SOL["params"].items()}
PREVIEW = os.path.join(ROOT, "inputs", "private", "preview")
PRIV = os.path.join(ROOT, "inputs", "private", "comparisons"); os.makedirs(PRIV, exist_ok=True)
PUB = os.path.join(ROOT, "renders", "qa")

from section import geom
G = geom(P); W, D = G["W"], G["D"]

def edges():
    E = []
    sec = G["section"]
    for y in (0, D):
        for i in range(len(sec)):
            a, b = sec[i], sec[(i+1) % len(sec)]; E.append(((a[0], y, a[1]), (b[0], y, b[1]), "shell"))
    for x, z in [(0,0),(W,0)] + list(G["ceil"]) + [(G["xL"],G["hbbL"]),(G["xR"],G["hbbR"])]:
        E.append(((x, 0, z), (x, D, z), "shell"))
    for x, y, hbb in ((G["xL"], P["ypl"], G["hbbL"]), (G["xR"], P["ypr"], G["hbbR"])):
        E.append(((x, y, 0), (x, y, hbb), "post"))
    def rect(pl, a0, a1, z0, z1):
        pts = [(a0,z0),(a1,z0),(a1,z1),(a0,z1)]
        f = {"Y0": lambda a, z: (a, 0, z), "YD": lambda a, z: (a, D, z), "XW": lambda a, z: (W, a, z)}[pl]
        for i in range(4): E.append((f(*pts[i]), f(*pts[(i+1) % 4]), "opening"))
    rect("Y0", P["CR3.xe1"], P["CR3.xe2"], 0, P["CR3.he"])
    rect("Y0", P["CR3.xw1"], P["CR3.xw2"], P["CR3.hwb"], P["CR3.hwt"])
    rect("Y0", P["g_xi1"], P["g_xi2"], 0, P["g_hi"])
    rect("YD", P["CR1.xd1"], P["CR1.xd2"], 0, P["CR1.hd"])
    rect("Y0", P["CR3.gw1a"], P["CR3.gw1b"], P["CR3.gw1s"], P["CR3.gw1h"])      # v0.3 gable windows (G1-01)
    rect("Y0", P["CR3.gw2a"], P["CR3.gw2b"], P["CR3.gw2s"], P["CR3.gw2h"])
    for a, b_ in ((1.15, 4.35), (4.50, 7.95)): rect("XW", a, b_, P["CR1.wsill"], P["CR1.wh"])   # scan reveals
    xs, ys = P["g_xs"], min(P["g_ys"], D - 0.35)                                   # stove (G1-07)
    for (x0, y0), (x1, y1) in (((xs-0.28, ys-0.25), (xs+0.28, ys-0.25)), ((xs-0.28, ys-0.25), (xs-0.28, ys+0.25)), ((xs+0.28, ys-0.25), (xs+0.28, ys+0.25))):
        for z in (0, P["CR1.hs"]): E.append(((x0, y0, z), (x1, y1, z), "opening"))
    E.append(((xs, ys + 0.1, P["CR1.hs"]), (xs, ys + 0.1, P["CR1.hfl"]), "post"))
    return E

COLORS = {"shell": (0, 230, 255), "post": (255, 200, 0), "opening": (255, 60, 200)}

def draw_edges(img, cam, Elist, n=40):
    d = ImageDraw.Draw(img)
    for a, b, kind in Elist:
        pts = []
        for t in np.linspace(0, 1, n):
            Pt = np.array(a) * (1-t) + np.array(b) * t
            uv, z = project(cam, Pt)
            pts.append(tuple(uv) if z > 0.1 else None)
        for p, q in zip(pts, pts[1:]):
            if p and q and max(abs(p[0]), abs(q[0])) < 5000 and max(abs(p[1]), abs(q[1])) < 5000:
                d.line([p, q], fill=COLORS[kind], width=3)

def label(img, text):
    d = ImageDraw.Draw(img)
    try: font = ImageFont.truetype("DejaVuSans-Bold.ttf", 26)
    except Exception: font = ImageFont.load_default()
    d.rectangle([0, 0, img.width, 40], fill=(0, 0, 0)); d.text((12, 6), text, fill=(255, 255, 255), font=font)

def main():
    E = edges()
    for cid, title in (("CR1", "Control Room 1"), ("CR2", "Control Room 2"), ("CR3", "Control Room 3")):
        cam = [P[f"{cid}.{k}"] for k in ("tx", "ty", "tz", "yaw", "pitch", "roll")] + [P["lens13.f"]]
        rows = [r for r in SOL["points"] if r["photo"] == cid]
        rms = float(np.sqrt(np.mean([r["err_px"]**2 for r in rows])))
        # public-safe edges-only
        blank = Image.new("RGB", (1600, 1200), (24, 24, 28)); draw_edges(blank, cam, E)
        label(blank, f"{cid} solved camera - model edges only (no photo)  RMS {rms:.1f}px"); blank.save(os.path.join(PUB, f"edges_{cid}.png"))
        photo_p = os.path.join(PREVIEW, title + ".jpg")
        if not os.path.exists(photo_p):
            print("private photo not staged; skipped private panel for", cid); continue
        photo = Image.open(photo_p).convert("RGB")
        render = Image.open(os.path.join(PUB, f"clay_{cid}.png")).convert("RGB").resize((1600, 1200))
        ov = photo.copy(); draw_edges(ov, cam, E)
        d = ImageDraw.Draw(ov)
        for r in rows:  # residual: observed (white dot) -> predicted (red), x5 exaggeration line
            (ou, ovv), (pu, pv) = r["obs"], r["pred"]
            d.ellipse([ou-6, ovv-6, ou+6, ovv+6], outline=(255, 255, 255), width=3)
            d.line([(ou, ovv), (ou + 5*(pu-ou), ovv + 5*(pv-ovv))], fill=(255, 40, 40), width=3)
        a, b, c = photo.copy(), render, ov
        label(a, f"ORIGINAL PHOTO  {title}.HEIC  (private)")
        label(b, f"BLENDER v0.2 clay (pre-review shell) - camera {cid}")
        label(c, f"v0.3 MODEL EDGES ON PHOTO  RMS {rms:.1f}px  (red = residual x5)")
        panel = Image.new("RGB", (4800, 1200)); [panel.paste(im, (i*1600, 0)) for i, im in enumerate((a, b, c))]
        panel.save(os.path.join(PRIV, f"match_{cid}.jpg"), quality=85)
        print(cid, "RMS", round(rms, 2), "->", os.path.join(PRIV, f"match_{cid}.jpg"))

if __name__ == "__main__":
    main()
