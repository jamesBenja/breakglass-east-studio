"""Proposed plans (SVG): PR-101 whole building, PR-102 control room monitoring layout.

    python3 model/make_proposed_plans.py  -> drawings/PR-101_building_plan.svg, drawings/PR-102_control_room_plan.svg
Same data as the Blender model (solve_result, scan_building_measurements, monitoring_geometry).
PROPOSED DESIGN on a provisional existing shell. Not for construction.
"""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from section import geom
P = {k: v["value"] for k, v in json.load(open(os.path.join(HERE, "solve_result.json")))["params"].items()}
G = geom(P); B = json.load(open(os.path.join(HERE, "scan_building_measurements.json")))
MG = json.load(open(os.path.join(HERE, "monitoring_geometry.json")))
W, D, AX = G["W"], G["D"], G["xf"]
Y_OFF = 15.185; Y_MID1 = 1.0 + Y_OFF; Y_LOFT_END = 7.7 + Y_OFF; Y_LG = B["live_gable_y"] + Y_OFF
LL, LR = AX - 6.15, AX + 5.75
OUT = os.path.join(ROOT, "drawings")
C = {"ex": "#555", "pr": "#b5651d", "eq": "#1f4e79", "imm": "#7a2e8e", "zone": "#c9a400", "unk": "#c2187a", "txt": "#222"}

def frame(w, h, body, title, sub):
    w = max(w, 1400)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" font-family="Helvetica,Arial,sans-serif">
<rect width="{w}" height="{h}" fill="#fbfaf7"/>{body}
<g font-size="11" fill="#333"><text x="20" y="{h-62}" font-size="15" font-weight="bold">{title}</text>
<text x="20" y="{h-44}">{sub}</text>
<text x="20" y="{h-28}">PROPOSED DESIGN v0.4 on a provisional existing shell (phone-LiDAR + photos, about +/-0.1-0.2 m). NOT FOR CONSTRUCTION, PRICING OR PERMIT. Acoustician/architect review required.</text>
<text x="20" y="{h-10}"><tspan fill="{C['ex']}">&#9632; existing</tspan>  <tspan fill="{C['eq']}">&#9632; actual equipment (tape)</tspan>  <tspan fill="{C['pr']}">&#9632; proposed</tspan>  <tspan fill="{C['imm']}">&#9679; immersive 7.1.4 (phase P7)</tspan>  <tspan fill="{C['zone']}">&#9632; machinery zone/aisle</tspan>  <tspan fill="{C['unk']}">&#9632; placeholder/unknown</tspan></text></g></svg>'''

# ------------------------------------------------------------ PR-101 building plan
sc = 26; ox, oy = 60, 60
X = lambda x: ox + (x + 0.8) * sc
Y = lambda y: oy + (Y_LG + 0.6 - y) * sc
b = []
def rect(x0, y0, x1, y1, stroke, fill="none", sw=1.5, dash=None, op=1):
    da = f' stroke-dasharray="{dash}"' if dash else ""
    b.append(f'<rect x="{X(min(x0,x1))}" y="{Y(max(y0,y1))}" width="{abs(x1-x0)*sc}" height="{abs(y1-y0)*sc}" fill="{fill}" fill-opacity="{op}" stroke="{stroke}" stroke-width="{sw}"{da}/>')
def text(x, y, s, col=C["txt"], size=11, anchor="middle", weight="normal"):
    b.append(f'<text x="{X(x)}" y="{Y(y)}" font-size="{size}" text-anchor="{anchor}" fill="{col}" font-weight="{weight}">{s}</text>')
rect(0, 0, W, D, C["ex"], sw=3); rect(0, D + 0.15, W, Y_MID1, C["ex"], sw=2.5); rect(LL, Y_MID1, LR, Y_LG, C["ex"], sw=3)
rect(AX - 2.6, D + 0.15, AX + 2.6, Y_LOFT_END, C["ex"], sw=1, dash="6 4"); text(AX + 2.4, Y_MID1 - 0.4, "LOFT above (deck +2.79 m, headroom >=2.1 m only ~2 m wide)", C["ex"], 9, "end")
for x in (AX - 0.7, AX + 0.7): b.append(f'<line x1="{X(x)}" y1="{Y(D+0.15)}" x2="{X(x)}" y2="{Y(Y_MID1)}" stroke="{C["ex"]}" stroke-width="1.5"/>')
for x0_, x1_, y_ in ((0, AX - 0.7, D + 0.15 + 4.55), (AX + 0.7, W, D + 0.15 + 2.05), (AX + 0.7, W, D + 0.15 + 5.75)):
    b.append(f'<line x1="{X(x0_)}" y1="{Y(y_)}" x2="{X(x1_)}" y2="{Y(y_)}" stroke="{C["ex"]}" stroke-width="1.5"/>')
text(AX, D + 4.2, "corridor", C["ex"], 9); text((AX - 0.7) / 2, D + 2.4, "VOCAL / ISO", C["pr"], 10, weight="bold"); text((AX - 0.7) / 2, D + 2.0, "(existing room)", C["ex"], 8)
text((AX + 0.7 + W) / 2, D + 1.2, "MACHINE ROOM", C["pr"], 10, weight="bold"); text((AX + 0.7 + W) / 2, D + 4.0, "AMP / ISO", C["pr"], 10, weight="bold")
text((AX - 0.7) / 2, D + 6.5, "STORAGE / MIC LOCKER", C["pr"], 9); text((AX + 0.7 + W) / 2, D + 7.0, "STORAGE", C["pr"], 9)
b.append(f'<line x1="{X(LL)}" y1="{Y(Y_LOFT_END)}" x2="{X(LR)}" y2="{Y(Y_LOFT_END)}" stroke="{C["ex"]}" stroke-dasharray="3 3"/>')
text(LR - 0.2, Y_LOFT_END - 0.35, "under-loft 2.59 m | tray zone 4.33 m", C["ex"], 9, "end")
GD = 3.7
rect(AX - GD/2, Y_MID1 + 0.3, AX + GD/2, Y_LG, C["zone"], fill=C["zone"], op=0.08, dash="8 4")
text(AX, Y_LG - 0.6, "MACHINERY AISLE 3.7 m", C["zone"], 10, weight="bold")
b.append(f'<text x="{X(LR + 0.5)}" y="{Y(Y_LG - 1.5)}" font-size="10" fill="{C["zone"]}">FARM MODE: aisle cleared, piano on locked dolly</text>')
b.append(f'<text x="{X(LR + 0.5)}" y="{Y(Y_LG - 1.9)}" font-size="10" fill="{C["zone"]}">rolls to the west bay, machines move in/out.</text>')
b.append(f'<text x="{X(LR + 0.5)}" y="{Y(Y_LG - 2.5)}" font-size="10" fill="{C["pr"]}">STUDIO MODE: machines parked under the loft;</text>')
b.append(f'<text x="{X(LR + 0.5)}" y="{Y(Y_LG - 2.9)}" font-size="10" fill="{C["pr"]}">the aisle becomes performance floor (shown).</text>')
for x0_, x1_ in ((LL + 0.3, AX - GD/2 - 0.3), (AX + GD/2 + 0.3, LR - 0.3)):
    rect(x0_, Y_MID1 + 0.4, x1_, Y_LOFT_END - 0.7, C["zone"], fill=C["zone"], op=0.15, sw=2)
    text((x0_ + x1_)/2, (Y_MID1 + Y_LOFT_END)/2, "MACHINERY STORAGE", C["zone"], 10, weight="bold"); text((x0_ + x1_)/2, (Y_MID1 + Y_LOFT_END)/2 - 0.45, "(owner list/sizes TBD)", C["unk"], 8)
b.append(f'<rect x="{X(AX - GD/2)}" y="{Y(Y_LG + 0.25)}" width="{GD*sc}" height="{0.25*sc}" fill="{C["ex"]}"/>'); text(AX, Y_LG + 0.55, "GARAGE DOOR (size to tape)", C["ex"], 9)
# piano + quartet
px, py, rot = AX - 1.4, Y_LOFT_END + 2.6, math.radians(-25)
pts = [(-0.76, 0), (0.76, 0), (0.76, 0.55), (0.45, 1.25), (0.15, 2.13), (-0.35, 2.13), (-0.76, 1.15)]
pp = " ".join(f"{X(px + x*math.cos(rot) - y*math.sin(rot))},{Y(py + x*math.sin(rot) + y*math.cos(rot))}" for x, y in pts)
b.append(f'<polygon points="{pp}" fill="#111" fill-opacity="0.85"/>'); text(px - 1.5, py + 0.5, "GRAND PIANO", C["pr"], 10, "end", "bold")
for k in range(4):
    a = math.radians(200 + k * 45); x, y = AX + 2.2 + 1.2*math.cos(a), Y_LOFT_END + 4.6 + 1.2*math.sin(a)
    b.append(f'<circle cx="{X(x)}" cy="{Y(y)}" r="{0.22*sc}" fill="{C["pr"]}" fill-opacity="0.6"/>')
text(AX + 2.2, Y_LOFT_END + 5.0, "string quartet", C["pr"], 9)
for x in (LL + 0.06, LR - 0.06):
    for k in range(5):
        y0_ = Y_LOFT_END + 0.6 + k*1.45; b.append(f'<line x1="{X(x)}" y1="{Y(y0_)}" x2="{X(x)}" y2="{Y(y0_+1.2)}" stroke="{C["pr"]}" stroke-width="5"/>')
text(LL + 0.4, Y_LOFT_END + 7.6, "variable panels", C["pr"], 8, "start")
# control room summary
st = MG["stereo"]; lp = st["listening_position"]
for k in ("L", "R"): b.append(f'<circle cx="{X(st[k][0])}" cy="{Y(st[k][1])}" r="5" fill="{C["eq"]}"/>')
rect(st["console"]["x0"], st["console"]["front_edge_y"], st["console"]["x1"], st["console"]["back_edge_y"], C["eq"], fill=C["eq"], op=0.35)
b.append(f'<circle cx="{X(lp[0])}" cy="{Y(lp[1])}" r="4" fill="#000"/>')
text(AX, D/2 - 2.4, "CONTROL ROOM — see PR-102", C["pr"], 11, weight="bold")
text(AX, -0.55, "GABLE ENTRY", C["ex"], 9)
b.append(f'<line x1="{X(AX)}" y1="{Y(-0.4)}" x2="{X(AX)}" y2="{Y(Y_LG + 0.3)}" stroke="#999" stroke-dasharray="14 4 2 4" stroke-width="0.8"/>')
text(AX + 0.15, Y_LG + 0.35, "building axis", "#888", 8, "start")
# dims
b.append(f'<text x="{X(W + 0.9)}" y="{Y(D/2)}" font-size="10" fill="{C["ex"]}">8.20</text><text x="{X(LR + 0.6)}" y="{Y((Y_MID1+Y_LG)/2)}" font-size="10" fill="{C["ex"]}">{Y_LG - Y_MID1:.1f}</text>')
b.append(f'<text x="{X(LR + 0.6)}" y="{Y((D+Y_MID1)/2)}" font-size="10" fill="{C["ex"]}">{Y_MID1 - D:.1f}</text>')
open(os.path.join(OUT, "PR-101_building_plan.svg"), "w").write(frame(int(X(LR + 2.2)), int(Y(-1.4)) + 90, "\n".join(b),
    "PR-101  WHOLE BUILDING — PROPOSED PLAN (control room / support rooms / live room; loft dashed)",
    f"Interior length about {Y_LG + 0.0:.1f} m gable to gable; dims in metres; existing partitions in the middle zone are scan-inferred and unchanged (no new walls)."))

# ------------------------------------------------------------ PR-102 control room
sc = 70; ox, oy = 80, 70
X = lambda x: ox + x * sc
Y = lambda y: oy + (D + 0.4 - y) * sc
b = []
b.append(f'<rect x="{X(0)}" y="{Y(D)}" width="{W*sc}" height="{D*sc}" fill="#fff" stroke="{C["ex"]}" stroke-width="4"/>')
for x in (G["xL"], G["xR"]): b.append(f'<line x1="{X(x)}" y1="{Y(0)}" x2="{X(x)}" y2="{Y(D)}" stroke="{C["ex"]}" stroke-dasharray="8 5"/>')
for x in (G["xc1"], G["xc2"]): b.append(f'<line x1="{X(x)}" y1="{Y(0)}" x2="{X(x)}" y2="{Y(D)}" stroke="{C["ex"]}" stroke-dasharray="2 4"/>')
for x, y in ((G["xL"], P["ypl"]), (G["xR"], P["ypr"])): b.append(f'<rect x="{X(x)-5}" y="{Y(y)-5}" width="10" height="10" fill="{C["ex"]}"/>')
b.append(f'<line x1="{X(AX)}" y1="{Y(-0.3)}" x2="{X(AX)}" y2="{Y(D + 0.3)}" stroke="#999" stroke-dasharray="14 4 2 4"/>')
# proposed treatment
STX = P["g_xs"]; STY = min(P["g_ys"], D - 0.35)
b.append(f'<rect x="{X(0)}" y="{Y(D)}" width="{(STX-0.28-0.9)*sc}" height="{0.3*sc}" fill="{C["pr"]}" fill-opacity="0.35"/>')
# existing wood stove (kept) + fireside lounge
b.append(f'<rect x="{X(STX-0.28)}" y="{Y(STY+0.25)}" width="{0.56*sc}" height="{0.5*sc}" fill="#222"/>')
b.append(f'<text x="{X(STX)}" y="{Y(STY+0.25)-4}" font-size="9" text-anchor="middle" fill="#222">wood stove (existing, kept)</text>')
b.append(f'<rect x="{X(STX-2.0)}" y="{Y(D-0.75)}" width="{2.6*sc}" height="{(D-0.75-(st["L"][1]+0.55))*sc}" fill="{C["pr"]}" fill-opacity="0.12" stroke="{C["pr"]}" stroke-dasharray="4 3"/>')
b.append(f'<text x="{X(STX-1.0)}" y="{Y(st["L"][1]+0.9)}" font-size="11" text-anchor="middle" fill="{C["pr"]}" font-weight="bold">FIRESIDE LOUNGE</text>')
b.append(f'<text x="{X(STX-1.0)}" y="{Y(st["L"][1]+0.9)+13}" font-size="9" text-anchor="middle" fill="{C["pr"]}">low soft seating; doorway route kept clear</text>')
b.append(f'<rect x="{X(P["CR1.xd2"]+0.05)}" y="{Y(D)}" width="{(W-P["CR1.xd2"]-0.05)*sc}" height="{0.3*sc}" fill="{C["pr"]}" fill-opacity="0.35"/>')
b.append(f'<text x="{X(0.2)}" y="{Y(D)+15}" font-size="9" fill="{C["pr"]}">front absorber (stove clearance kept)</text>')
for x0_ in (0, W - 0.75): b.append(f'<rect x="{X(x0_)}" y="{Y(D-0.35)}" width="{0.75*sc}" height="{(D-0.95)*sc}" fill="{C["pr"]}" fill-opacity="0.2"/>')
b.append(f'<text x="{X(0.38)}" y="{Y(D/2)}" font-size="10" fill="{C["pr"]}" transform="rotate(-90 {X(0.38)} {Y(D/2)})" text-anchor="middle">LF trap under windows (0.75 m)</text>')
b.append(f'<text x="{X(W-0.38)}" y="{Y(D/2)}" font-size="10" fill="{C["pr"]}" transform="rotate(-90 {X(W-0.38)} {Y(D/2)})" text-anchor="middle">LF trap under windows (0.75 m)</text>')
b.append(f'<rect x="{X(0.3)}" y="{Y(0.2)}" width="{(W-0.6)*sc}" height="{0.2*sc}" fill="{C["pr"]}" fill-opacity="0.45"/>')
b.append(f'<text x="{X(W/2)}" y="{Y(0.2)-6}" font-size="10" text-anchor="middle" fill="{C["pr"]}">rear-wall diffusion (reclaimed Clark wood) between existing openings</text>')
lp = st["listening_position"]
b.append(f'<rect x="{X(AX-1.55)}" y="{Y(st["L"][1]-0.2)}" width="{3.1*sc}" height="{(st["L"][1]-0.2-(lp[1]-0.6))*sc}" fill="none" stroke="{C["pr"]}" stroke-dasharray="4 3"/>')
b.append(f'<text x="{X(AX+1.6)}" y="{Y(lp[1]+0.9)}" font-size="10" fill="{C["pr"]}">ceiling cloud above (3.9 m)</text>')
CIN = MG["cinema"]
b.append(f'<rect x="{X(0.85)}" y="{Y(3.9)}" width="{0.7*sc}" height="{2.2*sc}" fill="{C["pr"]}" fill-opacity="0.3" stroke="{C["pr"]}"/><text x="{X(1.2)}" y="{Y(2.8)}" font-size="9" text-anchor="middle" fill="{C["pr"]}" transform="rotate(-90 {X(1.2)} {Y(2.8)})">producer / outboard desk</text>')
b.append(f'<rect x="{X(AX-1.4)}" y="{Y(1.25)}" width="{2.8*sc}" height="{0.95*sc}" fill="{C["pr"]}" fill-opacity="0.3" stroke="{C["pr"]}"/><text x="{X(AX)}" y="{Y(0.75)}" font-size="10" text-anchor="middle" fill="{C["pr"]}">FAMILY CINEMA SOFA</text>')
for cx in (AX - 2.75, AX + 2.75):
    b.append(f'<rect x="{X(cx-0.4)}" y="{Y(1.85)}" width="{0.8*sc}" height="{0.8*sc}" fill="{C["pr"]}" fill-opacity="0.3" stroke="{C["pr"]}"/>')
se = CIN["sofa_eye"]
for sx in (CIN["screen_width"]/2, -CIN["screen_width"]/2):
    b.append(f'<line x1="{X(se[0])}" y1="{Y(se[1])}" x2="{X(AX+sx)}" y2="{Y(CIN["screen_y"])}" stroke="#555" stroke-dasharray="2 4"/>')
b.append(f'<text x="{X(AX+1.0)}" y="{Y(se[1]+0.55)}" font-size="9" fill="#555">{CIN["viewing_distance"]} m to screen, {CIN["horizontal_view_angle_deg"]} deg wide, centre {CIN["elevation_to_centre_deg"]} deg up</text>')
b.append(f'<rect x="{X(AX-0.25)}" y="{Y(1.2)}" width="{0.5*sc}" height="{0.5*sc}" fill="none" stroke="#555"/><text x="{X(AX+0.3)}" y="{Y(1.0)}" font-size="8" fill="#555">projector (ceiling)</text>')
# equipment
c_ = st["console"]
b.append(f'<rect x="{X(c_["x0"])}" y="{Y(c_["back_edge_y"])}" width="{(c_["x1"]-c_["x0"])*sc}" height="{(c_["back_edge_y"]-c_["front_edge_y"])*sc}" fill="{C["eq"]}" fill-opacity="0.45" stroke="{C["eq"]}" stroke-width="2"/>')
b.append(f'<text x="{X(AX)}" y="{Y((c_["front_edge_y"]+c_["back_edge_y"])/2)+4}" font-size="10" text-anchor="middle" fill="#fff" font-weight="bold">SPECTRA SONICS</text>')
b.append(f'<text x="{X(AX)}" y="{Y((c_["front_edge_y"]+c_["back_edge_y"])/2)+18}" font-size="9" text-anchor="middle" fill="#fff">1585 x 1194 mm</text>')
for k in ("L", "R"):
    x, y, _ = st[k]; ang = math.atan2(lp[0]-x, -(lp[1]-y))
    pts = [(-0.25, 0), (0.25, 0), (0.25, 0.424), (-0.25, 0.424)]
    pp = " ".join(f"{X(x + px*math.cos(ang) - py*math.sin(ang))},{Y(y + px*math.sin(ang) + py*math.cos(ang))}" for px, py in pts)
    b.append(f'<polygon points="{pp}" fill="{C["eq"]}"/>')
    b.append(f'<line x1="{X(x)}" y1="{Y(y)}" x2="{X(lp[0])}" y2="{Y(lp[1])}" stroke="{C["eq"]}" stroke-dasharray="5 3"/>')
    b.append(f'<text x="{X(x) + (-60 if k == "L" else 60)}" y="{Y(y-0.15)}" font-size="10" text-anchor="middle" fill="{C["eq"]}" font-weight="bold">RL 901K {k}</text>')
b.append(f'<line x1="{X(st["L"][0])}" y1="{Y(st["L"][1])}" x2="{X(st["R"][0])}" y2="{Y(st["R"][1])}" stroke="{C["eq"]}" stroke-dasharray="5 3"/>')
b.append(f'<circle cx="{X(lp[0])}" cy="{Y(lp[1])}" r="6" fill="#000"/><text x="{X(lp[0])+10}" y="{Y(lp[1])+18}" font-size="10">LP (ears 1.20 m)</text>')
b.append(f'<text x="{X(AX)}" y="{Y(lp[1])+36}" font-size="10" text-anchor="middle" fill="{C["eq"]}">RL 901K: 2.80 m apart | +/-30 deg | 2.80 m to ears | toe-in 30 deg</text>')
for k, v in MG["immersive_7_1_4"].items():
    if not isinstance(v, list): continue
    x, y, z = v
    filled = z < 2
    b.append(f'<circle cx="{X(x)}" cy="{Y(y)}" r="7" fill="{C["imm"] if filled else "#fff"}" stroke="{C["imm"]}" stroke-width="2"/>')
    b.append(f'<text x="{X(x)+9}" y="{Y(y)-6}" font-size="9" fill="{C["imm"]}">{k}{"" if filled else " (overhead 3.18)"}</text>')
b.append(f'<line x1="{X(AX-CIN["screen_width"]/2)}" y1="{Y(CIN["screen_y"])}" x2="{X(AX+CIN["screen_width"]/2)}" y2="{Y(CIN["screen_y"])}" stroke="#777" stroke-width="3" stroke-dasharray="2 2"/>')
b.append(f'<text x="{X(AX+1.6)}" y="{Y(CIN["screen_y"])+12}" font-size="9" fill="#555">AT screen 3.0 m (drops for film nights)</text>')
# dims
def dimv(x, y0, y1, label):
    b.append(f'<line x1="{X(x)}" y1="{Y(y0)}" x2="{X(x)}" y2="{Y(y1)}" stroke="#333"/><line x1="{X(x)-4}" y1="{Y(y0)}" x2="{X(x)+4}" y2="{Y(y0)}" stroke="#333"/><line x1="{X(x)-4}" y1="{Y(y1)}" x2="{X(x)+4}" y2="{Y(y1)}" stroke="#333"/><text x="{X(x)+5}" y="{(Y(y0)+Y(y1))/2}" font-size="10">{label}</text>')
dimv(AX + 3.05, 0, lp[1], f"{lp[1]:.2f} (0.375 L from rear)"); dimv(AX + 2.0, st["L"][1], D, f"{D - st['L'][1]:.2f}")
dimv(-0.45, 0, D, "8.20")
b.append(f'<text x="{X(W/2)}" y="{Y(D)-10}" font-size="11" text-anchor="middle">FRONT: partition (doorway kept, opens into the fireside lounge)</text>')
b.append(f'<text x="{X(W/2)}" y="{Y(0)+22}" font-size="11" text-anchor="middle">REAR: gable: entry door, clerestory, 2 windows (all kept; blackout for daytime films)</text>')
b.append(f'<text x="{X(W/2)}" y="{Y(0)+38}" font-size="10" text-anchor="middle" fill="#777">W 11.24  |  posts ■  |  beam lines dashed  |  flat ceiling (4.11 m) dotted  |  building axis dash-dot</text>')
open(os.path.join(OUT, "PR-102_control_room_plan.svg"), "w").write(frame(int(X(W + 1.0)) + 200, int(Y(-0.9)) + 100, "\n".join(b),
    "PR-102  CONTROL ROOM: FIRESIDE + CINEMA LAYOUT v0.4 (facing the partition; console and speakers pulled into the room)",
    "Actual Spectra Sonics (tape 62.4 x 47 in) and both actual Geithain RL 901K (tape 19.7 x 16.7 x 21.4 in, top at 61 in). Geometry from model/monitoring_geometry.json."))
print("wrote PR-101, PR-102")
