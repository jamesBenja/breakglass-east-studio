"""v0.5 drawings (SVG) — acoustic integration & salvage. Same data as the v0.5 Blender model.

    python3 model/make_v05_drawings.py  -> drawings/v05/PR-50x_*.svg, PR-51x_*.svg + acoustics/out/reflection_coverage.json
Sources: model/solve_result.json, scan_building_measurements.json, monitoring_geometry.json (shell/equipment, v0.4 approved),
         acoustics/out/placements.json (Clark assets + NEW items), first_reflections.json, lounge_layout.json, modes_sbir_rt.json.
PROPOSED DESIGN on a provisional existing shell. NOT FOR CONSTRUCTION.
"""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from section import geom
P = {k: v["value"] for k, v in json.load(open(os.path.join(HERE, "solve_result.json")))["params"].items()}
G = geom(P); B = json.load(open(os.path.join(HERE, "scan_building_measurements.json")))
MG = json.load(open(os.path.join(HERE, "monitoring_geometry.json")))
AO = os.path.join(ROOT, "acoustics", "out")
PLC = json.load(open(os.path.join(AO, "placements.json"))); PL = PLC["placements"]; NEW = PLC["new_items"]
REF = json.load(open(os.path.join(AO, "first_reflections.json")))
LNG = json.load(open(os.path.join(AO, "lounge_layout.json")))
AN = json.load(open(os.path.join(AO, "modes_sbir_rt.json")))
W, D, AX = G["W"], G["D"], G["xf"]
Y_OFF = 15.185; Y_PART1 = D + 0.15; Y_MID1 = 1.0 + Y_OFF; Y_LOFT_END = 7.7 + Y_OFF; Y_LG = B["live_gable_y"] + Y_OFF
LL, LR = AX - 6.15, AX + 5.75; F_LIVE = B["live_floor"]; GD = 3.70
st = MG["stereo"]; LP = st["listening_position"]; CIN = MG["cinema"]; CON = st["console"]
XS, YS = P["g_xs"], min(P["g_ys"], D - 0.35)
OUT = os.path.join(ROOT, "drawings", "v05"); os.makedirs(OUT, exist_ok=True)
C = {"ex": "#555", "eq": "#1f4e79", "asset": "#2f6f4f", "prov": "#c2187a", "new": "#b5651d", "lounge": "#8a5a2b", "imm": "#7a2e8e",
     "zone": "#c9a400", "ray_ok": "#2f6f4f", "ray_open": "#d0342c", "ray_shadow": "#999", "txt": "#222"}
ROOMNAMES = {"Control room": "CR", "Live room": "LV"}

class Sheet:
    def __init__(s, sc, ox, oy, x0, ymax, flipy=True):
        s.sc, s.ox, s.oy, s.x0, s.ymax, s.b = sc, ox, oy, x0, ymax, []
    def X(s, x): return s.ox + (x - s.x0) * s.sc
    def Y(s, y): return s.oy + (s.ymax - y) * s.sc
    def poly(s, pts, stroke, fill="none", op=0.35, sw=1.2, dash=None):
        da = f' stroke-dasharray="{dash}"' if dash else ""
        s.b.append(f'<polygon points="{" ".join(f"{s.X(x):.1f},{s.Y(y):.1f}" for x, y in pts)}" fill="{fill}" fill-opacity="{op}" stroke="{stroke}" stroke-width="{sw}"{da}/>')
    def rect(s, x0, y0, x1, y1, stroke, fill="none", op=0.35, sw=1.2, dash=None):
        s.poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], stroke, fill, op, sw, dash)
    def line(s, x0, y0, x1, y1, stroke="#333", sw=1, dash=None, op=1):
        da = f' stroke-dasharray="{dash}"' if dash else ""
        s.b.append(f'<line x1="{s.X(x0):.1f}" y1="{s.Y(y0):.1f}" x2="{s.X(x1):.1f}" y2="{s.Y(y1):.1f}" stroke="{stroke}" stroke-width="{sw}" stroke-opacity="{op}"{da}/>')
    def text(s, x, y, t, col=C["txt"], size=10, anchor="middle", weight="normal", rot=0):
        tr = f' transform="rotate({rot} {s.X(x):.1f} {s.Y(y):.1f})"' if rot else ""
        s.b.append(f'<text x="{s.X(x):.1f}" y="{s.Y(y):.1f}" font-size="{size}" text-anchor="{anchor}" fill="{col}" font-weight="{weight}"{tr}>{t}</text>')
    def circle(s, x, y, r, fill, stroke="none"):
        s.b.append(f'<circle cx="{s.X(x):.1f}" cy="{s.Y(y):.1f}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>')
    def raw(s, t): s.b.append(t)

def save(name, w, h, body, title, sub, notes=()):
    w = max(int(w), 1400); h = int(h)
    nl = "".join(f'<text x="20" y="{h - 92 - 15 * i}" font-size="10" fill="#444">{n}</text>' for i, n in enumerate(reversed(notes)))
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" font-family="Helvetica,Arial,sans-serif">
<rect width="{w}" height="{h}" fill="#fbfaf7"/>{body}{nl}
<g font-size="11" fill="#333"><text x="20" y="{h-62}" font-size="15" font-weight="bold">{title}</text>
<text x="20" y="{h-44}">{sub}</text>
<text x="20" y="{h-28}">v0.5 ACOUSTIC INTEGRATION on the approved v0.4 layout and the provisional existing shell (scan + photos, about ±0.1–0.2 m). NOT FOR CONSTRUCTION. Acoustician review and on-site measurement required.</text>
<text x="20" y="{h-10}"><tspan fill="{C['ex']}">&#9632; existing</tspan>  <tspan fill="{C['eq']}">&#9632; actual equipment</tspan>  <tspan fill="{C['asset']}">&#9632; Clark asset (owner-measured body)</tspan>  <tspan fill="{C['prov']}">&#9632; Clark asset, depth PROVISIONAL</tspan>  <tspan fill="{C['new']}">&#9632; NEW purpose-built</tspan>  <tspan fill="{C['lounge']}">&#9632; lounge (owner-authorised correction)</tspan>  <tspan fill="{C['imm']}">&#9679; immersive (later)</tspan></text></g></svg>'''
    open(os.path.join(OUT, name + ".svg"), "w").write(svg); return name

def acol(p): return C["prov"] if p["depth_provisional"] else C["asset"]
def fp_sorted(p):
    pts = p["footprint_xy"]; cx = sum(x for x, _ in pts) / 4; cy = sum(y for _, y in pts) / 4
    return sorted(pts, key=lambda q: math.atan2(q[1] - cy, q[0] - cx))
def is_overhead(p): return p["aabb"][0][2] > 2.0 if p["room"] == "Control room" else p["aabb"][0][2] > 1.9 + (F_LIVE if p["room"] == "Live room" else 0)

# ------------------------------------------------------------------ reflection coverage (QA): which treatment intercepts each first reflection
def _boxes():
    for p in PL:
        if p["room"] == "Control room": yield p["asset"], p["aabb"][0], p["aabb"][1]
    for it in NEW:
        for g in it["geom"]:
            if "centre" in g:
                yield it["id"], [c - q / 2 for c, q in zip(g["centre"], g["size"])], [c + q / 2 for c, q in zip(g["centre"], g["size"])]
def _seg_hits(a, b, lo, hi, pad):
    t0, t1 = 0.0, 1.0
    for i in range(3):
        d = b[i] - a[i]; l_, h_ = lo[i] - pad, hi[i] + pad
        if abs(d) < 1e-12:
            if a[i] < l_ or a[i] > h_: return False
        else:
            ta, tb = (l_ - a[i]) / d, (h_ - a[i]) / d; t0, t1 = max(t0, min(ta, tb)), min(t1, max(ta, tb))
            if t0 > t1: return False
    return True
def covering(r, pad=0.05):
    """treatment that the reflected path actually meets: either leg (speaker->point, point->LP) crosses a treatment volume
    within 0.6 m of the reflection point (so a panel near the LP does not count for an unrelated path), or the point lies on it."""
    sp, pt = st[r["speaker"]], r["point"]; hits = []
    for name, lo, hi in _boxes():
        near_pt = all(lo[i] - 0.6 <= pt[i] <= hi[i] + 0.6 for i in range(3))
        if near_pt and (_seg_hits(sp, pt, lo, hi, pad) or _seg_hits(pt, LP, lo, hi, pad)): hits.append(name)
    return sorted(set(hits))
COV = []
for r in REF["reflections"]:
    h = covering(r)
    if h: status = "treated"
    elif r.get("console_shadowed"): status = "console-shadowed"
    elif r["off_axis_deg"] > 120 and r["surface"].startswith("front"): status = "rear radiation (cardioid); wall between stove clearance and doorway left bare"
    elif r["delay_ms"] > 15 and r["level_dB_re_direct"] <= -10: status = "late (>15 ms) and low (<= -10 dB); lands on glass/mullion -> NEW-04 shutters closed for critical work"
    else: status = "untreated"
    COV.append({**r, "treated_by": h, "status": status})
assert not [r for r in COV if r["status"] == "untreated"], "an early first reflection is untreated"
json.dump(COV, open(os.path.join(AO, "reflection_coverage.json"), "w"), indent=1)

# ================================================================== PR-501 control-room treatment plan
def cr_base(s, title_ceiling=False):
    s.rect(0, 0, W, D, C["ex"], "#fff", 1, 4)
    for x in (G["xL"], G["xR"]): s.line(x, 0, x, D, C["ex"], 1, "8 5")
    for x in (G["xc1"], G["xc2"]): s.line(x, 0, x, D, C["ex"], 1, "2 4")
    for x, y in ((G["xL"], P["ypl"]), (G["xR"], P["ypr"])): s.rect(x - 0.07, y - 0.07, x + 0.07, y + 0.07, C["ex"], C["ex"], 1)
    s.line(AX, -0.3, AX, D + 0.3, "#999", 0.8, "14 4 2 4")
    # openings (plan ticks)
    for a, b_ in ((min(P["CR3.xe1"], P["CR3.xe2"]), max(P["CR3.xe1"], P["CR3.xe2"])), (min(P["g_xi1"], P["g_xi2"]), max(P["g_xi1"], P["g_xi2"]))):
        s.rect(a, -0.06, b_, 0.06, "#fff", "#fff", 1, 0); s.line(a, 0, a, -0.25, C["ex"]); s.line(b_, 0, b_, -0.25, C["ex"])
    s.rect(P["CR1.xd1"], D - 0.06, P["CR1.xd2"], D + 0.06, "#fff", "#fff", 1, 0)
    for a, b_ in ((1.15, 4.35), (4.50, 7.95)): s.rect(W - 0.05, a, W + 0.05, b_, "#7aa7c7", "#cfe3f0", 1, 1)
    for a, b_ in ((1.95, 2.90), (4.45, 8.05)): s.rect(-0.05, a, 0.05, b_, "#7aa7c7", "#cfe3f0", 1, 1)
    for a, b_ in ((min(P["CR3.gw2a"], P["CR3.gw2b"]), max(P["CR3.gw2a"], P["CR3.gw2b"])), (min(P["CR3.gw1a"], P["CR3.gw1b"]), max(P["CR3.gw1a"], P["CR3.gw1b"]))):
        s.rect(a, -0.05, b_, 0.05, "#7aa7c7", "#cfe3f0", 1, 1)
    s.rect(XS - 0.28, YS - 0.25, XS + 0.28, YS + 0.25, "#111", "#222", 1)
    s.rect(XS - 0.65, YS - 0.85, XS + 0.65, D, "#777", "#bbb", 0.25, 1, "3 2")
def equipment(s):
    s.rect(CON["x0"], CON["front_edge_y"], CON["x1"], CON["back_edge_y"], C["eq"], C["eq"], 0.45, 2)
    for k in ("L", "R"):
        x, y, _ = st[k]; ang = math.atan2(LP[0] - x, -(LP[1] - y))
        pts = [(-0.25, 0), (0.25, 0), (0.25, 0.424), (-0.25, 0.424)]
        s.poly([(x + px * math.cos(ang) - py * math.sin(ang), y + px * math.sin(ang) + py * math.cos(ang)) for px, py in pts], C["eq"], C["eq"], 1, 1)
        s.line(x, y, LP[0], LP[1], C["eq"], 1, "5 3")
    s.circle(LP[0], LP[1], 5, "#000")
def tag(s, p, x, y, size=8, col=None):
    s.text(x, y, p["asset"], col or acol(p), size, weight="bold")

s = Sheet(68, 90, 80, -0.6, D + 0.5)
cr_base(s); equipment(s)
for it in NEW:
    if it["room"] != "Control room": continue
    for g in it["geom"]:
        if "tri" in g:
            x0, y0, L = g["tri"]; sx = 1 if x0 == 0 else -1
            s.poly([(x0, y0), (x0 + sx * L, y0), (x0, y0 - L)], C["new"], C["new"], 0.45, 1.5)
        else:
            (cx, cy, _), (sx_, sy_, _) = g["centre"], g["size"]
            s.rect(cx - sx_ / 2, cy - sy_ / 2, cx + sx_ / 2, cy + sy_ / 2, C["new"], C["new"], 0.30, 1.5)
s.text(0.375, 4.5, "NEW-01 under-sill LF bench trap 0.75 deep (window bench above)", C["new"], 9, rot=-90)
s.text(W - 0.375, 4.5, "NEW-01 under-sill LF bench trap 0.75 deep", C["new"], 9, rot=-90)
s.text(0.55, D - 0.95, "NEW-02", C["new"], 8, "start"); s.text(W - 0.55, D - 0.95, "NEW-02", C["new"], 8, "end")
s.text(AX, 0.32, "NEW-03 wool curtain (door)", C["new"], 8)
for p in PL:
    if p["room"] != "Control room" or is_overhead(p): continue
    s.poly(fp_sorted(p), acol(p), acol(p), 0.55, 1.2)
cnt = {}
for p in PL:
    if p["room"] != "Control room": continue
    lo, hi = p["aabb"]; cx, cy = (lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2
    if is_overhead(p): s.poly(fp_sorted(p), acol(p), "none", 0, 1.2, "6 3")
    off = {"ABS-003": (0, -0.30), "PAN-001": (0, -0.30), "DIF-001": (0, 0.42), "BTR-001": (0.35, 0.55), "BTR-002": (-0.35, 0.55), "GOB-005": (0.55, 0)}.get(p["asset"], (0, 0))
    key = (p["asset"], round(cy, 0) if p["asset"] in ("ABS-003", "PAN-001") else round(cx, 1))
    if key in cnt: continue
    cnt[key] = 1
    n = sum(1 for q in PL if q["asset"] == p["asset"] and q["room"] == "Control room" and q["zone"] == p["zone"])
    lbl = p["asset"] + (f" ×{n}" if p["asset"] in ("ABS-003", "PAN-001") else "")
    if p["asset"] in ("ABS-003", "PAN-001") and round(cy, 0) in cnt.get("_done", set()): continue
    tag(s, {**p, "asset": lbl}, cx + off[0], cy + off[1])
s.text(AX, 2.30, "ceiling above: GOB-004 + GOB-003 cloud (flat), GOB-003 on each slope — see PR-502", C["asset"], 9)
# lounge (fireside mode)
for name, v in LNG["fireside_mode"].items():
    if "footprint" in v: s.poly(v["footprint"], C["lounge"], C["lounge"], 0.45, 1.5)
    elif name == "side table": s.circle(*v["centre"], 0.25 * s.sc, C["lounge"])
FIRE = LNG["fire_point"]
for name, v in LNG["fireside_mode"].items():
    if "footprint" in v: s.line(v["centre"][0], v["centre"][1], FIRE[0], FIRE[1], C["lounge"], 1.2, "2 3")
s.text(2.0, 4.75, "loveseat → faces fire", C["lounge"], 9, weight="bold"); s.text(3.45, 6.62, "armchair → fire", C["lounge"], 8, "start")
B_ = LNG["cinema_mode"]["swivel armchair B (stays in the rear row)"]
s.rect(B_["centre"][0] - 0.4, 1.05, B_["centre"][0] + 0.4, 1.85, C["lounge"], C["lounge"], 0.45, 1.5); s.text(B_["centre"][0], 0.85, "swivel armchair B", C["lounge"], 8)
s.rect(AX - 1.4, 0.30, AX + 1.4, 1.25, "#7d6b5a", "#7d6b5a", 0.3, 1.2); s.text(AX, 1.45, "cinema sofa", "#7d6b5a", 9)
s.rect(0.85, 1.70, 1.55, 3.90, "#7d6b5a", "#7d6b5a", 0.25, 1); s.text(1.2, 2.8, "producer desk", "#7d6b5a", 8, rot=-90)
for nm in ("L", "R"): x = AX + (-2.15 if nm == "L" else 2.15); s.rect(x - 0.3, st["L"][1] + 0.15, x + 0.3, st["L"][1] + 0.75, "#444", "#444", 0.6, 1)
s.text(XS, YS + 0.42, "stove (kept)", "#111", 9); s.text(XS, YS - 0.95, "hearth pad", "#777", 8)
s.line(AX - CIN["screen_width"] / 2, CIN["screen_y"], AX + CIN["screen_width"] / 2, CIN["screen_y"], "#777", 3, "2 2")
s.text(AX, D + 0.25, "FRONT: partition (doorway → live room)", C["ex"], 10); s.text(AX, -0.45, "REAR: gable (entry door, clerestory, 2 windows)", C["ex"], 10)
save("PR-501_control_room_treatment_plan", s.X(W + 0.8) + 260, s.Y(-0.9) + 170, "\n".join(s.b),
     "PR-501  CONTROL ROOM — v0.5 TREATMENT PLAN (Clark assets + new LF traps) with the corrected fireside lounge",
     "Wall/floor items solid; ceiling items dashed (PR-502). Asset IDs = owner inventory. Lounge seats now face the stove glass (dotted sightlines). Dims in metres.",
     ["Stove clearance shown = 0.90 m PLACEHOLDER for the listed clearances (stove label / WETT). Hearth pad size to the same.",
      "PAN-001 ×3 and ABS-003 ×2 are re-hung on NEW-07 200 mm stand-off frames filled with mineral wool (front wall), stopping > 0.9 m from the stove.",
      "BTR-001 ×2 / BTR-002 ×2: two tapered traps per rear corner (gable + side wall). DIF-001 ×2 flank the entry door above the sofa back (bottom 0.92 m)."])

# ================================================================== PR-502 reflected ceiling plan
s = Sheet(68, 90, 80, -0.6, D + 0.5)
s.rect(0, 0, W, D, C["ex"], "#fff", 1, 4)
for x, z in ((G["xL"], G["hbL"]), (G["xR"], G["hbR"])): s.line(x, 0, x, D, C["ex"], 2); s.text(x, D + 0.12, f"beam {z:.2f}", C["ex"], 8)
for x in (G["xc1"], G["xc2"]): s.line(x, 0, x, D, C["ex"], 1, "2 4")
s.text(G["xL"] / 2, D - 0.3, f"low ceiling {G['hloL']:.2f}", C["ex"], 9); s.text((G["xR"] + W) / 2, D - 0.3, f"low ceiling {G['hloR']:.2f}", C["ex"], 9)
s.text((G["xL"] + G["xc1"]) / 2, D - 0.3, "slope", C["ex"], 9); s.text((G["xc2"] + G["xR"]) / 2, D - 0.3, "slope", C["ex"], 9)
s.text(AX, D - 0.3, f"flat ceiling {G['hc']:.2f}", C["ex"], 9)
for p in PL:
    if p["room"] == "Control room" and is_overhead(p):
        s.poly(fp_sorted(p), acol(p), acol(p), 0.5, 1.5)
        lo, hi = p["aabb"]; s.text((lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, p["asset"], "#fff", 9, weight="bold")
        s.text((lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2 - 0.22, f"{lo[2]:.2f}–{hi[2]:.2f}", "#fff", 8)
for r in COV:
    if r["surface"] in ("flat ceiling (4.11 m)", "left sloped ceiling", "right sloped ceiling"):
        col_ = C["ray_ok"] if r["treated_by"] else C["ray_open"]
        s.circle(r["point"][0], r["point"][1], 5, col_, "#fff")
        s.text(r["point"][0] + 0.12, r["point"][1] - 0.12, f'{r["speaker"]} {r["delay_ms"]:.1f} ms', col_, 8, "start")
s.rect(AX - 0.25, 0.70, AX + 0.25, 1.20, "#555", "none", 0, 1.2); s.text(AX, 0.55, "projector hush box", "#555", 8)
s.rect(AX - CIN["screen_width"] / 2 - 0.1, CIN["screen_y"] - 0.08, AX + CIN["screen_width"] / 2 + 0.1, CIN["screen_y"] + 0.10, "#555", "#555", 0.3, 1); s.text(AX, CIN["screen_y"] + 0.25, "screen cassette", "#555", 8)
for k in ("Ltf", "Rtf", "Ltr", "Rtr"):
    x, y, _ = MG["immersive_7_1_4"][k]; s.circle(x, y, 6, "#fff", C["imm"]); s.text(x + 0.12, y + 0.12, k, C["imm"], 8, "start")
for x in (G["xL"] + 0.12, G["xR"] - 0.12): s.line(x, 0.15, x, D - 0.15, "#e0a020", 3)
s.text(G["xL"] + 0.2, 0.3, "LED cove", "#c08000", 8, "start")
save("PR-502_control_room_RCP", s.X(W + 0.8) + 260, s.Y(-0.9) + 140, "\n".join(s.b),
     "PR-502  CONTROL ROOM — REFLECTED CEILING PLAN v0.5 (looking up; plan orientation as PR-501)",
     "Cloud = GOB-004 + GOB-003 hung 200 mm below the flat ceiling; GOB-003 on each slope on 50 mm stand-offs. Dots = first-reflection points (green treated, red open).",
     ["Clouds sit clear of the 7.1.4 overhead positions, projector, screen cassette and LED coves. Hanging hardware into the ceiling framing needs a structural check (load ~25–35 kg per panel, to verify).",
      "HVAC linear slots (v0.4, indicative) at the slope / flat junctions remain; confirm the roof-void route before fixing any cloud (ledger X4)."])

# ================================================================== PR-503 interior elevations
def elevation(s, wall, ox_m, oz_m, sc):
    """wall: 'front' (Y=D, seen from inside looking +Y), 'rear' (Y=0 looking -Y), 'left' (X=0 looking -X), 'right' (X=W looking +X)."""
    def U(x, y):   # along-wall coordinate as seen from inside
        return {"front": x, "rear": W - x, "left": D - y, "right": y}[wall]
    L_ = W if wall in ("front", "rear") else D
    def px(u): return s.ox + (ox_m + u) * sc
    def pz(z): return s.oy + (oz_m - z) * sc
    def prect(u0, z0, u1, z1, stroke, fill, op, sw=1, dash=None):
        da = f' stroke-dasharray="{dash}"' if dash else ""
        s.raw(f'<rect x="{px(min(u0,u1)):.1f}" y="{pz(max(z0,z1)):.1f}" width="{abs(u1-u0)*sc:.1f}" height="{abs(z1-z0)*sc:.1f}" fill="{fill}" fill-opacity="{op}" stroke="{stroke}" stroke-width="{sw}"{da}/>')
    # wall outline (ceiling profile for end walls, low ceiling for side walls)
    if wall in ("front", "rear"):
        prof = [(U(x, 0), z) for x, z in G["section"]]
        s.raw(f'<polygon points="{" ".join(f"{px(u):.1f},{pz(z):.1f}" for u, z in prof)}" fill="#fff" stroke="{C["ex"]}" stroke-width="3"/>')
    else:
        h = G["hloL"] if wall == "left" else G["hloR"]; prect(0, 0, L_, h, C["ex"], "#fff", 1, 3)
    ops = {"front": [(P["CR1.xd1"], P["CR1.xd2"], 0, P["CR1.hd"])],
           "rear": [(min(P["CR3.xe1"], P["CR3.xe2"]), max(P["CR3.xe1"], P["CR3.xe2"]), 0, P["CR3.he"]), (min(P["CR3.xw1"], P["CR3.xw2"]), max(P["CR3.xw1"], P["CR3.xw2"]), P["CR3.hwb"], P["CR3.hwt"]),
                    (min(P["g_xi1"], P["g_xi2"]), max(P["g_xi1"], P["g_xi2"]), 0, P["g_hi"]), (min(P["CR3.gw1a"], P["CR3.gw1b"]), max(P["CR3.gw1a"], P["CR3.gw1b"]), P["CR3.gw1s"], P["CR3.gw1h"]),
                    (min(P["CR3.gw2a"], P["CR3.gw2b"]), max(P["CR3.gw2a"], P["CR3.gw2b"]), P["CR3.gw2s"], P["CR3.gw2h"])],
           "left": [(1.95, 2.90, P["CR1.wsill"], P["CR1.wh"]), (4.45, 8.05, P["CR1.wsill"], P["CR1.wh"])],
           "right": [(1.15, 4.35, P["CR1.wsill"], P["CR1.wh"]), (4.50, 7.95, P["CR1.wsill"], P["CR1.wh"])]}[wall]
    for a, b_, z0, z1 in ops:
        u0, u1 = (U(a, 0), U(b_, 0)) if wall in ("front", "rear") else (U(0, a), U(0, b_))
        prect(u0, z0, u1, z1, "#7aa7c7", "#cfe3f0", 1, 1)
    def near(lo, hi):
        tol = 0.45
        return {"front": hi[1] > D - tol, "rear": lo[1] < tol, "left": lo[0] < tol, "right": hi[0] > W - tol}[wall]
    for p in PL:
        if p["room"] != "Control room": continue
        lo, hi = p["aabb"]
        if not near(lo, hi) or lo[2] > 2.2: continue
        if wall in ("front", "rear"): u0, u1 = U(lo[0], 0), U(hi[0], 0)
        else: u0, u1 = U(0, lo[1]), U(0, hi[1])
        prect(u0, lo[2], u1, hi[2], acol(p), acol(p), 0.5, 1.2)
        s.raw(f'<text x="{px((u0+u1)/2):.1f}" y="{pz((lo[2]+hi[2])/2)+3:.1f}" font-size="8" text-anchor="middle" fill="#fff" font-weight="bold">{p["asset"]}</text>')
    for it in NEW:
        if it["room"] != "Control room": continue
        for g in it["geom"]:
            if "centre" in g:
                lo = [c - q / 2 for c, q in zip(g["centre"], g["size"])]; hi = [c + q / 2 for c, q in zip(g["centre"], g["size"])]
            else:
                x0, y0, L = g["tri"]; lo = [min(x0, x0 + (L if x0 == 0 else -L)), y0 - L, 0]; hi = [max(x0, x0 + (L if x0 == 0 else -L)), y0, g["h"]]
            if not near(lo, hi): continue
            if wall in ("front", "rear"): u0, u1 = U(lo[0], 0), U(hi[0], 0)
            else: u0, u1 = U(0, lo[1]), U(0, hi[1])
            prect(u0, lo[2], u1, hi[2], C["new"], C["new"], 0.25, 1.2, "4 2")
    if wall == "front":
        prect(U(XS - 0.28, 0), 0, U(XS + 0.28, 0), P["CR1.hs"], "#111", "#222", 1)
        s.raw(f'<text x="{px(U(XS,0)):.1f}" y="{pz(P["CR1.hs"])-4:.1f}" font-size="8" text-anchor="middle">stove</text>')
    s.raw(f'<text x="{px(L_/2):.1f}" y="{pz(-0.35):.1f}" font-size="12" text-anchor="middle" font-weight="bold">{ {"front":"FRONT WALL (partition) — looking toward the live room","rear":"REAR WALL (gable) — looking toward the entry","left":"LEFT SIDE WALL (X = 0)","right":"RIGHT SIDE WALL (X = W)"}[wall] }</text>')
s = Sheet(1, 40, 40, 0, 0)
sc = 62
elevation(s, "front", 0.5, 4.6, sc); elevation(s, "rear", 0.5 + W + 1.4, 4.6, sc)
elevation(s, "left", 0.5, 4.6 + 3.6, sc); elevation(s, "right", 0.5 + D + 1.4, 4.6 + 3.6, sc)
save("PR-503_control_room_elevations", 40 + (0.5 + 2 * W + 2.4) * sc, 40 + (4.6 + 3.6 + 0.8) * sc + 150, "\n".join(s.b),
     "PR-503  CONTROL ROOM — INTERIOR ELEVATIONS v0.5 (existing openings kept; assets drawn at their owner-measured sizes)",
     "Solid = Clark asset face; dashed orange = NEW build (bench traps, corner traps, stand-off frames, door curtain). Elevations seen from inside the room.",
     ["Side walls: bench traps stop under the sills; window glass stays clear (shutters NEW-04 fold into the reveals, not drawn). Left wall: GOB-005 between the windows above the bench."])

# ================================================================== PR-504 sections + PR-505 reflection diagram
def section_cut(s, ox_m, oz_m, sc, y_cut):
    def px(x): return s.ox + (ox_m + x) * sc
    def pz(z): return s.oy + (oz_m - z) * sc
    s.raw(f'<polygon points="{" ".join(f"{px(x):.1f},{pz(z):.1f}" for x, z in G["section"])}" fill="#fff" stroke="{C["ex"]}" stroke-width="3"/>')
    for p in PL:
        if p["room"] != "Control room": continue
        lo, hi = p["aabb"]
        if not (lo[1] - 0.05 <= y_cut <= hi[1] + 0.05): continue
        if p["rot_deg"][1]:   # sloped panel: draw rotated rectangle in section
            cx, _, cz = p["centre"]; a = math.radians(p["rot_deg"][1]); w, t = p["size"][0] / 2, p["size"][2] / 2
            pts = [(cx + u * math.cos(a) + v * math.sin(a), cz - u * math.sin(a) + v * math.cos(a)) for u, v in ((-w, -t), (w, -t), (w, t), (-w, t))]
            s.raw(f'<polygon points="{" ".join(f"{px(x):.1f},{pz(z):.1f}" for x, z in pts)}" fill="{acol(p)}" fill-opacity="0.7" stroke="{acol(p)}"/>')
        else:
            s.raw(f'<rect x="{px(lo[0]):.1f}" y="{pz(hi[2]):.1f}" width="{(hi[0]-lo[0])*sc:.1f}" height="{(hi[2]-lo[2])*sc:.1f}" fill="{acol(p)}" fill-opacity="0.7" stroke="{acol(p)}"/>')
        s.raw(f'<text x="{px((lo[0]+hi[0])/2):.1f}" y="{pz(hi[2])-4:.1f}" font-size="8" text-anchor="middle" fill="{acol(p)}" font-weight="bold">{p["asset"]}</text>')
    for it in NEW:
        for g in it["geom"]:
            if it["id"] == "NEW-01":
                (cx, cy, cz), (sx_, sy_, sz_) = g["centre"], g["size"]
                s.raw(f'<rect x="{px(cx-sx_/2):.1f}" y="{pz(cz+sz_/2):.1f}" width="{sx_*sc:.1f}" height="{sz_*sc:.1f}" fill="{C["new"]}" fill-opacity="0.35" stroke="{C["new"]}" stroke-dasharray="4 2"/>')
    for k in ("L", "R"):
        x, _, z = st[k]; s.raw(f'<rect x="{px(x-0.25):.1f}" y="{pz(z+0.27):.1f}" width="{0.5*sc:.1f}" height="{0.54*sc:.1f}" fill="{C["eq"]}" fill-opacity="0.35" stroke="{C["eq"]}" stroke-dasharray="3 2"/>')
    return px, pz
s = Sheet(1, 40, 40, 0, 0); sc = 70
px, pz = section_cut(s, 0.6, 4.7, sc, 4.30)
s.raw(f'<text x="{px(W/2):.1f}" y="{pz(-0.45):.1f}" font-size="12" text-anchor="middle" font-weight="bold">SECTION A-A at Y = 4.30 (through the ceiling reflection zone), looking toward the front; speakers behind the cut dashed</text>')
for r in COV:   # ceiling + floor rays in the transverse plane (projected)
    if r["surface"] in ("flat ceiling (4.11 m)", "left sloped ceiling", "right sloped ceiling", "left side wall (X=0)", "right side wall (X=W)"):
        sp = st[r["speaker"]]; col_ = C["ray_ok"] if r["treated_by"] else C["ray_open"]
        s.raw(f'<polyline points="{px(sp[0]):.1f},{pz(sp[2]):.1f} {px(r["point"][0]):.1f},{pz(r["point"][2]):.1f} {px(LP[0]):.1f},{pz(LP[2]):.1f}" fill="none" stroke="{col_}" stroke-width="1.2" stroke-dasharray="5 3"/>')
s.raw(f'<circle cx="{px(LP[0]):.1f}" cy="{pz(LP[2]):.1f}" r="5" fill="#000"/>')
# longitudinal section B-B on the axis
ox2, oz2 = 0.6 + W + 1.6, 4.7
def qx(y): return s.ox + (ox2 + (D - y)) * sc
def qz(z): return s.oy + (oz2 - z) * sc
s.raw(f'<polygon points="{qx(0):.1f},{qz(0):.1f} {qx(D):.1f},{qz(0):.1f} {qx(D):.1f},{qz(G["hc"]):.1f} {qx(0):.1f},{qz(G["hc"]):.1f}" fill="#fff" stroke="{C["ex"]}" stroke-width="3"/>')
s.raw(f'<rect x="{qx(0)-3:.1f}" y="{qz(P["CR3.he"]):.1f}" width="6" height="{P["CR3.he"]*sc:.1f}" fill="#cfe3f0" stroke="#7aa7c7"/><rect x="{qx(0)-3:.1f}" y="{qz(P["CR3.hwt"]):.1f}" width="6" height="{(P["CR3.hwt"]-P["CR3.hwb"])*sc:.1f}" fill="#cfe3f0" stroke="#7aa7c7"/>')
s.raw(f'<rect x="{qx(D)-3:.1f}" y="{qz(P["CR1.hd"]):.1f}" width="6" height="{P["CR1.hd"]*sc:.1f}" fill="#cfe3f0" stroke="#7aa7c7"/>')
for p in PL:
    if p["room"] != "Control room": continue
    lo, hi = p["aabb"]
    if not (lo[0] - 0.4 <= AX <= hi[0] + 0.4) and p["asset"] not in ("DIF-001",): continue
    s.raw(f'<rect x="{qx(hi[1]):.1f}" y="{qz(hi[2]):.1f}" width="{(hi[1]-lo[1])*sc:.1f}" height="{(hi[2]-lo[2])*sc:.1f}" fill="{acol(p)}" fill-opacity="0.6" stroke="{acol(p)}"/>')
s.raw(f'<text x="{qx(0.2):.1f}" y="{qz(3.1):.1f}" font-size="8" fill="{C["asset"]}" font-weight="bold">DIF-001 (beside door)</text>')
c3 = next(i for i in NEW if i["id"] == "NEW-03")["geom"][0]
s.raw(f'<rect x="{qx(0.19):.1f}" y="{qz(2.2):.1f}" width="{0.06*sc:.1f}" height="{2.2*sc:.1f}" fill="{C["new"]}" fill-opacity="0.6"/>')
s.raw(f'<rect x="{qx(CON["back_edge_y"]):.1f}" y="{qz(1.041):.1f}" width="{(CON["back_edge_y"]-CON["front_edge_y"])*sc:.1f}" height="{1.041*sc:.1f}" fill="{C["eq"]}" fill-opacity="0.5" stroke="{C["eq"]}"/>')
s.raw(f'<rect x="{qx(st["L"][1]+0.42):.1f}" y="{qz(1.55):.1f}" width="{0.42*sc:.1f}" height="{0.54*sc:.1f}" fill="{C["eq"]}" fill-opacity="0.8"/>')
s.raw(f'<line x1="{qx(CIN["screen_y"]):.1f}" y1="{qz(1.2):.1f}" x2="{qx(CIN["screen_y"]):.1f}" y2="{qz(1.2+CIN["screen_height"]):.1f}" stroke="#777" stroke-width="3" stroke-dasharray="2 2"/>')
s.raw(f'<rect x="{qx(0.30+0.95):.1f}" y="{qz(0.85):.1f}" width="{0.95*sc:.1f}" height="{0.85*sc:.1f}" fill="#7d6b5a" fill-opacity="0.3"/>')
for r in COV:
    if r["speaker"] == "L" and r["surface"] in ("floor", "flat ceiling (4.11 m)", "rear wall / gable (Y=0)", "front wall / partition (Y=D)"):
        sp = st["L"]; col_ = C["ray_ok"] if r["treated_by"] else (C["ray_shadow"] if r["status"] != "untreated" else C["ray_open"])
        s.raw(f'<polyline points="{qx(sp[1]):.1f},{qz(sp[2]):.1f} {qx(r["point"][1]):.1f},{qz(r["point"][2]):.1f} {qx(LP[1]):.1f},{qz(LP[2]):.1f}" fill="none" stroke="{col_}" stroke-width="1.2" stroke-dasharray="5 3"/>')
s.raw(f'<circle cx="{qx(LP[1]):.1f}" cy="{qz(LP[2]):.1f}" r="5" fill="#000"/>')
s.raw(f'<text x="{qx(D/2):.1f}" y="{qz(-0.45):.1f}" font-size="12" text-anchor="middle" font-weight="bold">SECTION B-B on the building axis (front wall left, gable right) — L-speaker reflection paths</text>')
save("PR-504_control_room_sections", 40 + (0.6 + W + 1.6 + D + 0.6) * sc, 40 + 5.4 * sc + 150, "\n".join(s.b),
     "PR-504  CONTROL ROOM — SECTIONS A-A / B-B v0.5 with first-reflection paths",
     "Green = path meets treatment; grey = console-shadowed or rear (cardioid) radiation; red = open. Measured asymmetric tray section (model/section.py).", [])

# PR-505 plan reflection diagram + numbers
s = Sheet(68, 90, 80, -0.6, D + 0.5)
cr_base(s); equipment(s)
for p in PL:
    if p["room"] == "Control room": s.poly(fp_sorted(p), acol(p), acol(p), 0.18, 0.8, "4 2" if is_overhead(p) else None)
rows = []
for r in sorted(COV, key=lambda r: r["delay_ms"]):
    sp = st[r["speaker"]]; col_ = C["ray_ok"] if r["treated_by"] else (C["ray_shadow"] if r["status"] != "untreated" else C["ray_open"])
    s.raw(f'<polyline points="{s.X(sp[0]):.1f},{s.Y(sp[1]):.1f} {s.X(r["point"][0]):.1f},{s.Y(r["point"][1]):.1f} {s.X(LP[0]):.1f},{s.Y(LP[1]):.1f}" fill="none" stroke="{col_}" stroke-width="1.1" stroke-opacity="0.85"/>')
    s.circle(r["point"][0], r["point"][1], 4, col_)
    rows.append(r)
tx = s.X(W + 0.9); ty = 90
s.raw(f'<text x="{tx}" y="{ty}" font-size="12" font-weight="bold">First reflections at the LP (image-source, real planes)</text>')
for i, r in enumerate(rows):
    col_ = C["ray_ok"] if r["treated_by"] else (C["ray_shadow"] if r["status"] != "untreated" else C["ray_open"])
    who = ", ".join(sorted(set(r["treated_by"]))) or r["status"]
    s.raw(f'<text x="{tx}" y="{ty + 18 + 15 * i}" font-size="9.5" fill="{col_}">{r["speaker"]} · {r["surface"][:24]:<24} · +{r["delay_ms"]:.1f} ms · {r["level_dB_re_direct"]:+.1f} dB · {r["off_axis_deg"]:.0f}° off-axis · {who[:46]}</text>')
cr = AN["control_room"]; y2 = ty + 18 + 15 * len(rows) + 20
for i, t in enumerate([f"Volume {cr['volume_m3']} m³ · Schroeder ≈ {cr['schroeder_Hz_at_0.3s']:.0f} Hz · EBU 3276 T_m target {cr['EBU3276_target_Tm_s']} s",
                       "SBIR (omni ¼-wave): front wall 2.70 m → 32 Hz; floor 1.28 m → 67 Hz (console shadows the floor bounce); nearest side wall 4.5 m → 19 Hz",
                       "Axial modes at the LP: 30.5 Hz (2,0,0) and 62.8 Hz (0,3,0) peak; 83.7 Hz (0,4,0) null — see ANALYSIS_TABLES.md",
                       "Levels: spherical spreading only. Absorption and the RL 901K's cardioid pattern lower the real reflections further."]):
    s.raw(f'<text x="{tx}" y="{y2 + 15 * i}" font-size="10" fill="#333">{t}</text>')
save("PR-505_monitoring_reflections", tx + 720, s.Y(-0.9) + 120, "\n".join(s.b),
     "PR-505  MONITORING & FIRST-REFLECTION DIAGRAM v0.5 (actual RL 901K pair, LP at 0.375 L from the gable)",
     "Every first-order reflection from both speakers to the LP, traced on the measured surfaces; colour = what intercepts it in the v0.5 layout (acoustics/out/reflection_coverage.json).", [])

# ================================================================== PR-506 lounge in two modes
def lounge_view(s, mode):
    for nm, v in LNG["obstacles"].items():
        pts = v
        col_ = "#999"
        if "doorway" in nm: s.poly(pts, C["zone"], C["zone"], 0.12, 1, "6 3")
        elif "hearth" in nm: s.poly(pts, "#777", "#bbb", 0.3, 1, "3 2")
        else: s.poly(pts, col_, col_, 0.15, 1, "3 2")
    s.rect(XS - 0.28, YS - 0.25, XS + 0.28, YS + 0.25, "#111", "#222", 1)
    FIRE = LNG["fire_point"]
    if mode == "fire":
        for nm, v in LNG["fireside_mode"].items():
            if "footprint" in v:
                s.poly(v["footprint"], C["lounge"], C["lounge"], 0.5, 1.5); s.line(v["centre"][0], v["centre"][1], FIRE[0], FIRE[1], C["lounge"], 1.3, "2 3")
                lx, ly = (v["centre"][0] - 0.9, v["centre"][1] - 0.95) if nm == "loveseat" else (v["centre"][0] - 0.1, v["centre"][1] - 0.62)
                s.text(lx, ly, nm.split(" A")[0], C["lounge"], 9, weight="bold")
                s.text(lx, ly - 0.2, f'{v["to_fire_m"]} m to fire · {v["stove_clearance_m"]} m stove clearance', C["lounge"], 8)
            else: s.circle(*v["centre"], 0.25 * s.sc, C["lounge"])
        s.circle(FIRE[0], FIRE[1], 5, "#e25822")
    else:
        v = LNG["fireside_mode"]["loveseat"]; s.poly(v["footprint"], C["lounge"], C["lounge"], 0.5, 1.5); s.text(v["centre"][0], v["centre"][1], "loveseat stays", "#fff", 8, weight="bold")
        s.line(AX - CIN["screen_width"] / 2, CIN["screen_y"], AX + CIN["screen_width"] / 2, CIN["screen_y"], "#333", 3)
        s.text(AX, CIN["screen_y"] + 0.15, "screen down (faces the rear row)", "#333", 8)
        s.rect(AX - 1.4, 0.30, AX + 1.4, 1.25, "#7d6b5a", "#7d6b5a", 0.4, 1.2); s.text(AX, 0.75, "sofa 3–4", "#fff", 8, weight="bold")
        for nm, v in LNG["cinema_mode"].items():
            x, y = v["centre"]; s.rect(x - 0.4, y - 0.4, x + 0.4, y + 0.4, C["lounge"], C["lounge"], 0.5, 1.5)
            s.line(x, y, AX, CIN["screen_y"], C["lounge"], 1, "2 3"); s.text(x, y - 0.6, nm.split(" (")[0], C["lounge"], 8)
            s.text(x, y - 0.75, f'{v["screen_view_angle_deg"]}° screen width', C["lounge"], 7)
        fa = LNG["fireside_mode"]["swivel armchair A"]["centre"]; ca = LNG["cinema_mode"]["swivel armchair A (rolls back from the fire)"]["centre"]
        s.raw(f'<line x1="{s.X(fa[0]):.1f}" y1="{s.Y(fa[1]):.1f}" x2="{s.X(ca[0]):.1f}" y2="{s.Y(ca[1]):.1f}" stroke="{C["lounge"]}" stroke-width="1.5" marker-end="url(#arr)" stroke-dasharray="6 3"/>')
        s.text((fa[0] + ca[0]) / 2 - 0.5, (fa[1] + ca[1]) / 2, "armchair A rolls back (glides)", C["lounge"], 8, rot=-75)
    s.rect(0, 0, W, D, C["ex"], "none", 0, 3)
    s.rect(CON["x0"], CON["front_edge_y"], CON["x1"], CON["back_edge_y"], C["eq"], C["eq"], 0.4, 1.5)
    for k in ("L", "R"): s.circle(st[k][0], st[k][1], 6, C["eq"])
    s.circle(LP[0], LP[1], 4, "#000")
s1 = Sheet(55, 50, 70, -0.4, D + 0.4); lounge_view(s1, "fire")
s1.text(W / 2, D + 0.15, "FIRESIDE MODE — 3 seats face the stove glass", C["lounge"], 13, weight="bold")
s2 = Sheet(55, 50 + (W + 1.4) * 55, 70, -0.4, D + 0.4); lounge_view(s2, "cinema")
s2.text(W / 2, D + 0.15, "CINEMA MODE — sofa + 2 swivel armchairs (5–6 seats, as v0.4)", C["lounge"], 13, weight="bold")
defs = f'<defs><marker id="arr" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto"><path d="M0,0 L10,4 L0,8 z" fill="{C["lounge"]}"/></marker></defs>'
chk = LNG["checks"]
save("PR-506_lounge_two_modes", 50 + 2 * (W + 1.4) * 55, 70 + (D + 0.9) * 55 + 200, defs + "\n".join(s1.b + s2.b),
     "PR-506  FIRESIDE LOUNGE — CORRECTED (owner-authorised): seats now face the existing wood stove; two simple furniture modes",
     "Grey dashed = kept-clear zones (speaker + cardioid clear zone, sub, bench/corner traps, front frames, future Ls stand); yellow = doorway route to the live room; hearth pad hatched.",
     [f"Checks: minimum stove clearance {chk['min stove clearance (m)']} m (≥ 0.90 m placeholder); doorway route clear; lounge furniture ≤ 0.80 m high, below the RL 901K acoustic centre ({chk['speaker acoustic-centre height (m)']} m); nothing between the LP and either speaker.",
      "Tested: a third seat (second armchair) does not fit around the fire behind the speaker line with these clearances, so armchair B lives in the rear row in both modes.",
      "Honest limit: the lounge sits behind the drop-down screen; it is a fireside / listen-back spot, not a cinema seat. No mechanisms: armchair A is a swivel chair on felt glides."])

# ================================================================== PR-511 live room treatment + configurations
def live_base(s, scale_labels=True):
    s.rect(LL, Y_MID1, LR, Y_LG, C["ex"], "#fff", 1, 3)
    s.line(LL, Y_LOFT_END, LR, Y_LOFT_END, C["ex"], 1, "3 3")
    s.rect(AX - GD / 2, Y_MID1 + 0.3, AX + GD / 2, Y_LG, C["zone"], C["zone"], 0.06, 1, "8 4")
    for x0_, x1_ in ((LL + 0.3, AX - GD / 2 - 0.3), (AX + GD / 2 + 0.3, LR - 0.3)):
        s.rect(x0_, Y_MID1 + 0.4, x1_, Y_LOFT_END - 0.7, C["zone"], C["zone"], 0.12, 1.5)
    s.rect(AX - GD / 2, Y_LG, AX + GD / 2, Y_LG + 0.2, C["ex"], C["ex"], 1)
    for x, y in ((AX - 2.6, Y_MID1 + 2.3), (AX + 2.6, Y_MID1 + 2.3), (AX - 2.6, Y_LOFT_END - 0.4), (AX + 2.6, Y_LOFT_END - 0.4), (AX, Y_LOFT_END - 0.4)):
        s.rect(x - 0.1, y - 0.1, x + 0.1, y + 0.1, C["ex"], C["ex"], 1)
    for y0_ in (Y_MID1 + 1.5, Y_MID1 + 5.0, Y_LOFT_END + 1.5, Y_LOFT_END + 5.0):
        for x in (LL, LR): s.rect(x - 0.05, y0_, x + 0.05, y0_ + 1.4, "#7aa7c7", "#cfe3f0", 1)
def piano(s, x, y, deg):
    rot = math.radians(deg); pts = [(-0.76, 0), (0.76, 0), (0.76, 0.55), (0.45, 1.25), (0.15, 2.13), (-0.35, 2.13), (-0.76, 1.15)]
    s.poly([(x + px_ * math.cos(rot) - py_ * math.sin(rot), y + px_ * math.sin(rot) + py_ * math.cos(rot)) for px_, py_ in pts], "#111", "#111", 0.85)
def gobo(s, x, y, yaw, w, col_):
    a = math.radians(yaw); dx, dy = math.cos(a) * w / 2, math.sin(a) * w / 2
    s.line(x - dx, y - dy, x + dx, y + dy, col_, 5)
lv = [p for p in PL if p["room"] == "Live room"]
s = Sheet(40, 60, 60, LL - 0.6, Y_LG + 0.8)
live_base(s)
for p in lv:
    if p["shape"].startswith("gobo"): continue
    dash = "6 3" if is_overhead(p) else None
    s.poly(fp_sorted(p), acol(p), acol(p) if not dash else "none", 0.55, 1.4, dash)
for p in lv:
    if p["shape"].startswith("gobo"): gobo(s, p["centre"][0], p["centre"][1], p["rot_deg"][2], p["size"][0], acol(p))
piano(s, AX - 1.4, Y_LOFT_END + 2.6, -25)
for k in range(4):
    a = math.radians(200 + k * 45); s.circle(AX + 2.2 + 1.2 * math.cos(a), Y_LOFT_END + 4.6 + 1.2 * math.sin(a), 0.2 * 40, C["new"])
s.circle(AX + 3.35, 24.15, 0.75 * 40, "none", "#333"); s.text(AX + 3.35, 24.1, "drums", "#333", 9)
lbl = [("HYB-001 ×2 overhead (30 in chains)", AX, 26.6 + 1.5), ("HYB-001 vertical", 9.1, Y_LG - 0.55), ("PRF-002 ×3", 1.75, Y_LG - 0.45),
       ("PRF-001 ×4 (shimmed)", LL + 0.9, 23.6), ("DIF-003 + BTR-002", LL + 1.0, 26.85), ("WOOD-001…005 rustic wall (11 pcs)", LR - 1.6, 25.6),
       ("GOB-003 ×2 under joists", (LL + AX - GD / 2) / 2, 21.3), ("GOB-006 ×2 under joists", (AX + GD / 2 + LR) / 2, 21.3),
       ("GOB-001 ×5 wheeled", AX + 3.4, 25.9), ("GOB-002 ×2 half-height", AX + 2.6, 29.9), ("MACHINERY STORAGE", (LL + AX - GD / 2) / 2, 18.0), ("MACHINERY STORAGE", (AX + GD / 2 + LR) / 2, 18.0),
       ("MACHINERY AISLE 3.7 m → garage door", AX, Y_MID1 + 0.6), ("grand piano", AX - 1.9, Y_LOFT_END + 2.2), ("strings", AX + 2.2, Y_LOFT_END + 4.6)]
for t, x, y in lbl: s.text(x, y, t, C["zone"] if "MACHIN" in t else C["txt"], 9, weight="bold" if "MACHIN" in t else "normal")
s.text(AX, Y_LOFT_END + 0.15, "loft edge (under-loft 2.59 m | tray zone 4.33 m)", C["ex"], 8)
# configuration minis
cfg = [("A  PIANO / CHAMBER (bright)", "gobos parked in the bays; HYBs raised; piano on the axis", [], [(AX, 25.6, 0)]),
       ("B  ENSEMBLE (as modelled, neutral)", "3 gobos around drums, 2 screening piano/strings; GOB-002 at amps", [(p["centre"][0], p["centre"][1], p["rot_deg"][2], p["size"][0]) for p in lv if p["shape"].startswith("gobo")], [(AX - 1.4, Y_LOFT_END + 2.6, -25)]),
       ("C  BAND / OVERDUBS (dead)", "all gobos in booths; NEW curtains drawn on the tray side walls", [(AX + 2.4, 24.6, 75, 1.26), (AX + 3.1, 25.4, 15, 1.26), (AX + 4.2, 25.2, -30, 1.26), (AX - 3.0, 24.0, 90, 1.26), (AX - 2.4, 25.0, 0, 1.26), (AX + 0.6, 28.8, 60, 1.4), (AX - 0.6, 28.8, -60, 1.4)], [(AX - 1.4, Y_LOFT_END + 2.6, -25)]),
       ("D  FARM MODE", "aisle cleared to the garage door; piano on a locked dolly in the west bay; gobos nested", [(LL + 0.5, 23.2 + 0.3 * i, 90, 1.26) for i in range(5)] + [(LR - 0.5, 23.4 + 0.3 * i, 90, 1.4) for i in range(2)], [(LL + 2.0, Y_MID1 + 4.6, 90)])]
mini = []
for i, (t, sub, gob, pianos) in enumerate(cfg):
    m = Sheet(17, s.X(LR + 1.0) + 40 + (i % 2) * ((LR - LL + 1.2) * 17 + 30), 60 + (i // 2) * ((Y_LG - Y_MID1 + 2.4) * 17 + 40), LL - 0.6, Y_LG + 0.8)
    live_base(m)
    for p in lv:
        if not p["shape"].startswith("gobo") and not is_overhead(p): m.poly(fp_sorted(p), acol(p), acol(p), 0.5, 0.8)
    for gx, gy, gyaw, gw in gob: gobo(m, gx, gy, gyaw, gw, C["asset"])
    for px_, py_, d_ in pianos: piano(m, px_, py_, d_)
    if i == 3: m.rect(AX - GD / 2, Y_MID1 + 0.3, AX + GD / 2, Y_LG, C["zone"], C["zone"], 0.30, 1.5)
    if i == 2:
        for x in (LL + 0.12, LR - 0.12): m.line(x, Y_LOFT_END + 0.5, x, Y_LOFT_END + 6.5, C["new"], 4)
    m.text((LL + LR) / 2, Y_LG + 0.45, t, "#222", 11, weight="bold"); m.text((LL + LR) / 2, Y_MID1 - 0.8, sub, "#444", 8)
    mini += m.b
save("PR-511_live_room_treatment_configs", s.X(LR + 1.0) + 40 + 2 * ((LR - LL + 1.2) * 17 + 30), s.Y(Y_MID1 - 2.6) + 120, "\n".join(s.b + mini),
     "PR-511  LIVE ROOM — v0.5 TREATMENT PLAN (left) and four configurations (right); farm machinery stays",
     "All 34 live-room units are Clark assets (no new walls). Overhead items dashed. Gobos are drawn as lines at their measured widths; configurations are suggestions, not fixtures.",
     ["Under-loft GOB-003/006 hang only over the storage bays (2.46 m clear above the slab), never over the machinery aisle; check the tallest stored machine.",
      "Decay ranges per configuration: acoustics/out/ANALYSIS_TABLES.md (generic material classes; measurement required)."])

# ================================================================== PR-512 support rooms
s = Sheet(60, 60, 60, -0.6, Y_MID1 + 0.6)
s.rect(0, Y_PART1, W, Y_MID1, C["ex"], "#fff", 1, 3)
corr0, corr1 = AX - 0.70, AX + 0.70
for x in (corr0, corr1): s.line(x, Y_PART1, x, Y_MID1, C["ex"], 2)
for x0_, x1_, y in ((0, corr0, Y_PART1 + 4.55), (corr1, W, Y_PART1 + 2.05), (corr1, W, Y_PART1 + 5.75)): s.line(x0_, y, x1_, y, C["ex"], 2)
for p in PL:
    if p["room"] in ("Control room", "Live room"): continue
    s.poly(fp_sorted(p), acol(p), acol(p), 0.6, 1.4, "6 3" if p["aabb"][0][2] > 1.5 else None)
    lo, hi = p["aabb"]; s.text((lo[0] + hi[0]) / 2 + (0.35 if lo[0] < 0.3 else (-0.35 if hi[0] > W - 0.3 else 0)), (lo[1] + hi[1]) / 2 + (0.25 if (hi[0] - lo[0]) > 0.5 else 0), p["asset"], acol(p), 8, weight="bold")
s.text(corr0 / 2, Y_PART1 + 4.3, "VOCAL BOOTH (existing room)", C["txt"], 11, weight="bold"); s.text((corr1 + W) / 2, Y_PART1 + 1.8, "MACHINE ROOM", C["txt"], 11, weight="bold")
s.text((corr1 + W) / 2, Y_PART1 + 5.5, "AMP / ISO BOOTH", C["txt"], 11, weight="bold"); s.text(AX, Y_PART1 + 4.0, "corridor", C["ex"], 9, rot=-90)
s.text(corr0 / 2, Y_MID1 - 0.4, "storage / mic locker", C["ex"], 9); s.text((corr1 + W) / 2, Y_MID1 - 0.4, "storage", C["ex"], 9)
save("PR-512_support_rooms_treatment", s.X(W + 0.6) + 420, s.Y(Y_PART1 - 0.8) + 150, "\n".join(s.b),
     "PR-512  SUPPORT ROOMS — v0.5 TREATMENT (existing middle-zone rooms only; partitions scan-inferred, unchanged)",
     "Vocal booth reuses the Clark vocal-booth set (DIF-004, BTR-003, ABS-015/016, PAN-002) plus Sunny ABS-001/008/011 and GOB-005 ×2; amp booth and machine room take Sunny panels.",
     ["Magenta = depth PROVISIONAL (owner sheet has no depth; modelled 0.05 m). ABS-014 is HELD (possible duplicate of ABS-010); ABS-004 and ABS-006 are in reserve."])
print("wrote", sorted(os.listdir(OUT)))
print("reflection coverage:", [(r["speaker"], r["surface"][:18], r["status"], r["treated_by"]) for r in COV])
