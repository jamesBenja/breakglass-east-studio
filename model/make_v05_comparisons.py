"""Matched-camera v0.4 vs v0.5 comparison panels (same camera, lens, samples, resolution; only the design differs).

    python3 model/make_v05_comparisons.py -> renders/compare_v04_v05/<view>.jpg + _contact_sheet.jpg
"""
import os
from PIL import Image, ImageDraw, ImageFont
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R = os.path.join(ROOT, "renders", "design"); OUT = os.path.join(ROOT, "renders", "compare_v04_v05"); os.makedirs(OUT, exist_ok=True)
VIEWS = {"cr_front": "Control room toward the front wall", "cr_fireside": "Fireside lounge (v0.4 chairs faced away; v0.5 faces the stove)",
         "cr_cinema": "Cinema mode (screen down)", "cr_rear": "Toward the gable (rear wall)", "cr_console": "Over the console",
         "live_piano": "Live room from the garage end", "live_farm": "Live room toward the garage door", "axo_cutaway": "Axonometric cut-away"}
def font(sz):
    for f in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"):
        if os.path.exists(f): return ImageFont.truetype(f, sz)
    return ImageFont.load_default()
made = []
for v, label in VIEWS.items():
    a, b = os.path.join(R, f"{v}_v04.png"), os.path.join(R, f"{v}_v05.png")
    if not (os.path.exists(a) and os.path.exists(b)): print("skip", v); continue
    A, B = Image.open(a).convert("RGB"), Image.open(b).convert("RGB")
    w, h = A.size; bar = 56
    im = Image.new("RGB", (2 * w + 12, h + bar), (251, 250, 247)); im.paste(A, (0, bar)); im.paste(B, (w + 12, bar))
    d = ImageDraw.Draw(im); f = font(26)
    d.text((16, 14), f"v0.4 APPROVED — {label}", fill=(60, 60, 60), font=f); d.text((w + 28, 14), "v0.5 PROPOSED — same camera", fill=(47, 111, 79), font=f)
    p = os.path.join(OUT, f"{v}.jpg"); im.save(p, quality=88); made.append(p)
if made:
    thumbs = [Image.open(p) for p in made]; tw = 1400; th = int(thumbs[0].height * tw / thumbs[0].width)
    sheet = Image.new("RGB", (tw, th * len(thumbs)), (255, 255, 255))
    for i, t in enumerate(thumbs): sheet.paste(t.resize((tw, th)), (0, i * th))
    sheet.save(os.path.join(OUT, "_contact_sheet.jpg"), quality=85)
print("made", [os.path.basename(p) for p in made])
