"""Control-room monitoring geometry + basic acoustic screening (PROPOSED, for acoustician review).

    python3 model/monitoring_geometry.py -> model/monitoring_geometry.json

Inputs: solved/scanned shell (solve_result.json, scan measurements), owner tape measurements of the
actual equipment, and Geithain's published RL 901K data. Nothing here is a measured acoustic result:
mode lists use a rectangular-room approximation of a non-rectangular room, SBIR uses the omni
quarter-wave approximation (the RL 901K's cardioid LF reduces it). Orientation: listening axis on the
building axis X=xf, FACING THE PARTITION (+Y). See docs/CONTROL_ROOM_DESIGN.md for why.
"""
import json, math, os
HERE = os.path.dirname(os.path.abspath(__file__))
P = {k: v["value"] for k, v in json.load(open(os.path.join(HERE, "solve_result.json")))["params"].items()}
IN = 0.0254
W, D, hc, axis = P["W"], P["D"], P["hc"], P["xf"]
# --- actual equipment (owner tape 2026-11-08; RL 901K also manufacturer-published) ---
console = {"width": 62.4*IN, "depth": 47*IN, "h_front": 31*IN, "h_top": 41*IN}
rl901k = {"width": 19.7*IN, "depth": 16.7*IN, "height": 21.4*IN, "top_on_stand": 61*IN}
rl901k["bottom_on_stand"] = rl901k["top_on_stand"] - rl901k["height"]
rl901k["acoustic_centre_z"] = rl901k["bottom_on_stand"] + rl901k["height"]/2   # coaxial MF/HF at woofer centre: PHOTO-INFERRED
# --- stereo layout ---
EAR_Z = 1.20            # seated ear height (typical; confirm with owner's chair)
ANG = 30.0              # +/- degrees (ITU-R BS.775 / BS.2051 stereo)
DIST = 2.80             # ear to acoustic centre, inside the 2-4 m design range
half = DIST * math.sin(math.radians(ANG)); perp = DIST * math.cos(math.radians(ANG))
# LAYOUT (owner decision 8 Nov 2026): "fireside" = console + RL 901K pulled into the room, listening position at
# 0.375 L from the REAR (gable) wall; the existing wood stove stays and becomes a fireside lounge behind the speakers,
# and a drop-down AT screen serves family film nights from a rear sofa. "front_wall" = earlier v0.3 layout.
LAYOUT = os.environ.get("BG_LAYOUT", "fireside")
if LAYOUT == "fireside":
    lp_y = 0.375 * D
    y_spk = lp_y + perp
    BAFFLE_FROM_WALL = D - y_spk
else:
    BAFFLE_FROM_WALL = 0.65 # cabinet back 0.22 m from wall (> 0.20 m manufacturer minimum)
    y_spk = D - BAFFLE_FROM_WALL
lp = (axis, y_spk - perp, EAR_Z)
spk = {"L": (axis - half, y_spk, rl901k["acoustic_centre_z"]), "R": (axis + half, y_spk, rl901k["acoustic_centre_z"])}
toe_in = ANG
console_pos = {"front_edge_y": lp[1] + 0.38, "back_edge_y": lp[1] + 0.38 + console["depth"], "x0": axis - console["width"]/2, "x1": axis + console["width"]/2}
# sightline check: ear -> acoustic centre passes above the meter bridge at the console back edge?
t = (console_pos["back_edge_y"] - lp[1]) / (y_spk - lp[1]); z_line = EAR_Z + t * (spk["L"][2] - EAR_Z)
# --- 7.1.4 (Dolby Atmos music/home layout guidance; positions on a 2.8 m sphere where the room allows) ---
def pt(az, el, r=DIST):
    a, e = math.radians(az), math.radians(el)
    return [round(lp[0] + r*math.cos(e)*math.sin(a), 3), round(lp[1] + r*math.cos(e)*math.cos(a), 3), round(lp[2] + r*math.sin(e), 3)]
immersive = {"C": pt(0, 2), "Ls": pt(-95, 0), "Rs": pt(95, 0), "Lrs": pt(-140, 0), "Rrs": pt(140, 0),
             "Ltf": pt(-45, 45), "Rtf": pt(45, 45), "Ltr": pt(-135, 45), "Rtr": pt(135, 45)}
def ceiling_z(x):
    xL, xR = P["dsL"], W - P["dsR"]; xc1, xc2 = axis - P["wc"]/2, axis + P["wc"]/2
    if x <= xL or x >= xR: return 2.25
    if xc1 <= x <= xc2: return hc
    if x < xc1: return P["hbL"] + (hc - P["hbL"]) * (x - xL) / (xc1 - xL)
    return P["hbR"] + (hc - P["hbR"]) * (xR - x) / (xR - xc2)
for k in ("Ltf", "Rtf", "Ltr", "Rtr"):
    x, y, z = immersive[k]; cz = ceiling_z(x)
    immersive[k + "_ceiling_at_point"] = round(cz, 2)
    if z > cz - 0.25:   # cannot reach the sphere -> mount at ceiling (minus 0.25 m) and report actual elevation
        z2 = cz - 0.25; immersive[k][2] = round(z2, 3)
        r = math.dist(lp[:2], (x, y)); immersive[k + "_elev_deg"] = round(math.degrees(math.atan2(z2 - EAR_Z, r)), 1)
    else:
        immersive[k + "_elev_deg"] = 45.0
# --- acoustic screening ---
c = 343.0
h_eff = (P["hloR"] * (P["dsL"] + P["dsR"]) + hc * P["wc"] + 0.5*(hc + 2.45)*(W - P["dsL"] - P["dsR"] - P["wc"])) / W  # area-weighted
def axial(L): return [round(n*c/(2*L), 1) for n in range(1, 6)]
modes = {"length_Y_8.20": axial(D), "width_X_11.24": axial(W), "height_effective_%.2f" % h_eff: axial(h_eff)}
schroeder_note = "Room volume ~%.0f m3; modal region roughly below ~%.0f Hz (Schroeder estimate, RT 0.25 s assumed)" % (W*D*h_eff, 2000*math.sqrt(0.25/(W*D*h_eff)))
sbir = {"front_wall_distance_m": round(BAFFLE_FROM_WALL, 2), "omni_first_notch_Hz": round(c/(4*BAFFLE_FROM_WALL), 0),
        "note": "Quarter-wave estimate for an omni source at the baffle; the RL 901K's cardioid low-frequency radiation reduces rear energy, and thick front-wall absorption is proposed. Measure and tune on site."}
lp_ratio = (D - lp[1]) / D
# --- family cinema (screen just in front of the speakers, sofa against the rear diffusers) ---
SCR_W = 3.0; SCR_H = SCR_W * 9 / 16; SCR_Y = y_spk - 0.25; SCR_Z0 = 1.20
SOFA_EYE = (axis, 1.30, 1.05)
d_view = SCR_Y - SOFA_EYE[1]
cin = {"screen_width": SCR_W, "screen_height": round(SCR_H, 3), "screen_y": round(SCR_Y, 3), "screen_bottom_z": SCR_Z0,
       "sofa_eye": SOFA_EYE, "viewing_distance": round(d_view, 2),
       "horizontal_view_angle_deg": round(2 * math.degrees(math.atan(SCR_W / 2 / d_view)), 1),
       "elevation_to_centre_deg": round(math.degrees(math.atan((SCR_Z0 + SCR_H/2 - SOFA_EYE[2]) / d_view)), 1)}
t2 = (lp[1] + 0.38 + console["depth"] - SOFA_EYE[1]) / d_view
cin["sightline_z_at_console_back"] = round(SOFA_EYE[2] + t2 * (SCR_Z0 - SOFA_EYE[2]), 3)
cin["sightline_clears_console"] = cin["sightline_z_at_console_back"] > console["h_top"]
cin["projector"] = {"y": 0.95, "z": hc - 0.30, "throw_m": round(SCR_Y - 0.95, 2), "throw_ratio": round((SCR_Y - 0.95) / SCR_W, 2)}
SBIR_D = BAFFLE_FROM_WALL
out = {"layout": LAYOUT, "cinema": cin, "inputs": {"room": {"W": W, "D": D, "flat_ceiling": hc, "building_axis_x": axis}, "console_tape": console, "rl901k_tape": rl901k},
       "stereo": {"listening_position": [round(v, 3) for v in lp], "L": [round(v, 3) for v in spk["L"]], "R": [round(v, 3) for v in spk["R"]],
                  "spacing_m": round(2*half, 3), "ear_distance_m": DIST, "angle_deg": ANG, "toe_in_deg": toe_in,
                  "lp_from_front_wall_m": round(D - lp[1], 2), "lp_fraction_of_length_from_front": round(lp_ratio, 3), "lp_from_rear_wall_m": round(lp[1], 3),
                  "baffle_to_front_wall_m": BAFFLE_FROM_WALL, "console": console_pos,
                  "sightline_z_at_console_back_edge": round(z_line, 3), "meter_bridge_top": round(console["h_top"], 3),
                  "sightline_clear": z_line > console["h_top"]},
       "immersive_7_1_4": immersive, "posts_vs_lp": {"left_post": [P["dsL"], P["ypl"]], "right_post": [W - P["dsR"], P["ypr"]]},
       "axial_modes_Hz": modes, "modal_note": schroeder_note, "sbir_front": sbir}
json.dump(out, open(os.path.join(HERE, "monitoring_geometry.json"), "w"), indent=1)
print(json.dumps(out["stereo"], indent=1)); print(json.dumps(cin, indent=1)); print(json.dumps({k: v for k, v in immersive.items()}, indent=0)); print(modes, schroeder_note, sbir["omni_first_notch_Hz"])
