"""v0.5 Clark acoustic-asset allocation for Breakglass East (single source for matrix, model and drawings).

    python3 acoustics/allocation.py
      -> acoustics/out/inventory_snapshot.json   (public-safe copy of the owner's 'Acoustic Assets' tab, no Drive links)
      -> acoustics/out/placements.json           (every placed unit with exact body size, position, rotation, air gap)
      -> acoustics/out/deployment_matrix.csv / .md
Rules (owner handoff 2026-11-13):
  * Never allocate more units than the verified inventory count (asserted below).
  * ABS-010 / ABS-014 may be the same panel: only ABS-010 is placed; ABS-014 is held until the owner confirms.
  * DIF-002, ABS-002, MAT-002 are uncounted / unmeasured: reserve only.
  * Body dimensions are the owner's measurements (inches -> metres). Unknown depths are modelled at a
    PROVISIONAL 0.05 m and flagged; no absorption coefficients are assigned to individual assets.
Coordinates: model frame (docs/COORDINATE_SYSTEM.md). Control room uses model/monitoring_geometry.json (v0.4 fireside).
"""
import csv, json, math, os, sys
from collections import Counter
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from geometry import P, G, W, D, AX, ST
OUT = os.path.join(HERE, "out"); os.makedirs(OUT, exist_ok=True)
IN = 0.0254

# ---------------------------------------------------------------- inventory (owner sheet, 2026-11-13; inches)
# id: (clark_room, count, w, h, d, verification, construction summary)
INV = {
 "HYB-001": ("Dead Room", 3, 45.7, 98, 9, "DIMENSIONS DOCUMENTED", "barrel perforated wood 0.75 in shell, 4 in edges to 9 in centre, open rear, 30 in chains"),
 "DIF-001": ("Resident Suite", 2, 52, 80, 5, "DIMENSIONS DOCUMENTED", "wooden fin diffuser, variable fin projection (not a QRD); demountable"),
 "DIF-003": ("Live Room", 1, 52, 80, 5, "DIMENSIONS DOCUMENTED", "same design as DIF-001"),
 "DIF-004": ("Vocal Booth", 1, 52, 80, 5, "DIMENSIONS DOCUMENTED", "same design as DIF-001"),
 "BTR-001": ("Resident Suite", 2, 46.5, 15, 12, "DIMENSIONS DOCUMENTED", "tapered foam trap, 12 in bottom to 6.2 in top depth, ~3 in fabric gap, solid wood back"),
 "BTR-002": ("Live Room", 3, 46.5, 15, 12, "DIMENSIONS DOCUMENTED", "same as BTR-001"),
 "BTR-003": ("Vocal Booth", 1, 46.5, 15, 12, "DIMENSIONS DOCUMENTED", "same as BTR-001"),
 "BTR-004": ("Sunny Suite", 1, 46.5, 15, 12, "INHERITED FROM BTR-001", "count owner-confirmed; dims inherited"),
 "ABS-001": ("Sunny Suite", 1, 49, 49, 5, "DIMENSIONS DOCUMENTED", "ceiling cloud; core/backing unverified"),
 "ABS-003": ("Dead Room", 2, 134, 30, 4, "DIMENSIONS DOCUMENTED", "Roxul full 4 in, blue fabric, mesh back, no backboard"),
 "PAN-001": ("Dead Room", 3, 24.8, 97, 5, "DIMENSIONS DOCUMENTED", "Roxul full 5 in, wood frame, mesh back, mounted direct to wall"),
 "PAN-002": ("Vocal Booth", 1, 18, 36, 2, "DIMENSIONS DOCUMENTED", "Roxul full 2 in, mesh back"),
 "ABS-004": ("Sunny Suite", 1, 49, 24, 4, "POLYGON NOT MEASURED", "tapered cloud 49 / 10.2 in edges, 24 in across, recessed light"),
 "ABS-005": ("Sunny Suite", 2, 55.5, 46, None, "DEPTH UNKNOWN", "fabric panel, core unknown"),
 "ABS-006": ("Sunny Suite", 1, 95.5, 13.4, None, "DEPTH UNKNOWN", "blue strip panel, core unknown"),
 "ABS-007": ("Sunny Suite", 1, 48, 24, None, "DEPTH UNKNOWN", "panel, core unknown"),
 "ABS-008": ("Sunny Suite", 2, 46, 55, None, "DEPTH UNKNOWN", "tan fabric panel, core unknown"),
 "ABS-009": ("Sunny Suite", 2, 25.1, 58, None, "DEPTH UNKNOWN", "blue fabric panel, core unknown"),
 "ABS-010": ("Sunny Suite", 1, 25.1, 58, None, "DUPLICATION CHECK", "blue panel; size inferred; may be ABS-014"),
 "ABS-011": ("Sunny Suite", 1, 85, 49, None, "DEPTH UNKNOWN", "tan fabric panel, core unknown"),
 "ABS-012": ("Sunny Suite", 1, 36.5, 24, None, "DEPTH UNKNOWN", "blue panel, core unknown"),
 "ABS-013": ("Sunny Suite", 1, 36.5, 24, None, "DEPTH UNKNOWN", "blue panel, core unknown"),
 "ABS-014": ("Sunny Suite", 1, 25.1, 58, None, "DUPLICATION CHECK", "possible duplicate of ABS-010"),
 "ABS-015": ("Vocal Booth", 1, 55.5, 45.5, 4, "DIMENSIONS DOCUMENTED", "Roxul core confirmed; fill extent/backing unknown"),
 "ABS-016": ("Vocal Booth", 1, 25, 84, 4, "DIMENSIONS DOCUMENTED", "Roxul core confirmed; fill extent/backing unknown"),
 "GOB-001": ("Live Room", 5, 49.7, 97, 3.6, "DIMENSIONS DOCUMENTED", "wheeled gobo, Roxul, 103 in overall"),
 "GOB-002": ("Live Room", 2, 55, 45.5, 3.5, "DIMENSIONS DOCUMENTED", "half-height wheeled gobo, pegboard both faces, fill unknown, 52 in overall"),
 "GOB-003": ("Resident Suite", 5, 49.8, 96, 3, "DIMENSIONS DOCUMENTED", "Roxul + burlap, suspended, no wheels"),
 "GOB-004": ("Resident Suite", 1, 49.8, 96, 3, "DIMENSIONS DOCUMENTED", "Roxul + burlap, ceiling-hung horizontal"),
 "GOB-005": ("Resident Suite", 4, 45, 42, 3, "DIMENSIONS DOCUMENTED", "Roxul + burlap, small"),
 "GOB-006": ("Live Room", 2, 49.8, 96, 3, "FAMILY MATCHED (NOT TAPED)", "matched to GOB-003; verify on removal"),
 "PRF-001": ("Live Room", 4, 24, 95, 1, "DIMENSIONS DOCUMENTED", "perforated wood + fabric + air, 2 in shims"),
 "PRF-002": ("Live Room", 3, 30, 60, 1, "DIMENSIONS DOCUMENTED", "perforated wood + fabric + air, 2 in shims"),
 "WOOD-001": ("Live Room", 6, 49.5, 15.8, 4, "DIMENSIONS DOCUMENTED", "hollow open-backed rustic wood box"),
 "WOOD-002": ("Live Room", 2, 47, 15.3, 4, "DIMENSIONS DOCUMENTED", "hollow open-backed rustic wood box"),
 "WOOD-003": ("Live Room", 1, 16.8, 37.8, 4, "DIMENSIONS DOCUMENTED", "hollow open-backed rustic wood box"),
 "WOOD-004": ("Live Room", 1, 33, 10.5, 2.5, "DIMENSIONS DOCUMENTED", "hollow open-backed rustic wood box"),
 "WOOD-005": ("Live Room", 1, 18, 13, 4, "DIMENSIONS DOCUMENTED", "hollow open-backed rustic wood box"),
 "DIF-002": ("Below Breakglass", None, None, None, None, "COUNT UNKNOWN", "slatted assembly, photo only"),
 "ABS-002": ("Below Breakglass", None, None, None, None, "COUNT UNKNOWN", "thin wall panels, photo only"),
 "MAT-002": ("Below Breakglass", None, None, None, None, "COUNT UNKNOWN", "paper-covered treatment, photo only"),
}
assert len(INV) == 41 and sum(v[1] or 0 for v in INV.values()) == 74, "inventory snapshot must match owner sheet (41 families, 74 units)"

def m(inches): return None if inches is None else round(inches * IN, 4)
PROV_DEPTH = 0.05

# ---------------------------------------------------------------- building references
xL, xR, xc1, xc2, hc = G["xL"], G["xR"], G["xc1"], G["xc2"], G["hc"]
LP = ST["listening_position"]; LPy = LP[1]
B = json.load(open(os.path.join(ROOT, "model/scan_building_measurements.json")))
Y_OFF = 15.185; F_MID, F_LIVE = B["middle_floor"], B["live_floor"]
Y_PART1 = D + 0.15; Y_MID1 = 1.0 + Y_OFF; Y_LOFT_END = 7.7 + Y_OFF; Y_LG = B["live_gable_y"] + Y_OFF
LIVE_L, LIVE_R = AX - 6.15, AX + 5.75; LIVE_HC = B["live_flat_ceiling"]; UL_CLG = B["underloft_ceiling"]
CORR0, CORR1 = AX - 0.70, AX + 0.70   # as model/build_studio.py
STOVE_CLEAR_X = P["g_xs"] - 0.28 - 0.90
def slope_z(x):
    if x <= xc1: return G["hbL"] + (hc - G["hbL"]) * (x - xL) / (xc1 - xL)
    return G["hbR"] + (hc - G["hbR"]) * (xR - x) / (xR - xc2)
ANG_L = -math.degrees(math.atan2(hc - G["hbL"], xc1 - xL)); ANG_R = math.degrees(math.atan2(hc - G["hbR"], xR - xc2))

# ---------------------------------------------------------------- placements
PL = []
def place(asset, room, zone, purpose, shape, centre, size, rot=(0, 0, 0), gap=0.0, mode="reuse intact", install="", status=None, note=""):
    inv = INV[asset]
    PL.append({"asset": asset, "room": room, "zone": zone, "purpose": purpose, "shape": shape,
               "centre": [round(c, 3) for c in centre], "size": [round(s, 4) for s in size], "rot_deg": [round(r, 2) for r in rot],
               "air_gap_m": gap, "mode": mode, "install": install, "verification": status or inv[5], "note": note,
               "depth_provisional": INV[asset][4] is None})
def body(asset, horizontal=False):
    _, _, w, h, d, _, _ = INV[asset]; dd = m(d) if d else PROV_DEPTH
    return (m(h), m(w), dd) if horizontal else (m(w), m(h), dd)

CR = "Control room"
# --- ceiling 'halo' over the first-reflection zone (from acoustics/out/first_reflections.json)
yc = 3.82; cw, cl, ct = m(49.8), m(96), m(3)
for asset, x in (("GOB-004", AX - cw / 2 - 0.025), ("GOB-003", AX + cw / 2 + 0.025)):
    place(asset, CR, "flat-ceiling cloud", "absorb flat-ceiling first reflections (10.5 ms, -7 dB)", "panel",
          (x, yc, hc - 0.20 - ct / 2), (cw, cl, ct), gap=0.20, mode="reuse intact (rehang horizontal)",
          install="4-point aircraft-cable suspension from ceiling framing; structural check of fixings")
for x0, ang in ((3.45, ANG_L), (8.31, ANG_R)):
    z = slope_z(x0) - 0.05 - ct / 2
    place("GOB-003", CR, "sloped-ceiling panel", "absorb same/opposite-side sloped-ceiling reflections (9.5-15 ms)", "panel",
          (x0, yc, z), (cw, cl, ct), rot=(0, ang, 0), gap=0.05, mode="reuse intact (fixed parallel to slope)",
          install="Z-clips/cleats into slope framing, 50 mm stand-off; long edge along the room")
# --- rear wall: fin diffusers flanking the centred entry door (rear reflection 17 ms, near on-axis)
for x in (AX - 1.229, AX + 1.221):
    place("DIF-001", CR, "rear wall flanking entry door", "scatter rear-wall reflections behind the mix position", "diffuser",
          (x, m(5) / 2, 0.92 + m(80) / 2), (m(52), m(5), m(80)), mode="reuse (reassemble fins in original order)",
          install="French cleat to gable wall; bottom 0.92 m clears the cinema sofa back", note="fin layout in model is indicative; real fin order from DIF-001 photos")
# --- rear corners: tapered traps (two per corner, L-shaped)
for asset, x, y, yaw in (("BTR-001", 0.05 + m(46.5) / 2, 0.0, 0), ("BTR-001", 0.0, 0.35 + m(46.5) / 2, -90),
                         ("BTR-002", W - 0.05 - m(46.5) / 2, 0.0, 0), ("BTR-002", W, 0.35 + m(46.5) / 2, 90)):
    place(asset, CR, "rear corner", "low-frequency/corner absorption (rear corners)", "btr", (x, y, 0), (m(46.5), m(12), m(15)), rot=(0, 0, yaw),
          install="floor-standing against wall/corner; solid wood back to wall")
# --- front wall: Dead Room Roxul panels, clear of the stove (front reflections 15 ms)
for i, z0 in enumerate((0.45, 1.26)):
    place("ABS-003", CR, "front wall right of doorway", "broadband absorption behind the speakers (right front reflection point X 6.81)", "panel",
          (6.70 + m(134) / 2, D - 0.20 - m(4) / 2, z0 + m(30) / 2), (m(134), m(4), m(30)), mode="reuse intact (horizontal, stacked)",
          gap=0.20, install="re-hung on NEW-07 200 mm stand-off frame filled with mineral wool")
for i, z0 in enumerate((0.15, 0.80, 1.45)):
    place("PAN-001", CR, "front wall left (outside stove clearance)", "broadband absorption front-left", "panel",
          (0.72 + m(97) / 2, D - 0.20 - m(5) / 2, z0 + m(24.8) / 2), (m(97), m(5), m(24.8)), mode="reuse intact (turned horizontal)",
          gap=0.20, install="on NEW-07 stand-off frame (was direct-to-wall at Clark); > 0.9 m from the stove (verify label/WETT)")
# --- left side wall between windows (right-speaker side reflection, 31 ms)
place("GOB-005", CR, "left wall between windows", "late side reflection R->left wall (Y 4.16)", "panel",
      (m(3) / 2 + 0.05, 3.67, 1.17 + m(42) / 2), (m(3), m(45), m(42)), gap=0.05, install="cleats, 50 mm stand-off")

LV = "Live room"
# --- live room left wall (tray zone): perforated panels + diffuser/trap pair, between windows
for y in (23.25, 24.0, 29.65, 30.25):
    place("PRF-001", LV, "left wall, tray zone", "mid/high variable reflection (angled on shims as at Clark)", "panel",
          (LIVE_L + 0.05 + m(1) / 2, y, F_LIVE + 0.20 + m(95) / 2), (m(1), m(24), m(95)), rot=(0, 0, 4), gap=0.05,
          mode="reuse intact (2 in shims, angled)")
place("DIF-003", LV, "left wall, tray zone", "scattering near the piano position", "diffuser",
      (LIVE_L + m(5) / 2, 26.85, F_LIVE + 0.40 + m(80) / 2), (m(52), m(5), m(80)), rot=(0, 0, -90), mode="reuse (reassemble)")
place("BTR-002", LV, "left wall under DIF-003", "LF trap paired with diffuser", "btr", (LIVE_L, 26.85, F_LIVE), (m(46.5), m(12), m(15)), rot=(0, 0, -90))
# --- live room right wall: the rustic wood wall (all 11 pieces), as at Clark
rw = LIVE_R - m(4) / 2
wood = [("WOOD-001", 23.6, 0.45), ("WOOD-001", 23.6, 0.90), ("WOOD-001", 23.6, 1.35), ("WOOD-004", 23.6, 1.80),
        ("WOOD-001", 26.53, 0.40), ("WOOD-001", 26.53, 0.85), ("WOOD-001", 26.53, 1.30), ("WOOD-002", 26.53, 1.75), ("WOOD-002", 26.53, 2.20),
        ("WOOD-003", 27.55, 0.40), ("WOOD-005", 27.55, 1.42)]
for a, y, z0 in wood:
    _, _, w, h, d, _, _ = INV[a]
    place(a, LV, "right wall rustic wood composition", "visual + unknown scattering (open-backed hollow boxes; no acoustic claim)", "wood_box",
          (LIVE_R - m(d) / 2, y, F_LIVE + z0 + m(h) / 2), (m(d), m(w), m(h)), mode="reuse intact (open back to wall)",
          install="cleats; open backs face the wall (as built at Clark)", note="internal wall thickness unknown - modelled 15 mm nominal")
# --- live gable (garage end): PRF-002 row left of the door, one vertical HYB right of the door
for x in (0.75, 1.75, 2.75):
    place("PRF-002", LV, "garage gable wall, left of door", "mid/high control at the garage end", "panel",
          (x, Y_LG - 0.05 - m(1) / 2, F_LIVE + 0.60 + m(60) / 2), (m(30), m(1), m(60)), gap=0.05, mode="reuse intact (2 in shims)")
place("HYB-001", LV, "garage gable wall, right of door", "vertical abfusor (absorb/scatter) at the garage end", "hyb",
      (9.10, Y_LG - 0.05 - m(9) / 2, F_LIVE + 0.15 + m(98) / 2), (m(45.7), m(98), m(9)), rot=(-90, 0, 0), mode="reuse intact (vertical, chain to wall cleat)")
# --- live room ceiling: two horizontal HYB abfusors over the piano / ensemble area (30 in chains)
for x in (AX - 0.75, AX + 0.75):
    place("HYB-001", LV, "tray-zone ceiling over piano/ensemble", "overhead absorb/scatter, tames flutter under the flat ceiling", "hyb",
          (x, 26.6, LIVE_HC - m(30) - m(9) / 2), (m(45.7), m(98), m(9)), mode="reuse intact (horizontal, 30 in chains)",
          install="chains to structure; verify ceiling framing load")
# --- under-loft ceiling over the two machinery/overflow bays (NOT over the machinery aisle: keeps aisle headroom)
GD_W = 3.70; BAY_L = (LIVE_L + 0.3, AX - GD_W / 2 - 0.3); BAY_R = (AX + GD_W / 2 + 0.3, LIVE_R - 0.3)
for a, x, y in (("GOB-003", BAY_L[1] - 0.70, 19.95), ("GOB-003", BAY_L[1] - 2.05, 19.95), ("GOB-006", BAY_R[0] + 0.70, 19.95), ("GOB-006", BAY_R[0] + 2.05, 19.95)):   # between the scan posts
    place(a, LV, "under-loft ceiling over the storage bays", "damp the low joist ceiling (slab-to-joist flutter); covers the foil insulation", "panel",
          (x, y, UL_CLG - 0.05 - ct / 2), (cw, cl, ct), gap=0.05, mode="reuse intact (horizontal under joists)",
          install="screwed cleats to joists; 2.46 m clear above the slab in the bays only (check against the tallest stored machine)")
# --- movable gobos (live room tray zone); shown in the default 'ensemble' configuration (piano + band: drums, amps, vocal/acoustic)
DRUM = (AX + 3.35, 24.15)
for i, (x, y, yaw) in enumerate(((DRUM[0] - 1.10, DRUM[1] + 0.30, 75), (DRUM[0] - 0.30, DRUM[1] + 1.16, 15), (DRUM[0] + 0.93, DRUM[1] + 0.98, -30),
                                 (AX - 3.40, 27.30, 70), (AX + 0.90, 25.40, 80))):
    place("GOB-001", LV, "movable (ensemble config: 3 around drums, 2 screening piano / strings)", "movable isolation/absorption", "gobo_wheeled",
          (x, y, F_LIVE + 0.15 + m(97) / 2), (m(49.7), m(3.6), m(97)), rot=(0, 0, yaw), mode="reuse intact (wheeled)")
for i, (x, y, yaw) in enumerate(((AX + 3.75, 29.30, 60), (AX + 1.10, 29.60, 10))):
    place("GOB-002", LV, "movable half-height (amps / sight-line screens)", "low screens (pegboard both faces; fill unknown)", "gobo_wheeled",
          (x, y, F_LIVE + 0.17 + m(45.5) / 2), (m(55), m(3.5), m(45.5)), rot=(0, 0, yaw), mode="reuse intact (wheeled)")

# --- support rooms (existing partitions only; scan-inferred)
VB, AB, MR = "Vocal booth (middle zone, west room)", "Amp / iso booth (middle zone, east room)", "Machine room (middle zone, east room by control room)"
vb_y0, vb_y1 = Y_PART1 + 0.06, Y_PART1 + 4.55 - 0.06
place("DIF-004", VB, "cross wall", "scattering behind the singer (as at Clark)", "diffuser", (2.6, vb_y1 - m(5) / 2, F_MID + 0.40 + m(80) / 2), (m(52), m(5), m(80)), rot=(0, 0, 180), mode="reuse (reassemble)")
place("BTR-003", VB, "under DIF-004", "LF trap paired with diffuser", "btr", (2.6, vb_y1, F_MID), (m(46.5), m(12), m(15)), rot=(0, 0, 180))
place("ABS-015", VB, "west wall", "broadband absorption", "panel", (m(4) / 2 + 0.03, vb_y0 + 1.3, F_MID + 0.9 + m(45.5) / 2), (m(4), m(55.5), m(45.5)), gap=0.03)
place("ABS-011", VB, "west wall", "broadband absorption", "panel", (m(4) / 2 + 0.03, vb_y0 + 3.3, F_MID + 0.75 + m(49) / 2), (PROV_DEPTH, m(85), m(49)), gap=0.03, status="DEPTH UNKNOWN")
place("ABS-016", VB, "corridor wall", "tall broadband panel", "panel", (CORR0 - 0.06 - m(4) / 2, vb_y0 + 1.0, F_MID + 0.15 + m(84) / 2), (m(4), m(25), m(84)))
for x in (1.0, 2.6):
    place("ABS-008", VB, "partition wall (control-room side)", "absorption", "panel", (x, vb_y0 + PROV_DEPTH / 2, F_MID + 0.8 + m(55) / 2), (m(46), PROV_DEPTH, m(55)))
place("PAN-002", VB, "partition wall", "small absorber", "panel", (4.2, vb_y0 + m(2) / 2, F_MID + 1.2 + m(36) / 2), (m(18), m(2), m(36)))
place("ABS-001", VB, "ceiling cloud over the vocal mic", "ceiling absorption", "panel", (2.6, vb_y0 + 2.2, F_MID + 2.54 - 0.10 - m(5) / 2), (m(49), m(49), m(5)), gap=0.10)
for y in (vb_y0 + 2.6, vb_y0 + 3.75):
    place("GOB-005", VB, "corridor wall", "absorption", "panel", (CORR0 - 0.06 - m(3) / 2, y, F_MID + 0.9 + m(42) / 2), (m(3), m(45), m(42)))
ab_y0, ab_y1 = Y_PART1 + 2.05 + 0.06, Y_PART1 + 5.75 - 0.06
for y in (ab_y0 + 0.9, ab_y0 + 2.5):
    place("ABS-005", AB, "east wall", "absorption around amps", "panel", (W - PROV_DEPTH / 2, y, F_MID + 0.6 + m(46) / 2), (PROV_DEPTH, m(55.5), m(46)))
for x in (CORR1 + 1.2, CORR1 + 2.4):
    place("ABS-009", AB, "south cross wall", "absorption", "panel", (x, ab_y0 + PROV_DEPTH / 2, F_MID + 0.5 + m(58) / 2), (m(25.1), PROV_DEPTH, m(58)))
place("ABS-010", AB, "north cross wall", "absorption", "panel", (CORR1 + 1.8, ab_y1 - PROV_DEPTH / 2, F_MID + 0.5 + m(58) / 2), (m(25.1), PROV_DEPTH, m(58)), note="ABS-014 held until duplicate resolved")
place("BTR-004", AB, "corner", "LF trap", "btr", (W - 0.05 - m(46.5) / 2, ab_y1, F_MID), (m(46.5), m(12), m(15)), rot=(0, 0, 180))
place("GOB-005", AB, "corridor wall", "absorption", "panel", (CORR1 + 0.06 + m(3) / 2, ab_y0 + 1.6, F_MID + 0.9 + m(42) / 2), (m(3), m(45), m(42)))
mr_y0 = Y_PART1 + 0.06
place("ABS-007", MR, "east wall", "fan-noise absorption", "panel", (W - PROV_DEPTH / 2, mr_y0 + 1.0, F_MID + 1.2 + m(24) / 2), (PROV_DEPTH, m(48), m(24)))
for x in (CORR1 + 1.0, CORR1 + 2.3):
    place("ABS-012" if x < CORR1 + 2 else "ABS-013", MR, "partition wall", "fan-noise absorption", "panel", (x, mr_y0 + PROV_DEPTH / 2, F_MID + 1.3 + m(24) / 2), (m(36.5), PROV_DEPTH, m(24)))

RESERVE_NOTE = {"ABS-004": "reserve: tapered polygon and light aperture unmeasured; candidate for the fireside lounge ceiling once surveyed",
                "ABS-006": "reserve: 95.5 x 13.4 in strip; candidate for the lounge or a booth once depth is known",
                "ABS-014": "held: possible duplicate of ABS-010 (owner to confirm)",
                "DIF-002": "reserve: count/size unknown (photo only) - measure before allocating",
                "ABS-002": "reserve: count/size unknown (photo only)", "MAT-002": "reserve: count/size unknown (photo only)"}

# ---------------------------------------------------------------- new purpose-built items (not Clark assets)
NEW = [
 {"id": "NEW-01", "room": CR, "item": "Under-sill low-frequency bench traps, both side walls", "qty": 2, "size_m": "≈5.85 m long × 0.75 deep × 1.10 high each (v0.4 envelope, under the sills)",
  "build": "Mineral wool (e.g. 2 layers 100–150 mm + air) behind fabric and spaced reclaimed-wood slats; window sills stay clear", "why": "the room's main LF control; the Clark inventory has no deep traps",
  "geom": [{"centre": [0.375, 4.525, 0.55], "size": [0.75, 5.85, 1.10]}, {"centre": [W - 0.375, 4.525, 0.55], "size": [0.75, 5.85, 1.10]}]},
 {"id": "NEW-02", "room": CR, "item": "Front-corner full-height corner traps", "qty": 2, "size_m": "triangular, 0.70 m legs, floor to low ceiling (≈2.2 m)",
  "build": "Stacked mineral-wool triangles behind fabric", "why": "pressure maxima of all modes are in the corners",
  "geom": [{"tri": [0, D, 0.70], "h": G["hloL"] - 0.02}, {"tri": [W, D, 0.70], "h": G["hloR"] - 0.02}]},
 {"id": "NEW-03", "room": CR, "item": "Heavy wool acoustic curtain across the gable entry door", "qty": 1, "size_m": "≈1.3 × 2.2 m on a ceiling track",
  "build": "Heavy wool/velour, generous fullness", "why": "the rear reflection lands on the door jambs (17 ms, near on-axis); also draught and cinema blackout",
  "geom": [{"centre": [AX, 0.16, 1.10], "size": [1.30, 0.06, 2.20]}]},
 {"id": "NEW-04", "room": CR, "item": "Fabric-faced folding window shutters / blackout", "qty": 6, "size_m": "to suit 4 side + 2 gable windows",
  "build": "Insulated board + fabric face, hinged in the reveals", "why": "late side reflections fall on glass; daytime film blackout; Quiet-Light daylight control", "geom": []},
 {"id": "NEW-07", "room": CR, "item": "Front-wall stand-off frames: reused ABS-003 / PAN-001 mounted 200 mm proud, cavity filled with mineral wool", "qty": 1, "size_m": "≈3.4 × 1.6 m right + 2.5 × 1.9 m left, 200 mm deep",
  "build": "Timber stand-off frame, mineral-wool batts in the cavity, Clark panels re-hung on the face unmodified", "why": "turns 100-125 mm panels into ~300 mm broadband absorbers (the v0.4 front-wall intent) without new panels",
  "geom": [{"centre": [6.70 + 3.4036 / 2, D - 0.10, 1.215], "size": [3.4036, 0.20, 1.55]}, {"centre": [0.72 + 2.4638 / 2, D - 0.10, 1.10], "size": [2.4638, 0.20, 1.93]}]},
 {"id": "NEW-05", "room": "All", "item": "Mounting kit: cleats, aircraft cable, chains, stand-off brackets", "qty": 1, "size_m": "-", "build": "-", "why": "hang the reused assets safely", "geom": []},
 {"id": "NEW-06", "room": LV, "item": "Farm-mode protective covers (piano, gobos) and stove-safe hearth pad", "qty": 1, "size_m": "-", "build": "-", "why": "dust/fumes when machinery moves", "geom": []},
]

# ---------------------------------------------------------------- world footprints (single geometry source for model + drawings)
def _rot(v, rot):
    rx, ry, rz = (math.radians(a) for a in rot); x, y, z = v
    y, z = y * math.cos(rx) - z * math.sin(rx), y * math.sin(rx) + z * math.cos(rx)
    x, z = x * math.cos(ry) + z * math.sin(ry), -x * math.sin(ry) + z * math.cos(ry)
    x, y = x * math.cos(rz) - y * math.sin(rz), x * math.sin(rz) + y * math.cos(rz)
    return x, y, z
for p in PL:
    sx, sy, sz = p["size"]
    if p["shape"] == "btr":   # anchor = back-bottom-centre on the wall; local +Y into the room
        loc = [(x, y, z) for x in (-sx/2, sx/2) for y in (0, sy) for z in (0, sz)]
    else:
        loc = [(x, y, z) for x in (-sx/2, sx/2) for y in (-sy/2, sy/2) for z in (-sz/2, sz/2)]
    w = [tuple(c + d for c, d in zip(p["centre"], _rot(v, p["rot_deg"]))) for v in loc]
    p["aabb"] = [[round(min(q[i] for q in w), 3) for i in range(3)], [round(max(q[i] for q in w), 3) for i in range(3)]]
    p["footprint_xy"] = [[round(q[0], 3), round(q[1], 3)] for q in w if q[2] == min(r[2] for r in w)][:4]

# ---------------------------------------------------------------- validation + outputs
used = Counter(p["asset"] for p in PL)
for a, n in used.items():
    have = INV[a][1]
    assert have is not None and n <= have, f"{a}: allocated {n} > inventory {have}"
assert used.get("ABS-014", 0) == 0, "ABS-014 must be held until the duplicate check"
rows = []
for a, (room, cnt, w, h, d, ver, cons) in INV.items():
    n = used.get(a, 0); rem = None if cnt is None else cnt - n
    rooms = sorted({p["room"] for p in PL if p["asset"] == a})
    zones = sorted({p["zone"] for p in PL if p["asset"] == a})
    purp = sorted({p["purpose"] for p in PL if p["asset"] == a})
    modes = sorted({p["mode"] for p in PL if p["asset"] == a})
    gaps = sorted({p["air_gap_m"] for p in PL if p["asset"] == a})
    inst = sorted({p["install"] for p in PL if p["asset"] == a and p["install"]})
    rows.append({"asset": a, "clark_room": room, "inventory": "" if cnt is None else cnt, "allocated": n, "reserve": "" if rem is None else rem,
                 "body_in": "" if w is None else f"{w} × {h} × {d if d else '?'}", "verification": ver,
                 "proposed_room": "; ".join(rooms) or "RESERVE", "placement": "; ".join(zones), "purpose": "; ".join(purp),
                 "mounting_air_gap_m": "; ".join(str(g) for g in gaps), "reuse_mode": "; ".join(modes), "install": " | ".join(inst),
                 "notes": RESERVE_NOTE.get(a, "") + (" depth PROVISIONAL 0.05 m in model" if d is None and n else "")})
with open(os.path.join(OUT, "deployment_matrix.csv"), "w", newline="") as f:
    wr = csv.DictWriter(f, fieldnames=list(rows[0])); wr.writeheader(); wr.writerows(rows)
json.dump({"placements": PL, "new_items": NEW, "ensemble": {"drum_centre": [round(DRUM[0], 3), round(DRUM[1], 3)]}, "inventory_units": 74, "allocated_units": sum(used.values()),
           "reserve": RESERVE_NOTE}, open(os.path.join(OUT, "placements.json"), "w"), indent=1)
json.dump({k: {"clark_room": v[0], "count": v[1], "w_in": v[2], "h_in": v[3], "d_in": v[4], "verification": v[5], "construction": v[6]} for k, v in INV.items()},
          open(os.path.join(OUT, "inventory_snapshot.json"), "w"), indent=1)
with open(os.path.join(OUT, "deployment_matrix.md"), "w") as f:
    f.write("| Asset | Inv. | Alloc. | Reserve | Body (in) | Verification | Room | Placement | Purpose | Gap (m) | Reuse |\n|---|---|---|---|---|---|---|---|---|---|---|\n")
    for r in rows:
        f.write(f"| {r['asset']} | {r['inventory']} | {r['allocated']} | {r['reserve']} | {r['body_in']} | {r['verification']} | {r['proposed_room']} | {r['placement']} | {r['purpose']} | {r['mounting_air_gap_m']} | {r['reuse_mode']} |\n")
print(f"families {len(INV)}, inventory 74, allocated {sum(used.values())}, by room:", Counter(p['room'] for p in PL))
print("reserve/held:", {a: INV[a][1] - used.get(a, 0) for a in INV if INV[a][1] and INV[a][1] - used.get(a, 0)})
