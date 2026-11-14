"""v0.5 screening acoustics: room modes + coupling, SBIR, decay-time RANGES (not predictions).

    python3 acoustics/modes_rt.py  ->  acoustics/out/modes_sbir_rt.json, acoustics/out/ANALYSIS_TABLES.md

Honesty rules (owner brief + inventory handoff):
  * No absorption coefficient is assigned to any individual Clark asset. Decay estimates use
    GENERIC MATERIAL-CLASS RANGES (low/high bounds typical of the class in general literature), applied to the
    measured AREAS of the allocated assets. They bound the answer; they are not data for these panels.
  * Rectangular-room mode maths on an asymmetric tray room is an approximation; height modes are bracketed
    by the low-zone and flat-ceiling heights. Measurement (sweeps at the LP) supersedes all of this.
"""
import itertools, json, math, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from geometry import G, W, D, AX, EAR, SPK, C_SOUND, P
OUT = os.path.join(HERE, "out")
PLC = json.load(open(os.path.join(OUT, "placements.json")))
B = json.load(open(os.path.join(ROOT, "model/scan_building_measurements.json")))
BANDS = [63, 125, 250, 500, 1000, 2000, 4000]

def poly_area(pts):
    return 0.5 * abs(sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1])))
def poly_perim(pts, skip_floor=True):
    return sum(math.dist(a, b) for a, b in zip(pts, pts[1:] + pts[:1]))

# ------------------------------------------------------------------ control room volume/surfaces (measured section)
sec = G["section"]; A_sec = poly_area(sec); V = A_sec * D; H_EFF = V / (W * D)
ceil_len = sum(math.dist(a, b) for a, b in zip(G["ceil"], G["ceil"][1:]))
S_floor = W * D; S_ceil = ceil_len * D; S_walls_side = (G["hloL"] + G["hloR"]) * D; S_ends = 2 * A_sec
S_total = S_floor + S_ceil + S_walls_side + S_ends
op = {"glass": 0.0, "door": 0.0}
win = [(1.15, 4.35), (4.50, 7.95), (1.95, 2.90), (4.45, 8.05)]
op["glass"] += sum(b - a for a, b in win) * (P["CR1.wh"] - P["CR1.wsill"])
op["glass"] += abs(P["CR3.xw2"] - P["CR3.xw1"]) * (P["CR3.hwt"] - P["CR3.hwb"])
op["glass"] += abs(P["CR3.gw1b"] - P["CR3.gw1a"]) * (P["CR3.gw1h"] - P["CR3.gw1s"]) + abs(P["CR3.gw2b"] - P["CR3.gw2a"]) * (P["CR3.gw2h"] - P["CR3.gw2s"])
op["door"] = abs(P["CR3.xe2"] - P["CR3.xe1"]) * P["CR3.he"]   # entry door only: the g_xi rectangle is an electrical cabinet (owner, 14 Nov), counted as wall
op["doorway_open"] = (P["CR1.xd2"] - P["CR1.xd1"]) * P["CR1.hd"]

# ------------------------------------------------------------------ modes (rectangular approximation, bracketed heights)
def modes(Lx, Ly, Lz, fmax=125):
    out = []
    for n, m_, l in itertools.product(range(0, 9), range(0, 7), range(0, 4)):
        if n == m_ == l == 0: continue
        f = C_SOUND / 2 * math.sqrt((n / Lx) ** 2 + (m_ / Ly) ** 2 + (l / Lz) ** 2)
        if f <= fmax:
            kind = ("axial", "tangential", "oblique")[sum(1 for q in (n, m_, l) if q) - 1]
            out.append((round(f, 1), (n, m_, l), kind))
    return sorted(out)
def coupling(nml, p, Lz):
    n, m_, l = nml
    return abs(math.cos(n * math.pi * p[0] / W) * math.cos(m_ * math.pi * p[1] / D) * math.cos(l * math.pi * p[2] / Lz))
MODES = []
for f, nml, kind in modes(W, D, H_EFF):
    lp = coupling(nml, EAR, H_EFF); sl = coupling(nml, SPK["L"], H_EFF); sr = coupling(nml, SPK["R"], H_EFF)
    MODES.append({"f": f, "nml": nml, "kind": kind, "LP": round(lp, 2), "spkL": round(sl, 2), "spkR": round(sr, 2),
                  "risk": "peak at LP (driven + heard)" if lp > 0.7 and max(sl, sr) > 0.7 else ("null at LP" if lp < 0.2 and max(sl, sr) > 0.5 else "")})
height_axial = {"flat 4.11 m": [round(C_SOUND / 2 * k / G["hc"], 1) for k in (1, 2, 3)],
                "effective %.2f m" % H_EFF: [round(C_SOUND / 2 * k / H_EFF, 1) for k in (1, 2, 3)],
                "low zone %.2f m" % G["hloL"]: [round(C_SOUND / 2 * k / G["hloL"], 1) for k in (1, 2)]}

# ------------------------------------------------------------------ SBIR (omni quarter-wave first notch; RL 901K is cardioid at LF)
SB = {}
for s, p in SPK.items():
    xc = p[0]; z_ceiling = G["hc"] if G["xc1"] <= xc <= G["xc2"] else None
    d = {"front wall (behind)": D - p[1], "floor": p[2], "near side wall": min(xc, W - xc), "ceiling above": (z_ceiling or 3.5) - p[2]}
    SB[s] = {k: {"d_m": round(v, 2), "first_notch_Hz": round(C_SOUND / (4 * v), 1)} for k, v in d.items()}

# ------------------------------------------------------------------ generic material classes (LOW, HIGH) per band 63..4k
# Typical-of-class bounds for screening only. NOT measured, NOT the Clark assets' data.
CLASS = {
 "hard_existing":   ([0.05, 0.05, 0.04, 0.04, 0.04, 0.04, 0.04], [0.20, 0.25, 0.15, 0.10, 0.08, 0.08, 0.08]),  # board/plaster/wood lining on framing (unknown)
 "oak_floor":       ([0.10, 0.08, 0.06, 0.05, 0.05, 0.05, 0.05], [0.20, 0.15, 0.10, 0.10, 0.10, 0.10, 0.10]),
 "concrete":        ([0.01, 0.01, 0.01, 0.02, 0.02, 0.02, 0.02], [0.02, 0.02, 0.03, 0.03, 0.04, 0.05, 0.05]),
 "glass":           ([0.10, 0.10, 0.06, 0.04, 0.03, 0.02, 0.02], [0.35, 0.35, 0.25, 0.18, 0.12, 0.07, 0.04]),
 "porous_thin":     ([0.02, 0.05, 0.20, 0.50, 0.75, 0.80, 0.80], [0.10, 0.20, 0.50, 0.90, 1.00, 1.00, 1.00]),  # <= 50 mm
 "porous_75_125":   ([0.05, 0.20, 0.55, 0.85, 0.90, 0.90, 0.85], [0.25, 0.50, 0.95, 1.00, 1.00, 1.00, 1.00]),  # 75-125 mm, with/without small gap
 "porous_deep":     ([0.30, 0.55, 0.85, 0.95, 0.95, 0.95, 0.90], [0.70, 0.95, 1.00, 1.00, 1.00, 1.00, 1.00]),  # >= 300 mm deep (new LF traps)
 "foam_tapered":    ([0.05, 0.15, 0.40, 0.70, 0.80, 0.85, 0.85], [0.30, 0.55, 0.90, 1.00, 1.00, 1.00, 1.00]),
 "diffuser_wood":   ([0.05, 0.08, 0.10, 0.10, 0.10, 0.10, 0.10], [0.20, 0.30, 0.40, 0.40, 0.40, 0.35, 0.30]),
 "perf_wood_panel": ([0.05, 0.15, 0.30, 0.40, 0.30, 0.20, 0.15], [0.25, 0.50, 0.80, 0.80, 0.70, 0.60, 0.50]),
 "hybrid_barrel":   ([0.05, 0.15, 0.35, 0.50, 0.45, 0.35, 0.30], [0.30, 0.60, 0.90, 0.90, 0.85, 0.75, 0.65]),
 "open_box_wood":   ([0.02, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05], [0.20, 0.25, 0.20, 0.15, 0.12, 0.10, 0.10]),
 "heavy_curtain":   ([0.03, 0.05, 0.25, 0.50, 0.60, 0.60, 0.55], [0.10, 0.20, 0.50, 0.80, 0.90, 0.90, 0.90]),
 "upholstery_furn": ([0.10, 0.20, 0.30, 0.40, 0.45, 0.45, 0.45], [0.30, 0.45, 0.65, 0.80, 0.85, 0.85, 0.85]),  # m² per sofa/chair face
 "rug":             ([0.01, 0.02, 0.06, 0.15, 0.30, 0.45, 0.55], [0.05, 0.08, 0.20, 0.40, 0.60, 0.70, 0.75]),
 "open_doorway":    ([1.0] * 7, [1.0] * 7),
}
def asset_class(p):
    a = p["asset"]
    if a.startswith("BTR"): return "foam_tapered"
    if a.startswith("DIF"): return "diffuser_wood"
    if a.startswith("HYB"): return "hybrid_barrel"
    if a.startswith("PRF"): return "perf_wood_panel"
    if a.startswith("WOOD"): return "open_box_wood"
    t = min(p["size"]); return "porous_75_125" if t >= 0.07 else "porous_thin"
def face_area(p):
    s = sorted(p["size"]); return s[1] * s[2]

def decay(V_, S_, items):
    lo, hi = np.zeros(7), np.zeros(7)
    A_lo, A_hi = np.zeros(7), np.zeros(7)
    for area, cls in items:
        a_lo, a_hi = np.array(CLASS[cls][0]), np.array(CLASS[cls][1])
        A_lo += area * a_lo; A_hi += area * a_hi
    m_air = np.array([0, 0, 0, 0.0006, 0.001, 0.0024, 0.006])   # air absorption (4m), ~20 °C, 50 % RH
    out = {}
    for name, A in (("low_absorption", A_lo), ("high_absorption", A_hi)):
        abar = np.clip(A / S_, 0, 0.99)
        sab = 0.161 * V_ / (A + 4 * m_air * V_); ey = 0.161 * V_ / (-S_ * np.log(1 - abar) + 4 * m_air * V_)
        out[name] = {"A_m2": A.round(1).tolist(), "alpha_mean": abar.round(3).tolist(), "T_sabine": sab.round(2).tolist(), "T_eyring": ey.round(2).tolist()}
    # decay range: longest = Sabine with low absorption; shortest = Eyring with high absorption
    out["T_range_s"] = [[round(float(out["high_absorption"]["T_eyring"][i]), 2), round(float(out["low_absorption"]["T_sabine"][i]), 2)] for i in range(7)]
    return out

S_glass, S_door, S_dw = op["glass"], op["door"], op["doorway_open"]
S_hard = S_total - S_floor - S_glass - S_door - S_dw
base_cr = [(S_floor, "oak_floor"), (S_glass, "glass"), (S_door, "hard_existing"), (S_dw, "open_doorway"), (S_hard, "hard_existing")]
furn_cr = [(3.0, "upholstery_furn"), (2.0, "upholstery_furn"), (12.0, "rug")]   # sofa + 2 armchairs + lounge seats; mix + lounge rugs
cr_assets = [p for p in PLC["placements"] if p["room"] == "Control room"]
cr_treat = [(face_area(p), asset_class(p)) for p in cr_assets]
new_cr = [(5.85 * 1.10 + 5.85 * 0.75, "porous_deep"), (5.85 * 1.10 + 5.85 * 0.75, "porous_deep"),   # two bench traps: face + top
          (2 * 0.99 * 2.2, "porous_deep"),                                                         # two corner traps (0.70 m legs -> 0.99 m face)
          (1.3 * 2.2, "heavy_curtain")]
def covered(items): return sum(a for a, _ in items)
front_ids = {"ABS-003", "PAN-001"}
cr_treat_deep = [(face_area(p), "porous_deep" if p["asset"] in front_ids else asset_class(p)) for p in cr_assets]   # NEW-07 stand-off frames
CASES = {
 "CR bare shell (furnished, no treatment)": base_cr + furn_cr,
 "CR v0.5 Clark reuse only": base_cr + furn_cr + cr_treat,
 "CR v0.5 Clark reuse + NEW LF traps/curtain": base_cr + furn_cr + cr_treat + new_cr,
 "CR v0.5 recommended (above + NEW-07 200 mm wool behind front panels)": base_cr + furn_cr + cr_treat_deep + new_cr,
}
RT = {k: decay(V, S_total, v) for k, v in CASES.items()}
T_EBU = 0.25 * (V / 100) ** (1 / 3)

# ------------------------------------------------------------------ live room (tray zone + under-loft as one coupled volume)
F = B["live_floor"]; LL, LR = AX - 6.15, AX + 5.75
lsec = [(LL, F), (LR, F), (LR, B["live_low_ceiling_right"]), (AX + 2.75, B["live_low_ceiling_right"]), (AX + 2.75, 2.31),
        (AX + 1.75, B["live_flat_ceiling"]), (AX - 1.75, B["live_flat_ceiling"]), (AX - 3.45, 2.20), (AX - 3.45, B["live_low_ceiling_left"]), (LL, B["live_low_ceiling_left"])]
Y_MID1, Y_LOFT_END, Y_LG = 16.185, 22.885, B["live_gable_y"] + 15.185
L_tray, L_ul = Y_LG - Y_LOFT_END, Y_LOFT_END - Y_MID1
wid = LR - LL; h_ul = B["underloft_ceiling"] - F
V_live = poly_area(lsec) * L_tray + wid * h_ul * L_ul
S_l_floor = wid * (L_tray + L_ul)
S_l_ceil = (poly_perim(lsec) - wid - (B["live_low_ceiling_left"] - F) - (B["live_low_ceiling_right"] - F)) * L_tray + wid * L_ul
S_l_walls = 2 * (B["live_low_ceiling_left"] - F) * L_tray + 2 * h_ul * L_ul + poly_area(lsec) * 2 * 0.6   # sides + ends (partly open to middle zone)
S_l_glass = 8 * 1.4 * 0.7; S_l_garage = 3.70 * 3.40
S_l = S_l_floor + S_l_ceil + S_l_walls
lv = [p for p in PLC["placements"] if p["room"] == "Live room"]
fixed = [(face_area(p), asset_class(p)) for p in lv if not p["shape"].startswith("gobo")]
gobos = [(2 * face_area(p), "porous_75_125" if p["asset"] == "GOB-001" else "perf_wood_panel") for p in lv if p["shape"].startswith("gobo")]
hyb = [x for x in fixed if x[1] == "hybrid_barrel"]; nonhyb = [x for x in fixed if x[1] != "hybrid_barrel"]
base_lv = [(S_l_floor, "concrete"), (S_l_glass, "glass"), (S_l_garage, "hard_existing"), (S_l_ceil + S_l_walls - S_l_glass - S_l_garage, "hard_existing"),
           (6.0, "upholstery_furn")]   # piano + people (rough)
LIVE_CASES = {
 "LIVE bright (piano/chamber: gobos parked in the bays, HYBs raised)": base_lv + nonhyb + [(a * 0.35, c) for a, c in gobos],
 "LIVE neutral (ensemble config as modelled)": base_lv + fixed + gobos,
 "LIVE dead (band: gobos + GOB-002 + NEW curtains 2 x 3 x 6 m on the tray side walls)": base_lv + fixed + gobos + [(36.0, "heavy_curtain")],
}
RT_LIVE = {k: decay(V_live, S_l, v) for k, v in LIVE_CASES.items()}

f_s = 2000 * math.sqrt(0.3 / V)
res = {"control_room": {"volume_m3": round(V, 1), "section_area_m2": round(A_sec, 2), "h_eff_m": round(H_EFF, 3), "surface_m2": round(S_total, 1),
                        "glass_m2": round(S_glass, 1), "doors_m2": round(S_door, 1), "schroeder_Hz_at_0.3s": round(f_s, 0),
                        "EBU3276_target_Tm_s": round(T_EBU, 2), "EBU_tolerance": "±0.05 s 200 Hz–4 kHz; up to +0.3 s allowed at 63 Hz (sloping limit)",
                        "treated_area_clark_m2": round(covered(cr_treat), 1), "treated_area_new_m2": round(covered(new_cr), 1)},
       "modes": MODES, "height_axial_Hz": height_axial, "sbir": SB, "rt_bands_Hz": BANDS, "rt_control_room": RT,
       "live_room": {"volume_m3": round(V_live, 0), "surface_m2": round(S_l, 0)}, "rt_live_room": RT_LIVE,
       "classes": CLASS, "notes": __doc__}
json.dump(res, open(os.path.join(OUT, "modes_sbir_rt.json"), "w"), indent=1, default=lambda o: list(o) if isinstance(o, tuple) else str(o))

# ------------------------------------------------------------------ human-readable tables
L_ = []
L_.append(f"## Control room\nVolume **{V:.0f} m³** (measured section {A_sec:.1f} m² × {D:.2f} m); effective height {H_EFF:.2f} m; "
          f"surface {S_total:.0f} m² (glass {S_glass:.1f} m²). Schroeder frequency ≈ {f_s:.0f} Hz at T = 0.3 s. "
          f"EBU Tech 3276 target T_m = 0.25·(V/100 m³)^⅓ = **{T_EBU:.2f} s**.\n")
L_.append("### Axial modes and coupling at the listening position (rectangular approximation)\n| f (Hz) | (n,m,l) | LP | L spk | R spk | Note |\n|---|---|---|---|---|---|")
for md in MODES:
    if md["kind"] == "axial" and md["f"] <= 100:
        L_.append(f"| {md['f']} | {md['nml']} | {md['LP']} | {md['spkL']} | {md['spkR']} | {md['risk']} |")
L_.append(f"\nHeight axial modes are bracketed: {height_axial}. The tray ceiling spreads them, so treat the vertical series as a band, not lines.\n")
risky = [md for md in MODES if md["risk"]]
L_.append("### Modes (all kinds, ≤125 Hz) flagged at the LP\n| f | (n,m,l) | kind | LP | L | R | risk |\n|---|---|---|---|---|---|---|")
for md in risky[:40]:
    L_.append(f"| {md['f']} | {md['nml']} | {md['kind']} | {md['LP']} | {md['spkL']} | {md['spkR']} | {md['risk']} |")
L_.append("\n### SBIR (omni quarter-wave first notch; the RL 901K's cardioid bass reduces the rear/side terms)\n| Speaker | Boundary | Distance (m) | First notch (Hz) |\n|---|---|---|---|")
for s, d in SB.items():
    for k, v in d.items(): L_.append(f"| {s} | {k} | {v['d_m']} | {v['first_notch_Hz']} |")
def rt_table(RTD, title):
    L_.append(f"\n### {title}\nDecay-time RANGE (s): shortest = Eyring with the class HIGH bounds; longest = Sabine with the class LOW bounds.\n")
    L_.append("| Case | " + " | ".join(f"{b} Hz" for b in BANDS) + " |\n|---|" + "---|" * len(BANDS))
    for k, v in RTD.items():
        L_.append(f"| {k} | " + " | ".join(f"{a:.2f}–{b:.2f}" for a, b in v["T_range_s"]) + " |")
rt_table(RT, "Control-room decay ranges (generic material classes on measured areas)")
L_.append(f"\nTarget for mixing: **{T_EBU:.2f} ± 0.05 s** from 200 Hz up (EBU 3276), flat or gently rising below. "
          f"Clark treatment area placed: {covered(cr_treat):.1f} m² + new LF traps/curtain {covered(new_cr):.1f} m².")
L_.append(f"\n## Live room\nVolume ≈ **{V_live:.0f} m³** (tray zone + under-loft, coupled; partly open to the middle zone), surface ≈ {S_l:.0f} m².")
rt_table(RT_LIVE, "Live-room decay ranges by configuration")
L_.append("\nDesign intent (not a standard): piano/strings ≈ 0.7–1.0 s mid-band; ensemble ≈ 0.5–0.7 s; band/drums ≈ 0.35–0.5 s. "
          "The ranges above show the configurations move the room in that direction; the actual values need an impulse-response measurement.")
open(os.path.join(OUT, "ANALYSIS_TABLES.md"), "w").write("\n".join(L_) + "\n")
print(f"V={V:.1f} m3 h_eff={H_EFF:.2f} S={S_total:.0f} glass={S_glass:.1f} T_EBU={T_EBU:.2f} fs={f_s:.0f} V_live={V_live:.0f}")
for k, v in {**RT, **RT_LIVE}.items(): print(k[:60].ljust(60), [f"{a:.2f}-{b:.2f}" for a, b in v["T_range_s"]])
for s, d in SB.items(): print(s, {k: v["first_notch_Hz"] for k, v in d.items()})
print("flagged modes:", [(m["f"], m["nml"], m["risk"]) for m in risky[:12]])
