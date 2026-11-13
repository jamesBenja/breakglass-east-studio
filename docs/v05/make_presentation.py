"""Build the v0.5 presentation (HTML -> uploaded to Google Drive as a native Doc).

    python3 docs/v05/make_presentation.py <commit-sha>  -> docs/v05/presentation_v05.html
Images load from the public repo at a pinned commit (only owner-approved model renders and drawings; no private photos).
All numbers are read from acoustics/out/*.json so the Doc, drawings and model agree.
"""
import json, os, sys, html
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SHA = sys.argv[1]
RAW = f"https://raw.githubusercontent.com/jamesBenja/breakglass-east-studio/{SHA}/"
AO = os.path.join(ROOT, "acoustics", "out")
PLC = json.load(open(os.path.join(AO, "placements.json"))); LNG = json.load(open(os.path.join(AO, "lounge_layout.json")))
AN = json.load(open(os.path.join(AO, "modes_sbir_rt.json"))); COV = json.load(open(os.path.join(AO, "reflection_coverage.json")))
CST = json.load(open(os.path.join(AO, "costs_v05.json")))
import csv
MAT = list(csv.DictReader(open(os.path.join(AO, "deployment_matrix.csv"))))
e = html.escape
def img(path, w=640): return f'<p><img src="{RAW}{path}" width="{w}"></p>' if os.path.exists(os.path.join(ROOT, path)) else f"<p><i>[{e(path)} pending]</i></p>"
def table(head, rows):
    h = "".join(f"<th>{e(str(x))}</th>" for x in head)
    b = "".join("<tr>" + "".join(f"<td>{e(str(x))}</td>" for x in r) + "</tr>" for r in rows)
    return f'<table border="1" cellpadding="4" style="border-collapse:collapse;font-size:9pt">{"<tr>" + h + "</tr>"}{b}</table>'
cr = AN["control_room"]; T = CST["totals"]; fs = LNG["fireside_mode"]
P = []
P.append("<h1>Breakglass East v0.5 — Acoustic Integration &amp; Salvage Optimisation</h1>")
P.append(f"<p><b>Status: PROPOSED for owner review.</b> An evolution of the approved v0.4 fireside + cinema design, not a redesign. "
         "Not for construction: the shell is a phone-LiDAR + photo reconstruction (±0.1–0.2 m); acoustic numbers are screening ranges that an acoustician and on-site measurement must confirm. "
         f"Repository branch <code>claude/v05-acoustic-integration</code>, commit {SHA[:7]}. v0.4 files in Drive and Git are unchanged.</p>")
P.append("<h2>1. Concept</h2><ul>"
         "<li><b>Absorb where the reflections really land.</b> The trace on the measured tray ceiling puts the strongest early reflections (+9.5 to +15 ms) on the sloped and flat ceiling around Y 4.1–4.5 m. Four Clark GOB panels form a ceiling ‘halo’ exactly there.</li>"
         "<li><b>Deep bass control in the low side zones</b> (new under-sill bench traps, windows kept), corner traps, Clark tapered traps in the rear corners.</li>"
         "<li><b>Quiet front wall:</b> Clark Dead Room Roxul panels on 200 mm wool-filled stand-off frames, clear of the stove.</li>"
         "<li><b>Scattering rear wall:</b> the two Clark fin diffusers flank the entry door; a wool curtain covers the door (also film blackout).</li>"
         "<li><b>Fireside lounge corrected:</b> every lounge seat now faces the stove glass; one armchair rolls back for films.</li>"
         "<li><b>Live room stays a barn:</b> Clark barrels, perforated panels, rustic wood wall and gobos make it variable; machinery bays and the aisle to the garage door are untouched.</li></ul>")
P.append("<h2>2. Matched-camera comparisons (v0.4 approved → v0.5 proposed)</h2><p>Same camera, lens, samples and resolution; only the design differs.</p>")
for v in ("cr_front", "cr_fireside", "cr_cinema", "cr_rear", "cr_console", "axo_cutaway"):
    P.append(img(f"renders/compare_v04_v05/{v}.jpg", 640))
P.append("<h2>3. Control room drawings</h2>")
for d in ("PR-501_control_room_treatment_plan", "PR-502_control_room_RCP", "PR-503_control_room_elevations", "PR-504_control_room_sections"):
    P.append(img(f"drawings/v05/{d}.png", 640))
P.append("<h2>4. Corrected fireside lounge — two modes</h2>")
P.append(img("drawings/v05/PR-506_lounge_two_modes.png", 640))
P.append(table(["Piece", "Fireside mode", "Distance to fire", "Stove clearance", "Cinema mode"],
               [["Loveseat (2)", "faces the stove glass", f'{fs["loveseat"]["to_fire_m"]} m', f'{fs["loveseat"]["stove_clearance_m"]} m', "stays (behind the screen, not a viewing seat)"],
                ["Swivel armchair A", "faces the stove glass", f'{fs["swivel armchair A"]["to_fire_m"]} m', f'{fs["swivel armchair A"]["stove_clearance_m"]} m', "rolls on glides to the rear row"],
                ["Swivel armchair B", "rear row", "—", "—", "rear row (29.8° screen width)"]]))
P.append("<p>Constraints solved in <code>acoustics/lounge.py</code>: 0.90 m stove clearance (placeholder for the label / WETT value), speaker + cardioid clear zone, sub, traps, future Ls stand, doorway route to the live room clear, nobody blocking anybody's view of the fire. "
         "A third fireside seat was tested and does not fit behind the speaker line with these clearances — it is reported, not forced. No mechanisms.</p>")
P.append(img("renders/design/cr_fire_seat_v05.png", 640))
P.append("<h2>5. Monitoring, reflections and treatment</h2>")
P.append(img("drawings/v05/PR-505_monitoring_reflections.png", 640))
rows = [[r["speaker"], r["surface"], f'+{r["delay_ms"]:.1f}', f'{r["level_dB_re_direct"]:+.1f}', f'{r["off_axis_deg"]:.0f}°', ", ".join(r["treated_by"]) or r["status"]] for r in sorted(COV, key=lambda r: r["delay_ms"])]
P.append(table(["Spk", "Surface", "Delay ms", "Level dB", "Off-axis", "Intercepted by / status"], rows))
P.append(f"<p>Volume {cr['volume_m3']} m³ · Schroeder ≈ {cr['schroeder_Hz_at_0.3s']:.0f} Hz · EBU Tech 3276 target T<sub>m</sub> {cr['EBU3276_target_Tm_s']} s. "
         "Axial modes at the listening position: peaks 30.5 Hz (2,0,0), 62.8 Hz (0,3,0), 91.5 Hz (6,0,0); null 83.7 Hz (0,4,0). "
         "SBIR (omni ¼-wave): front wall 32 Hz, floor 67 Hz (console shadows the floor bounce), side walls 19–22 Hz; the RL 901K's cardioid bass weakens the front term.</p>")
P.append("<h2>6. The treated control room</h2>")
for v in ("cr_front_v05", "cr_ceiling_v05", "cr_rear_v05", "cr_cinema_v05"): P.append(img(f"renders/design/{v}.png", 640))
P.append("<h2>7. Live room treatment plan and configurations</h2>")
P.append(img("drawings/v05/PR-511_live_room_treatment_configs.png", 640))
P.append("<p>A piano / chamber (bright) · B ensemble (as modelled) · C band / overdubs (dead) · D farm mode (aisle clear, piano on a locked dolly in the west bay). Under-loft panels hang only over the storage bays (2.46 m clear), never over the machinery aisle.</p>")
P.append("<h2>8. Live room renders (farm equipment, piano, movable treatment)</h2>")
for v in ("live_piano", "live_farm"): P.append(img(f"renders/compare_v04_v05/{v}.jpg", 640))
P.append(img("renders/design/live_drums_v05.png", 640))
P.append(img("drawings/v05/PR-512_support_rooms_treatment.png", 640))
P.append("<h2>9. Inventory deployment matrix</h2>")
P.append(f"<p><b>74 counted units in 41 families → 71 allocated, 3 held/reserve, 0 over-allocated</b> (asserted in code). Control room 16 · live room 34 · vocal booth 11 · amp booth 7 · machine room 3. "
         "ABS-014 held (possible duplicate of ABS-010); ABS-004 and ABS-006 in reserve; DIF-002 / ABS-002 / MAT-002 uncounted, reserve only. Full matrix with mounting, air gaps and install notes is in the v0.5 workbook (tab ‘Asset deployment’).</p>")
P.append(table(["Asset", "Inv.", "Alloc.", "Res.", "Body (in)", "Verification", "Room", "Placement"],
               [[m["asset"], m["inventory"], m["allocated"], m["reserve"], m["body_in"], m["verification"], m["proposed_room"], m["placement"]] for m in MAT]))
P.append("<h2>10. New fabrication, mounting and materials</h2>")
P.append(table(["ID", "Room", "Item", "Qty", "Size", "Build", "Why"], [[i["id"], i["room"], i["item"], i["qty"], i["size_m"], i["build"], i["why"]] for i in PLC["new_items"]]))
P.append("<h2>11. Revised phased costs (CAD, planning allowances)</h2>")
P.append(table(["#", "Phase", "Package", "Low", "High", "Status"], [[l[0], l[1], l[2], f"${l[3]:,}", f"${l[4]:,}", l[5]] for l in CST["lines"]] +
               [["", "", "Essential subtotal", f"${T['essential_low']:,}", f"${T['essential_high']:,}", ""],
                ["", "", "Incl. 10–15 % contingency", f"${T['essential_incl_contingency'][0]:,}", f"${T['essential_incl_contingency'][1]:,}", f"v0.4: $38,830–$125,925"]] +
               [[l[0], l[1], l[2], f"${l[3]:,}", f"${l[4]:,}", l[5]] for l in CST["later"]]))
P.append("<h2>12. Acoustic rationale, uncertainties and commissioning</h2>")
rt = AN["rt_control_room"]
P.append(table(["Case (decay-time range, s)", "125 Hz", "500 Hz", "2 kHz"], [[k, f"{v['T_range_s'][1][0]}–{v['T_range_s'][1][1]}", f"{v['T_range_s'][3][0]}–{v['T_range_s'][3][1]}", f"{v['T_range_s'][5][0]}–{v['T_range_s'][5][1]}"] for k, v in rt.items()] +
               [[k, f"{v['T_range_s'][1][0]}–{v['T_range_s'][1][1]}", f"{v['T_range_s'][3][0]}–{v['T_range_s'][3][1]}", f"{v['T_range_s'][5][0]}–{v['T_range_s'][5][1]}"] for k, v in AN["rt_live_room"].items()]))
P.append("<p><b>How to read this:</b> ranges apply generic material-class bounds to the measured areas of the allocated assets — they are not the Clark panels' data, and the existing wall lining is unknown. "
         "They show direction: the recommended control room reaches the 0.36 s target at mid/high frequencies at its lower bound, while below 125 Hz it may stay long — which is why the new deep LF traps are in the base scope and more can be added after measurement.</p>")
P.append("<p><b>Commissioning:</b> C0 tape-verify assets (ABS-010/014, Sunny depths, ABS-004 polygon, weights, DIF fin photos) → C1 empty-room sweeps + RT + noise → C2 after LF traps → C3 after ceiling / front / rear (ETC at the LP; 9–17 ms window ≥ 15–20 dB below direct; tune speaker stands ±0.2 m) → C4 cinema / sub calibration (dual subs for the 30.5 / 62.8 Hz peaks) → C5 live-room configurations → C6 WETT stove clearances.</p>")
P.append("<p><b>Open items</b> (workbook tab ‘Open items’): U1 ABS-010/014 · U2 Sunny depths · U3 ABS-004 polygon · U4 weights + structural letter · U5 roof-void framing · U6 stove clearances · U7 DIF fin schedule · U8 GOB-006 tape · U9 existing lining · U10 tallest machine · U11 live-room window jambs · U12 measurements · U13 truck volume · U14 third fireside seat · U15 Below Breakglass counts.</p>")
P.append("<p><b>Changelog</b> v0.4 → v0.5: generic treatment replaced by measured Clark assets + NEW LF traps; lounge faces the fire; fixed cinema chairs become swivel armchairs; nothing in the building, equipment or monitoring geometry changed (v0.4 rebuild verified identical). "
         "<b>Decision requested:</b> approve v0.5 for development, or redirect. Nothing has been merged.</p>")
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "presentation_v05.html")
open(out, "w").write("<html><head><meta charset='utf-8'></head><body style='font-family:Arial'>" + "\n".join(P) + "</body></html>")
print("wrote", out, os.path.getsize(out))
