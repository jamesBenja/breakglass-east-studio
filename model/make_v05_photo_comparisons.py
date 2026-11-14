"""Standard vs photo-look pairs (same camera, same geometry; materials + lighting only) -> renders/compare_v05_photo/"""
import os
from PIL import Image, ImageDraw
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); R = os.path.join(ROOT, "renders", "design")
OUT = os.path.join(ROOT, "renders", "compare_v05_photo"); os.makedirs(OUT, exist_ok=True)
PAIRS = [("cr_front", "_v05", "_v05_photo"), ("cr_overview_rear", "_v05", "_v05_photo"), ("cr_fireside", "_v05", "_v05_photo"),
         ("cr_console", "_v05", "_v05_photo"), ("live_band", "_v05", "_v05_photo"), ("live_piano", "_v05", "_v05_photo"),
         ("live_farm", "_v05_farm", "_v05_farm_photo")]
for v, a, b in PAIRS:
    A, B = os.path.join(R, f"{v}{a}.png"), os.path.join(R, f"{v}{b}.png")
    if not (os.path.exists(A) and os.path.exists(B)): print("skip", v); continue
    ia = Image.open(A).convert("RGB").resize((960, 540)); ib = Image.open(B).convert("RGB").resize((960, 540))
    s = Image.new("RGB", (1920, 580), "white"); s.paste(ia, (0, 40)); s.paste(ib, (960, 40)); d = ImageDraw.Draw(s)
    d.text((10, 12), f"{v}  |  v0.5 standard render", fill="black")
    d.text((970, 12), f"{v}  |  v0.5 photo look pass (same geometry, materials + lighting only)", fill="black")
    s.save(os.path.join(OUT, f"{v}_std_vs_photo.png")); print("ok", v)
