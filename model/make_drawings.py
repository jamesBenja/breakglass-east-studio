"""Existing-conditions plan + two sections (SVG) generated from model/solve_result.json.

    python3 model/make_drawings.py   ->  drawings/EX-101_plan.svg, EX-201_section_AA.svg, EX-202_section_BB.svg

Same numbers as the Blender model (single source of truth). Every dimension prints its
1-sigma solve uncertainty and evidence class. NOT a measured survey. NOT for construction.
"""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
SOL = json.load(open(os.path.join(HERE, "solve_result.json")))
P = {k: v["value"] for k, v in SOL["params"].items()}; S = {k: v["sigma"] for k, v in SOL["params"].items()}
OUT = os.path.join(ROOT, "drawings"); os.makedirs(OUT, exist_ok=True)
W, D = P["W"], P["D"]; ds, hlo, hbb, hb, hc, wc = (P[k] for k in ("ds", "hlo", "hbb", "hb", "hc", "wc"))
xc1, xc2 = W/2 - wc/2, W/2 + wc/2
SC = 60  # px per metre (1:~50 at 96dpi is not implied; drawing is diagrammatic-to-scale)
COL = {"SOLVED": "#1f6f8b", "SCAN": "#5a6b85", "INFERRED": "#c98a1b", "UNKNOWN": "#c2187a"}

def svg(w, h, body, title):
    w = max(w, 1330)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" font-family="Helvetica,Arial,sans-serif">
<rect width="{w}" height="{h}" fill="#fbfaf7"/>
{body}
<g font-size="11" fill="#333">
<text x="20" y="{h-58}" font-size="15" font-weight="bold">{title}</text>
<text x="20" y="{h-40}">BREAKGLASS EAST / Ways Mills - EXISTING CONDITIONS v0.1 - photo-constrained reconstruction from 3 camera matches; scale from scan labels only.</text>
<text x="20" y="{h-24}">NOT A MEASURED SURVEY. NOT FOR CONSTRUCTION, PRICING OR PERMIT. Dimensions: value +/- 1-sigma solve uncertainty (metres). Interior faces; wall thickness unknown.</text>
<text x="20" y="{h-8}"><tspan fill="{COL['SOLVED']}">&#9632; PHOTO-SOLVED</tspan>   <tspan fill="{COL['SCAN']}">&#9632; SCAN-LABELLED</tspan>   <tspan fill="{COL['INFERRED']}">&#9632; PHOTO-INFERRED</tspan>   <tspan fill="{COL['UNKNOWN']}">&#9632; UNKNOWN / NOT YET OBSERVED</tspan>   Source: model/solve_result.json</text>
</g></svg>'''

def dim(x1, y1, x2, y2, text, color, off=0, vertical=False):
    if vertical:
        x = x1 + off
        return (f'<line x1="{x}" y1="{y1}" x2="{x}" y2="{y2}" stroke="{color}" stroke-width="1"/>'
                f'<line x1="{x-5}" y1="{y1}" x2="{x+5}" y2="{y1}" stroke="{color}"/><line x1="{x-5}" y1="{y2}" x2="{x+5}" y2="{y2}" stroke="{color}"/>'
                f'<text x="{x+6}" y="{(y1+y2)/2}" font-size="11" fill="{color}">{text}</text>')
    y = y1 + off
    return (f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{color}" stroke-width="1"/>'
            f'<line x1="{x1}" y1="{y-5}" x2="{x1}" y2="{y+5}" stroke="{color}"/><line x1="{x2}" y1="{y-5}" x2="{x2}" y2="{y+5}" stroke="{color}"/>'
            f'<text x="{(x1+x2)/2}" y="{y-4}" font-size="11" text-anchor="middle" fill="{color}">{text}</text>')

def pm(k): return f"{P[k]:.2f} &#177;{S[k]:.2f}"

# ------------------------------------------------------------------ plan
ox, oy = 250, 90
X = lambda x: ox + x*SC
Y = lambda y: oy + (D - y)*SC          # +Y (towards live room) drawn UP
b = []
b.append(f'<rect x="{X(0)}" y="{Y(D)}" width="{W*SC}" height="{D*SC}" fill="none" stroke="{COL["SCAN"]}" stroke-width="4"/>')
for x in (ds, W-ds):
    b.append(f'<line x1="{X(x)}" y1="{Y(0)}" x2="{X(x)}" y2="{Y(D)}" stroke="{COL["SOLVED"]}" stroke-dasharray="8 5" stroke-width="2"/>')
for x in (xc1, xc2):
    b.append(f'<line x1="{X(x)}" y1="{Y(0)}" x2="{X(x)}" y2="{Y(D)}" stroke="{COL["SOLVED"]}" stroke-dasharray="2 4" stroke-width="1.5"/>')
for x, k in ((ds, "ypl"), (W-ds, "ypr")):
    b.append(f'<rect x="{X(x)-5}" y="{Y(P[k])-5}" width="10" height="10" fill="{COL["SOLVED"]}"/>')
    b.append(f'<ellipse cx="{X(x)}" cy="{Y(P[k])}" rx="{max(S["ds"]*SC,4)}" ry="{S[k]*SC}" fill="none" stroke="{COL["SOLVED"]}" stroke-width="0.8"/>')
def gap(x0, x1, y, color, label):
    b.append(f'<line x1="{X(x0)}" y1="{Y(y)}" x2="{X(x1)}" y2="{Y(y)}" stroke="#fbfaf7" stroke-width="6"/>')
    b.append(f'<line x1="{X(x0)}" y1="{Y(y)}" x2="{X(x1)}" y2="{Y(y)}" stroke="{color}" stroke-width="2"/>')
    b.append(f'<text x="{X((x0+x1)/2)}" y="{Y(y)+(18 if y==0 else -8)}" font-size="10" text-anchor="middle" fill="{color}">{label}</text>')
gap(P["CR3.xe2"], P["CR3.xe1"], 0, COL["SOLVED"], "EXT. ENTRY DOOR")
gap(P["g_xi2"], P["g_xi1"], 0, COL["SOLVED"], "DOOR (leads to ? UNKNOWN)")
gap(P["CR1.xd1"], P["CR1.xd2"], D, COL["SOLVED"], "DOORWAY TO INTERMEDIATE ZONE")
ya, yb = sorted((P["CR1.wy1"], P["CR1.wy2"]))
b.append(f'<line x1="{X(W)}" y1="{Y(yb)}" x2="{X(W)}" y2="{Y(ya)}" stroke="{COL["SOLVED"]}" stroke-width="7"/>')
b.append(f'<line x1="{X(W)}" y1="{Y(ya)}" x2="{X(W)}" y2="{Y(0.3)}" stroke="{COL["UNKNOWN"]}" stroke-width="3" stroke-dasharray="4 4"/>')
b.append(f'<text x="{X(W)+10}" y="{Y((ya+yb)/2)}" font-size="10" fill="{COL["SOLVED"]}">LONG WINDOW (far end solved)</text>')
b.append(f'<text x="{X(W)+10}" y="{Y(ya/2)}" font-size="10" fill="{COL["UNKNOWN"]}">window continues - extent UNKNOWN</text>')
b.append(f'<text x="{X(-0.2)}" y="{Y(D/2)}" font-size="10" fill="{COL["UNKNOWN"]}" text-anchor="end">X=0 wall windows</text>')
b.append(f'<text x="{X(-0.2)}" y="{Y(D/2)+13}" font-size="10" fill="{COL["UNKNOWN"]}" text-anchor="end">seen, NOT solved</text>')
b.append(f'<text x="{X(W/2)}" y="{Y(D/2)}" font-size="16" text-anchor="middle" fill="#555">CONTROL ROOM (existing)</text>')
b.append(f'<text x="{X(W/2)}" y="{Y(D/2)+18}" font-size="11" text-anchor="middle" fill="#777">area {W*D:.1f} m2 (scan-label rectangle {10.51*7.86:.1f} m2)</text>')
b.append(f'<text x="{X(W/2)}" y="{Y(D)-28}" font-size="11" text-anchor="middle" fill="#777">&#8593; +Y  intermediate zone / live room beyond (NOT MODELLED)</text>')
b.append(f'<text x="{X(W/2)}" y="{Y(0)+50}" font-size="11" text-anchor="middle" fill="#777">gable end / building entry. Origin (0,0) at lower-left interior corner. A-A and B-B: section cuts.</text>')
b.append(dim(X(0), Y(D), X(W), Y(D), f"W {pm('W')}  (scan labels 10.51 / 10.38)", COL["SCAN"], -45))
b.append(dim(X(0), Y(0), X(0), Y(D), "", COL["SCAN"], -130, vertical=True))
b.append(f'<text x="{X(0)-136}" y="{Y(D/2)-30}" font-size="11" text-anchor="end" fill="{COL["SCAN"]}">D {pm("D")}</text><text x="{X(0)-136}" y="{Y(D/2)-16}" font-size="11" text-anchor="end" fill="{COL["SCAN"]}">(label 7.86)</text>')
b.append(dim(X(0), Y(D), X(ds), Y(D), f"{pm('ds')}", COL["SOLVED"], -15))
b.append(dim(X(xc1), Y(D), X(xc2), Y(D), f"flat clg {pm('wc')}", COL["SOLVED"], -15))
b.append(dim(X(W-ds), Y(0), X(W-ds), Y(P["ypr"]), f"post Y {pm('ypr')}", COL["SOLVED"], 18, vertical=True))
b.append(f'<line x1="{X(-0.6)}" y1="{Y(D*0.55)}" x2="{X(W+0.6)}" y2="{Y(D*0.55)}" stroke="#999" stroke-dasharray="14 4 2 4"/><text x="{X(W+0.7)}" y="{Y(D*0.55)+4}" font-size="13" font-weight="bold">A</text>')
b.append(f'<line x1="{X(W*0.62)}" y1="{Y(-0.6)}" x2="{X(W*0.62)}" y2="{Y(D+0.4)}" stroke="#999" stroke-dasharray="14 4 2 4"/><text x="{X(W*0.62)+4}" y="{Y(-0.7)}" font-size="13" font-weight="bold">B</text>')
open(os.path.join(OUT, "EX-101_plan.svg"), "w").write(svg(int(X(W)+280), int(Y(0)+150), "\n".join(b), "EX-101  CONTROL ROOM - EXISTING PLAN (photo-constrained)"))

# ------------------------------------------------------------------ section A-A (transverse, looking +Y)
ox, oy = 110, 70; Z = lambda z: oy + (hc + 0.5 - z)*SC; X = lambda x: ox + x*SC
sec = [(0,0),(W,0),(W,hlo),(W-ds,hlo),(W-ds,hb),(xc2,hc),(xc1,hc),(ds,hb),(ds,hlo),(0,hlo)]
b = [f'<polygon points="{" ".join(f"{X(x)},{Z(z)}" for x, z in sec)}" fill="#efece6" stroke="{COL["SOLVED"]}" stroke-width="3"/>']
for x in (ds, W-ds):
    b.append(f'<rect x="{X(x)-6}" y="{Z(hlo)}" width="12" height="{(hlo-hbb)*SC}" fill="{COL["SOLVED"]}"/>')
    b.append(f'<rect x="{X(x)-4}" y="{Z(hbb)}" width="8" height="{hbb*SC}" fill="{COL["SOLVED"]}" opacity="0.55"/>')
b.append(f'<line x1="{X(0)}" y1="{Z(0)}" x2="{X(W)}" y2="{Z(0)}" stroke="{COL["SCAN"]}" stroke-width="4"/>')
b.append(f'<text x="{X(W/2)}" y="{Z(hc+0.42)}" font-size="11" text-anchor="middle" fill="{COL["UNKNOWN"]}">ROOF STRUCTURE, PITCH AND ANY VOID ABOVE THE FINISHED CEILING: NOT OBSERVED - NOT DRAWN</text>')
b.append(dim(X(0), Z(0), X(0), Z(hlo), f"{pm('hlo')}", COL["SOLVED"], -60, vertical=True))
b.append(dim(X(ds), Z(0), X(ds), Z(hbb), f"{pm('hbb')} u/s beam", COL["SOLVED"], 30, vertical=True))
b.append(dim(X(W-ds), Z(0), X(W-ds), Z(hb), f"{pm('hb')} slope foot", COL["SOLVED"], -12, vertical=True).replace('font-size="11" fill', 'font-size="11" text-anchor="end" fill').replace(f'x="{X(W-ds)-12+6}"', f'x="{X(W-ds)-16}"'))
b.append(dim(X(W/2), Z(0), X(W/2), Z(hc), f"{pm('hc')} (scan label 4.07)", COL["SOLVED"], 0, vertical=True))
b.append(dim(X(xc1), Z(hc), X(xc2), Z(hc), f"{pm('wc')}", COL["SOLVED"], -14))
b.append(dim(X(0), Z(0), X(W), Z(0), f"W {pm('W')}", COL["SCAN"], 30))
b.append(f'<text x="{X(ds)+10}" y="{Z(0.4)}" font-size="10" fill="#555">post</text><text x="{X(W-ds)-34}" y="{Z(0.4)}" font-size="10" fill="#555">post</text>')
b.append(f'<text x="{X(0.15)}" y="{Z(hlo)-8}" font-size="10" fill="#555">low side zone</text>')
open(os.path.join(OUT, "EX-201_section_AA.svg"), "w").write(svg(int(X(W)+330), int(Z(0)+150), "\n".join(b), "EX-201  SECTION A-A (transverse, looking toward partition)"))

# ------------------------------------------------------------------ section B-B (longitudinal at x=0.62W, looking -X)
x_cut = W*0.62; z_at = hb + (hc-hb)*min(1, max(0, (W-ds-x_cut)/(W-ds-xc2))) if x_cut > xc2 else hc
ox = 110; Yh = lambda y: ox + y*SC
b = [f'<rect x="{Yh(0)}" y="{Z(z_at)}" width="{D*SC}" height="{z_at*SC}" fill="#efece6" stroke="{COL["SOLVED"]}" stroke-width="3"/>']
b.append(f'<line x1="{Yh(0)}" y1="{Z(hc)}" x2="{Yh(D)}" y2="{Z(hc)}" stroke="{COL["SOLVED"]}" stroke-dasharray="3 4"/>')
b.append(f'<text x="{Yh(D/2)}" y="{Z(hc)-6}" font-size="10" text-anchor="middle" fill="{COL["SOLVED"]}">flat ceiling beyond {pm("hc")}</text>')
b.append(f'<line x1="{Yh(0)}" y1="{Z(hbb)}" x2="{Yh(D)}" y2="{Z(hbb)}" stroke="{COL["SOLVED"]}" stroke-dasharray="10 4"/>')
b.append(f'<text x="{Yh(D/2)}" y="{Z(hbb)+14}" font-size="10" text-anchor="middle" fill="{COL["SOLVED"]}">u/s beam beyond {pm("hbb")} (beam bearing at end walls UNKNOWN)</text>')
b.append(f'<rect x="{Yh(P["ypr"])-4}" y="{Z(hbb)}" width="8" height="{hbb*SC}" fill="{COL["SOLVED"]}" opacity="0.55"/>')
for y0, y1, z0, z1, lab in ((P["CR3.xe2"]*0, 0, 0, 0, ""),):
    pass
b.append(f'<rect x="{Yh(D)-3}" y="{Z((P["CR1.hd"]))}" width="6" height="{P["CR1.hd"]*SC}" fill="{COL["SOLVED"]}"/>')
b.append(f'<text x="{Yh(D)-8}" y="{Z(P["CR1.hd"])-4}" font-size="10" text-anchor="end" fill="{COL["SOLVED"]}">doorway head {pm("CR1.hd")}</text>')
b.append(f'<rect x="{Yh(0)-3}" y="{Z(P["CR3.hwt"])}" width="6" height="{(P["CR3.hwt"]-P["CR3.hwb"])*SC}" fill="{COL["SOLVED"]}"/>')
b.append(f'<text x="{Yh(0)+8}" y="{Z(P["CR3.hwt"])+12}" font-size="10" fill="{COL["SOLVED"]}">gable clerestory {P["CR3.hwb"]:.2f}-{P["CR3.hwt"]:.2f}</text>')
b.append(dim(Yh(0), Z(0), Yh(D), Z(0), f"D {pm('D')}", COL["SCAN"], 30))
b.append(dim(Yh(0), Z(0), Yh(P["ypr"]), Z(0), f"post {pm('ypr')}", COL["SOLVED"], 75))
b.append(f'<text x="{Yh(0)}" y="{Z(-0.25)+40}" font-size="10" fill="#555">GABLE END (Y=0)</text><text x="{Yh(D)}" y="{Z(-0.25)+40}" font-size="10" text-anchor="end" fill="#555">PARTITION (Y=D) &#8594; intermediate zone</text>')
b.append(f'<line x1="{Yh(D)}" y1="{Z(0)}" x2="{Yh(D+1.2)}" y2="{Z(0)}" stroke="{COL["UNKNOWN"]}" stroke-dasharray="5 4"/><text x="{Yh(D+0.1)}" y="{Z(0.15)}" font-size="9" fill="{COL["UNKNOWN"]}">floor level beyond: UNKNOWN (tile seen in CR3)</text>')
open(os.path.join(OUT, "EX-202_section_BB.svg"), "w").write(svg(int(Yh(D)+220), int(Z(0)+150), "\n".join(b), f"EX-202  SECTION B-B (longitudinal at X={x_cut:.2f}, looking toward X=0)"))
print("wrote drawings/EX-101_plan.svg, EX-201_section_AA.svg, EX-202_section_BB.svg")
