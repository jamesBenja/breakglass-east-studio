"""Fetch the CC0 photo textures, HDRI and models used by the photo look (model/lookdev.py).

    python3 model/fetch_assets.py           -> model/assets/polyhaven/ (gitignored cache) + model/assets/polyhaven_manifest.json

All assets are from Poly Haven (polyhaven.com), licence CC0 1.0 (public domain); nothing here is a project
photograph. The manifest records asset id, files, URLs and md5 so a render can be reproduced exactly.
Generic, presentation-only materials: they do NOT document the barn's real finishes (see docs/v05/UNRESOLVED.md U9).
"""
import hashlib, json, os, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "assets", "polyhaven"); os.makedirs(CACHE, exist_ok=True)
UA = {"User-Agent": "studio-render-pipeline/1.0"}
API = "https://api.polyhaven.com/files/"

TEXTURES = {   # id: use
 "oak_wood_planks": "control-room oak floor (proposed finish)",
 "brown_leather": "leather grain for the black leather sofa / loveseat / armchairs (recoloured black)",
 "rough_linen": "window-seat cushions, floor cushions (recoloured oatmeal / charcoal)",
 "poly_wool_herringbone": "wool rug",
 "painted_plaster_wall": "plaster walls (very low contrast; existing lining unknown)",
 "brushed_concrete": "live-room / middle-zone slab",
 "corrugated_iron": "galvanised ribbed roof (type photo-observed)",
 "dark_wooden_planks": "stained vertical board siding (type photo-observed; recoloured to the photos)",
 "weathered_brown_planks": "weathered live-room gable siding",
 "leafy_grass": "lawn (indicative context)",
}
MAPS = ("Diffuse", "nor_gl", "Rough")
HDRIS = {"kloofendal_48d_partly_cloudy_puresky": "sky + daylight (indicative context)"}
MODELS = {"fir_tree_01": "distant conifers (context)", "tree_small_02": "distant hardwoods (context)", "throw_pillows_01": "throw pillows (recoloured)"}

def get(u): return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=120).read()
def save(url, rel):
    p = os.path.join(CACHE, rel); os.makedirs(os.path.dirname(p), exist_ok=True)
    if not os.path.exists(p): open(p, "wb").write(get(url))
    return {"file": rel, "url": url, "md5": hashlib.md5(open(p, "rb").read()).hexdigest()}

man = {"source": "Poly Haven (polyhaven.com)", "licence": "CC0 1.0", "textures": {}, "hdris": {}, "models": {}}
for k, use in TEXTURES.items():
    f = json.loads(get(API + k)); ent = {"use": use, "files": {}}
    for mp in MAPS:
        if mp in f: ent["files"][mp] = save(f[mp]["2k"]["jpg"]["url"], f"tex/{k}/{os.path.basename(f[mp]['2k']['jpg']['url'])}")
    man["textures"][k] = ent; print("tex", k, list(ent["files"]))
for k, use in HDRIS.items():
    f = json.loads(get(API + k)); u = f["hdri"]["4k"]["hdr"]["url"]
    man["hdris"][k] = {"use": use, "files": {"hdr": save(u, f"hdri/{os.path.basename(u)}")}}; print("hdri", k)
for k, use in MODELS.items():
    f = json.loads(get(API + k)); b = f["blend"]["1k"]["blend"]; ent = {"use": use, "files": {"blend": save(b["url"], f"models/{k}/{os.path.basename(b['url'])}")}}
    for rel, inc in b.get("include", {}).items(): ent["files"][rel] = save(inc["url"], f"models/{k}/{rel}")
    man["models"][k] = ent; print("model", k, len(ent["files"]), "files")
json.dump(man, open(os.path.join(HERE, "assets", "polyhaven_manifest.json"), "w"), indent=1)
print("cache", CACHE)
