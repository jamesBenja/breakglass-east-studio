"""Breakglass East — whole-building Blender model: EXISTING shell + actual equipment + PROPOSED fit-out.

    python3 model/build_studio.py                 # build + save model/breakglass_east_v04.blend
    BG_RENDER=1 python3 model/build_studio.py     # also render renders/design/*.png (Cycles CPU)
    BG_ONLY=cr_front,live_piano BG_RENDER=1 ...   # render a subset

Single source of truth for numbers:
  model/solve_result.json               control-room shell (fused scan + photo solve)
  model/scan_building_measurements.json live room / middle zone / loft (native LiDAR mesh)
  model/monitoring_geometry.json        speaker, console, listening and 7.1.4 positions
Frame: docs/COORDINATE_SYSTEM.md (origin = control-room floor, left/gable interior corner).

Collections separate evidence classes: 1x EXISTING (scan/photo), 2x EQUIPMENT (actual gear from
owner tape measurements), 3x PROPOSED (design - editable, not approved), 9x CAMERAS.
Openings are real boolean cuts (live modifiers, cutters hidden) - review finding G1-01.
"""
import json, math, os, sys
import bpy
from mathutils import Vector, Matrix

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from section import geom
SOL = json.load(open(os.path.join(HERE, "solve_result.json")))
P = {k: v["value"] for k, v in SOL["params"].items()}
G = geom(P)
B = json.load(open(os.path.join(HERE, "scan_building_measurements.json")))
MG = json.load(open(os.path.join(HERE, "monitoring_geometry.json")))
W, D, AX = G["W"], G["D"], G["xf"]

# ------------------------------------------------------------------ building zones (local frame)
Y_OFF = 15.185                       # global scan Y of the control-room gable -> local Y = global + Y_OFF
F_MID, F_LIVE = B["middle_floor"], B["live_floor"]              # -0.225, -0.355 (rel. control floor)
Y_PART0, Y_PART1 = D, D + 0.15                                   # control/middle partition (thickness nominal)
Y_MID1 = 1.0 + Y_OFF                                             # middle zone ends (scan plan slice)
Y_LOFT_END = 7.7 + Y_OFF                                         # end of loft / under-loft zone
Y_LIVE_G = B["live_gable_y"] + Y_OFF                             # live-room gable interior face
LIVE_L, LIVE_R = AX - 6.15, AX + 5.75                            # live-room side walls (scan, aligned to flat-ceiling axis)
LIVE = dict(hlo_l=B["live_low_ceiling_left"], hlo_r=B["live_low_ceiling_right"], hc=B["live_flat_ceiling"],
            footL=AX - 3.45, footR=AX + 2.75, flat_half=1.75, hbL=2.10, hbR=2.21)
LOFT_DECK = B["loft_deck"]; UNDERLOFT_CLG = B["underloft_ceiling"]
ROOF_RIDGE, ROOF_PITCH = 4.65 + 0.20, 13.0                        # ridge underside 4.65 (loft scan) + nominal roof build-up
EXT_L, EXT_R, EXT_G0, EXT_G1 = -0.45, 12.05, -0.25, Y_LIVE_G + 0.25
GROUND = -0.50                                                   # PHOTO-INFERRED grade

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = "METRIC"

COLS = {}
def col(name):
    if name not in COLS:
        c = bpy.data.collections.new(name); scene.collection.children.link(c); COLS[name] = c
    return COLS[name]

# ------------------------------------------------------------------ materials
def mat(name, rgb, rough=0.6, metal=0.0, emit=None, estr=0.0, alpha=1.0, transm=0.0, noise=None):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if emit: b.inputs["Emission Color"].default_value = (*emit, 1); b.inputs["Emission Strength"].default_value = estr
    if transm: b.inputs["Transmission Weight"].default_value = transm
    if alpha < 1: b.inputs["Alpha"].default_value = alpha
    if noise:   # subtle procedural variation (wood / concrete / plaster)
        tex = nt.nodes.new("ShaderNodeTexNoise"); tex.inputs["Scale"].default_value = noise[0]
        tex.inputs["Detail"].default_value = 8
        ramp = nt.nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].color = (*[c * (1 - noise[1]) for c in rgb], 1)
        ramp.color_ramp.elements[1].color = (*[min(1, c * (1 + noise[1])) for c in rgb], 1)
        nt.links.new(tex.outputs["Fac"], ramp.inputs["Fac"]); nt.links.new(ramp.outputs["Color"], b.inputs["Base Color"])
        if len(noise) > 2:  # stretched grain (wood)
            mp = nt.nodes.new("ShaderNodeMapping"); tc = nt.nodes.new("ShaderNodeTexCoord")
            mp.inputs["Scale"].default_value = noise[2]
            nt.links.new(tc.outputs["Object"], mp.inputs["Vector"]); nt.links.new(mp.outputs["Vector"], tex.inputs["Vector"])
    m.diffuse_color = (*rgb, 1)
    return m

M = {
 # existing
 "ex_wall": mat("ex_wall_painted_panel", (0.78, 0.74, 0.67), 0.85, noise=(18, 0.04)),
 "ex_floor_cr": mat("ex_floor_control", (0.45, 0.45, 0.44), 0.8, noise=(6, 0.08)),
 "ex_concrete": mat("ex_concrete_slab", (0.55, 0.54, 0.52), 0.9, noise=(3, 0.12)),
 "ex_post": mat("ex_timber_post", (0.50, 0.33, 0.20), 0.6, noise=(40, 0.15, (1, 1, 12))),
 "ex_joist": mat("ex_timber_joist", (0.62, 0.48, 0.32), 0.7, noise=(30, 0.15, (1, 12, 1))),
 "ex_foil": mat("ex_foil_insulation", (0.75, 0.75, 0.78), 0.35, metal=0.6),
 "ex_siding": mat("ex_siding_stained", (0.24, 0.16, 0.10), 0.75, noise=(25, 0.2, (12, 1, 1))),
 "ex_siding_live": mat("ex_siding_weathered", (0.38, 0.34, 0.30), 0.85, noise=(25, 0.2, (12, 1, 1))),
 "ex_roof": mat("ex_roof_metal", (0.62, 0.64, 0.66), 0.35, metal=0.7),
 "ex_ground": mat("ex_ground_grass", (0.18, 0.28, 0.10), 0.95, noise=(2, 0.25)),
 "ex_osb": mat("ex_osb_deck", (0.62, 0.50, 0.33), 0.8, noise=(60, 0.25)),
 "glass": mat("glass", (0.85, 0.92, 0.95), 0.02, transm=1.0),
 "door": mat("door_painted", (0.92, 0.92, 0.90), 0.4),
 "door_dark": mat("door_dark", (0.06, 0.06, 0.07), 0.4),
 "stove": mat("stove_black", (0.03, 0.03, 0.03), 0.5, metal=0.6),
 # equipment
 "walnut": mat("walnut", (0.17, 0.085, 0.04), 0.45, noise=(35, 0.2, (12, 1, 1))),
 "panel_black": mat("console_panel", (0.035, 0.037, 0.04), 0.5, metal=0.3),
 "meter_face": mat("vu_face", (0.92, 0.82, 0.55), 0.4, emit=(1.0, 0.82, 0.5), estr=0.6),
 "meter_bridge": mat("meter_bridge_brass", (0.62, 0.45, 0.18), 0.35, metal=0.6),
 "fader": mat("fader_white", (0.9, 0.9, 0.88), 0.3),
 "knob": mat("knob", (0.05, 0.05, 0.05), 0.35),
 "knob_red": mat("knob_red", (0.6, 0.05, 0.03), 0.35),
 "steel_black": mat("steel_black", (0.02, 0.02, 0.02), 0.4, metal=0.8),
 "spk_cab": mat("geithain_cabinet", (0.025, 0.025, 0.027), 0.55),
 "spk_cone": mat("geithain_cone", (0.012, 0.012, 0.012), 0.75),
 "spk_dome": mat("geithain_dome", (0.04, 0.04, 0.045), 0.3, metal=0.3),
 # proposed
 "oak": mat("pr_oak_floor", (0.66, 0.53, 0.38), 0.45, noise=(30, 0.15, (14, 1, 1))),
 "plaster": mat("pr_lime_plaster", (0.86, 0.84, 0.80), 0.95, noise=(12, 0.03)),
 "fabric": mat("pr_fabric_absorber", (0.42, 0.40, 0.37), 0.95, noise=(80, 0.05)),
 "fabric_dark": mat("pr_fabric_dark", (0.16, 0.16, 0.17), 0.95, noise=(80, 0.05)),
 "reclaimed": mat("pr_reclaimed_wood_clark", (0.45, 0.30, 0.18), 0.6, noise=(40, 0.25, (1, 1, 10))),
 "cove": mat("pr_cove_light", (1, 0.9, 0.75), 0.5, emit=(1.0, 0.86, 0.68), estr=25),
 "cove_cool": mat("pr_cove_light_cool", (0.85, 0.9, 1), 0.5, emit=(0.70, 0.80, 1.0), estr=12),
 "screen": mat("pr_ac_screen", (0.85, 0.85, 0.85), 0.9, emit=(0.55, 0.65, 0.85), estr=0.0),
 "sofa": mat("pr_sofa_wool", (0.35, 0.33, 0.30), 0.95, noise=(60, 0.05)),
 "rug": mat("pr_wool_rug", (0.30, 0.28, 0.25), 1.0, noise=(90, 0.08)),
 "spk_small": mat("pr_monitor_small", (0.03, 0.03, 0.035), 0.5),
 "machinery": mat("pr_machinery_placeholder", (0.62, 0.08, 0.05), 0.45, metal=0.2),
 "zone_paint": mat("pr_zone_paint_yellow", (0.85, 0.65, 0.05), 0.6),
 "piano": mat("pr_piano_black", (0.01, 0.01, 0.01), 0.12),
 "gobo": mat("pr_gobo_wood", (0.55, 0.40, 0.25), 0.6, noise=(40, 0.2, (1, 1, 10))),
 "steel": mat("pr_steel", (0.35, 0.35, 0.36), 0.35, metal=0.9),
 "pendant": mat("pr_pendant_glow", (1, 0.85, 0.6), 0.5, emit=(1.0, 0.82, 0.6), estr=40),
}

# ------------------------------------------------------------------ geometry helpers
def link(ob, c, ev=None, note=None):
    col(c).objects.link(ob)
    if ev: ob["evidence_class"] = ev
    if note: ob["note"] = note
    return ob

def box(name, x0, x1, y0, y1, z0, z1, m, c, ev=None, note=None, bevel=0.0):
    x0, x1 = sorted((x0, x1)); y0, y1 = sorted((y0, y1)); z0, z1 = sorted((z0, z1))
    v = [(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)]
    f = [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    me = bpy.data.meshes.new(name); me.from_pydata(v, [], f); me.update()
    ob = bpy.data.objects.new(name, me); ob.data.materials.append(M[m] if isinstance(m, str) else m)
    if bevel:
        bv = ob.modifiers.new("bevel", "BEVEL"); bv.width = bevel; bv.segments = 2
    return link(ob, c, ev, note)

def poly_prism(name, pts2d, axis, a0, a1, m, c, ev=None, note=None):
    """Extrude a 2-D polygon. axis='Y': pts are (x,z), extruded y a0..a1. axis='X': pts (y,z). axis='Z': pts (x,y)."""
    n = len(pts2d); v = []
    for a in (a0, a1):
        for p, q in pts2d:
            v.append({"Y": (p, a, q), "X": (a, p, q), "Z": (p, q, a)}[axis])
    f = [tuple(range(n))[::-1], tuple(range(n, 2*n))] + [(i, (i+1) % n, n + (i+1) % n, n + i) for i in range(n)]
    me = bpy.data.meshes.new(name); me.from_pydata(v, [], f); me.update(); me.validate()
    ob = bpy.data.objects.new(name, me); ob.data.materials.append(M[m] if isinstance(m, str) else m)
    return link(ob, c, ev, note)

def cyl(name, r, h, loc, m, c, rot=(0, 0, 0), verts=32, ev=None):
    me = bpy.data.meshes.new(name); import bmesh
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=verts, radius1=r, radius2=r, depth=h); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); ob.location = loc; ob.rotation_euler = rot
    ob.data.materials.append(M[m] if isinstance(m, str) else m); return link(ob, c, ev)

def cut(target, x0, x1, y0, y1, z0, z1, label):
    cutter = box(f"CUT_{label}", x0, x1, y0, y1, z0, z1, "glass", "19_CUTTERS")
    cutter.hide_render = True; cutter.display_type = "WIRE"
    mod = target.modifiers.new(f"open_{label}", "BOOLEAN"); mod.operation = "DIFFERENCE"; mod.object = cutter
    try: mod.solver = "EXACT"
    except Exception: pass
    return cutter

def opening(wall_ob, plane, a0, a1, z0, z1, label, kind, src):
    """Cut a real hole through a wall and fill it with glass (window) or a door leaf."""
    t = 0.6
    if plane == "Y0":   cut(wall_ob, a0, a1, -t, 0.05, z0, z1, label); fill = (a0, a1, -0.12, -0.08, z0, z1)
    elif plane == "YD": cut(wall_ob, a0, a1, D - 0.05, D + t, z0, z1, label); fill = (a0, a1, D + 0.06, D + 0.09, z0, z1)
    elif plane == "X0": cut(wall_ob, -t, 0.05, a0, a1, z0, z1, label); fill = (-0.12, -0.08, a0, a1, z0, z1)
    elif plane == "XW": cut(wall_ob, W - 0.05, W + t, a0, a1, z0, z1, label); fill = (W + 0.08, W + 0.12, a0, a1, z0, z1)
    elif plane == "LG": cut(wall_ob, a0, a1, Y_LIVE_G - 0.05, Y_LIVE_G + t, z0, z1, label); fill = (a0, a1, Y_LIVE_G + 0.08, Y_LIVE_G + 0.12, z0, z1)
    if kind != "void":
        ob = box(f"{kind.upper()}_{label}", *fill, "glass" if kind == "window" else ("door" if kind == "door" else "door_dark"),
                 "13_EXISTING_OPENINGS", "PHOTO-SOLVED/SCAN", src)
        if kind == "window": ob.visible_shadow = False

# ================================================================== EXISTING
EX = "11_EXISTING_SHELL"
T_EXT, T_PART = 0.20, 0.15   # nominal thicknesses (UNKNOWN - rendering only)
# control room floor + walls (solid slabs, outward thickness)
box("EX_CR_floor", 0, W, 0, D, -0.15, 0, "ex_floor_cr", EX, "SCAN-MEASURED")
wX0 = box("EX_CR_wall_X0", -T_EXT, 0, -T_EXT, D, 0, G["hloL"], "ex_wall", EX, "SCAN-MEASURED")
wXW = box("EX_CR_wall_XW", W, W + T_EXT, -T_EXT, D, 0, G["hloR"], "ex_wall", EX, "SCAN-MEASURED")
sec = G["section"]
wG = poly_prism("EX_CR_gable_wall", sec, "Y", -T_EXT, 0, "ex_wall", EX, "SCAN+PHOTO", "Building end wall")
wP = poly_prism("EX_CR_partition_wall", sec, "Y", D, D + T_PART, "ex_wall", EX, "SCAN+PHOTO", "Partition to middle zone; thickness UNKNOWN")
# ceiling: extruded section skin (thickness 0.05 upward)
ceil = G["ceil"]; skin = ceil + [(x, z + 0.05) for x, z in ceil[::-1]]
poly_prism("EX_CR_ceiling", skin, "Y", -T_EXT, D + T_PART, "ex_wall", EX, "SCAN+PHOTO", "Asymmetric tray ceiling")
for nm, x, hbb, hlo in (("L", G["xL"], G["hbbL"], G["hloL"]), ("R", G["xR"], G["hbbR"], G["hloR"])):
    box(f"EX_CR_beam_{nm}", x - 0.095, x + 0.095, 0, D, hbb, hlo, "ex_wall", EX, "PHOTO-SOLVED")
for nm, x, y, hbb in (("L", G["xL"], P["ypl"], G["hbbL"]), ("R", G["xR"], P["ypr"], G["hbbR"])):
    box(f"EX_CR_post_{nm}", x - 0.07, x + 0.07, y - 0.07, y + 0.07, 0, hbb, "ex_post", EX, "PHOTO-SOLVED", "section photo-inferred")
# openings (G1-01): real cuts
S_ = lambda k: P[k]
opening(wG, "Y0", min(S_("CR3.xe1"), S_("CR3.xe2")), max(S_("CR3.xe1"), S_("CR3.xe2")), 0, S_("CR3.he"), "gable_entry_door", "door_dark", "CR3 photo solve")
opening(wG, "Y0", min(S_("CR3.xw1"), S_("CR3.xw2")), max(S_("CR3.xw1"), S_("CR3.xw2")), S_("CR3.hwb"), S_("CR3.hwt"), "gable_clerestory", "window", "CR3 photo solve")
opening(wG, "Y0", min(S_("g_xi1"), S_("g_xi2")), max(S_("g_xi1"), S_("g_xi2")), 0, S_("g_hi"), "gable_interior_door", "door", "CR3 photo solve")
opening(wG, "Y0", min(S_("CR3.gw1a"), S_("CR3.gw1b")), max(S_("CR3.gw1a"), S_("CR3.gw1b")), S_("CR3.gw1s"), S_("CR3.gw1h"), "gable_window_E", "window", "CR3 photo solve (scan disagrees: ledger X8)")
opening(wG, "Y0", min(S_("CR3.gw2a"), S_("CR3.gw2b")), max(S_("CR3.gw2a"), S_("CR3.gw2b")), S_("CR3.gw2s"), S_("CR3.gw2h"), "gable_window_W", "window", "CR3 photo solve")
opening(wP, "YD", S_("CR1.xd1"), S_("CR1.xd2"), 0, S_("CR1.hd"), "partition_doorway", "void", "CR1/CR2 photo solve")
SILL, HEAD = S_("CR1.wsill"), S_("CR1.wh")
for i, (a, b) in enumerate(((1.15, 4.35), (4.50, 7.95))):
    opening(wXW, "XW", a, b, SILL, HEAD, f"right_window_{i+1}", "window", "extent: scan reveals; sill/head: CR1 photo")
for i, (a, b) in enumerate(((1.95, 2.90), (4.45, 8.05))):
    opening(wX0, "X0", a, b, SILL, HEAD, f"left_window_{i+1}", "window", "extent: scan reveals; sill/head assumed = right side (PHOTO-INFERRED)")
# stove + flue (G1-07) - existing appliance; clearances to be confirmed
xs, ys = S_("g_xs"), min(S_("g_ys"), D - 0.35)
box("EX_wood_stove", xs - 0.28, xs + 0.28, ys - 0.25, ys + 0.25, 0, S_("CR1.hs"), "stove", "12_EXISTING_SERVICES", "PHOTO-SOLVED", "existing wood stove; position Y sigma ~0.3 m")
cyl("EX_stove_flue", 0.075, S_("CR1.hfl") - S_("CR1.hs"), (xs, ys + 0.1, (S_("CR1.hfl") + S_("CR1.hs")) / 2), "stove", "12_EXISTING_SERVICES", ev="PHOTO-SOLVED")
box("EX_stove_flue_to_partition", xs - 0.075, xs + 0.075, ys + 0.1, D + T_PART, S_("CR1.hfl") - 0.15, S_("CR1.hfl"), "stove", "12_EXISTING_SERVICES", "PHOTO-INFERRED", "route beyond partition UNKNOWN")

# middle zone (scan plan slice, approximate partitions)
MZ = "14_EXISTING_MIDDLE_ZONE"
box("EX_MZ_floor", 0, W, Y_PART1, Y_MID1, F_MID - 0.15, F_MID, "ex_concrete", MZ, "SCAN-MEASURED")
mz_clg = F_MID + 2.54
box("EX_MZ_ceiling", -T_EXT, W + T_EXT, Y_PART1, Y_MID1, mz_clg, mz_clg + 0.05, "ex_wall", MZ, "SCAN-MEASURED")
corr0, corr1 = AX - 0.70, AX + 0.70
for nm, x in (("corr_wall_L", corr0), ("corr_wall_R", corr1)):
    w_ = box(f"EX_MZ_{nm}", x - 0.06, x + 0.06, Y_PART1, Y_MID1, F_MID, mz_clg, "ex_wall", MZ, "SCAN-INFERRED", "approximate")
    for k, (a, b) in enumerate(((Y_PART1 + 1.2, Y_PART1 + 2.1), (Y_MID1 - 2.6, Y_MID1 - 1.7))):
        cut(w_, x - 0.2, x + 0.2, a, b, F_MID, F_MID + 2.0, f"{nm}_door{k}")
for nm, x0_, x1_, y in (("cross_L", 0, corr0, Y_PART1 + 4.55), ("cross_R1", corr1, W, Y_PART1 + 2.05), ("cross_R2", corr1, W, Y_PART1 + 5.75)):
    box(f"EX_MZ_{nm}", x0_, x1_, y - 0.06, y + 0.06, F_MID, mz_clg, "ex_wall", MZ, "SCAN-INFERRED", "approximate partition")
box("EX_MZ_end_wall_L", 0, corr0, Y_MID1 - 0.06, Y_MID1 + 0.06, F_MID, mz_clg, "ex_wall", MZ, "SCAN-INFERRED")
box("EX_MZ_end_wall_R", corr1, W, Y_MID1 - 0.06, Y_MID1 + 0.06, F_MID, mz_clg, "ex_wall", MZ, "SCAN-INFERRED")
for side, x0_, x1_ in (("L", -T_EXT, 0), ("R", W, W + T_EXT)):
    box(f"EX_MZ_extwall_{side}", x0_, x1_, Y_PART1, Y_MID1, F_MID, mz_clg, "ex_wall", MZ, "SCAN-INFERRED")

# live room
LV = "15_EXISTING_LIVE_ROOM"
box("EX_LV_slab", LIVE_L, LIVE_R, Y_MID1, Y_LIVE_G, F_LIVE - 0.2, F_LIVE, "ex_concrete", LV, "SCAN-MEASURED")
lw_l = box("EX_LV_wall_L", LIVE_L - T_EXT, LIVE_L, Y_MID1, Y_LIVE_G, F_LIVE, LIVE["hlo_l"], "ex_wall", LV, "SCAN-MEASURED")
lw_r = box("EX_LV_wall_R", LIVE_R, LIVE_R + T_EXT, Y_MID1, Y_LIVE_G, F_LIVE, LIVE["hlo_r"], "ex_wall", LV, "SCAN-MEASURED")
for k, y0_ in enumerate((Y_MID1 + 1.5, Y_MID1 + 5.0, Y_LOFT_END + 1.5, Y_LOFT_END + 5.0)):   # PHOTO-INFERRED window rhythm
    for w_, x_, pl in ((lw_l, LIVE_L, "L"), (lw_r, LIVE_R, "R")):
        cut(w_, x_ - 0.5, x_ + 0.5, y0_, y0_ + 1.4, F_LIVE + 1.25, F_LIVE + 1.95, f"live_win_{pl}{k}")
        box(f"WINDOW_live_{pl}{k}", x_ - 0.12 if pl == "L" else x_ + 0.08, x_ - 0.08 if pl == "L" else x_ + 0.12, y0_, y0_ + 1.4,
            F_LIVE + 1.25, F_LIVE + 1.95, "glass", "13_EXISTING_OPENINGS", "PHOTO-INFERRED", "window positions approximate (photos), not yet scan-measured")
lsec = [(LIVE_L, F_LIVE), (LIVE_R, F_LIVE), (LIVE_R, LIVE["hlo_r"]), (LIVE["footR"], LIVE["hlo_r"]), (LIVE["footR"], LIVE["hbR"] + 0.1),
        (AX + LIVE["flat_half"], LIVE["hc"]), (AX - LIVE["flat_half"], LIVE["hc"]), (LIVE["footL"], LIVE["hbL"] + 0.1),
        (LIVE["footL"], LIVE["hlo_l"]), (LIVE_L, LIVE["hlo_l"])]
lg = poly_prism("EX_LV_gable_wall", lsec, "Y", Y_LIVE_G, Y_LIVE_G + T_EXT, "ex_wall", LV, "SCAN-MEASURED")
GD_W, GD_H = 3.70, 3.40      # PHOTO-INFERRED overhead garage door (to tape)
opening(lg, "LG", AX - GD_W/2, AX + GD_W/2, F_LIVE, F_LIVE + GD_H, "garage_door", "void", "PHOTO-INFERRED size; position on axis from photos")
box("EX_LV_garage_door_panel_raised", AX - GD_W/2, AX + GD_W/2, Y_LIVE_G - 1.2, Y_LIVE_G - 0.2, F_LIVE + GD_H + 0.05, F_LIVE + GD_H + 0.10, "door", LV, "PHOTO-INFERRED", "overhead door shown open")
lceil = lsec[2:]; lskin = lceil + [(x, z + 0.05) for x, z in lceil[::-1]]
poly_prism("EX_LV_tray_ceiling", lskin, "Y", Y_LOFT_END, Y_LIVE_G + T_EXT, "ex_wall", LV, "SCAN-MEASURED")
# end face between tray zone and under-loft zone, with the loft overlook opening
endface = poly_prism("EX_LV_loft_end_face", [(LIVE_L, UNDERLOFT_CLG), (LIVE_R, UNDERLOFT_CLG)] + lsec[2:][1:-1] + [], "Y", Y_LOFT_END - 0.12, Y_LOFT_END, "ex_wall", LV, "SCAN-MEASURED")
cut(endface, AX - 0.9, AX + 0.9, Y_LOFT_END - 0.5, Y_LOFT_END + 0.3, LOFT_DECK + 0.05, LOFT_DECK + 1.0, "loft_overlook")
# under-loft zone: joists + foil insulation (existing), posts
box("EX_LV_underloft_foil", LIVE_L, LIVE_R, Y_MID1, Y_LOFT_END, UNDERLOFT_CLG + 0.20, UNDERLOFT_CLG + 0.22, "ex_foil", LV, "PHOTO-OBSERVED")
y = Y_MID1 + 0.2
while y < Y_LOFT_END:
    box(f"EX_LV_joist_{y:.1f}", LIVE_L, LIVE_R, y, y + 0.05, UNDERLOFT_CLG, UNDERLOFT_CLG + 0.20, "ex_joist", LV, "PHOTO-OBSERVED", "spacing photo-inferred 0.6 m")
    y += 0.6
for k, (x, yy) in enumerate(((AX - 2.6, Y_MID1 + 2.3), (AX + 2.6, Y_MID1 + 2.3), (AX - 2.6, Y_LOFT_END - 0.4), (AX + 2.6, Y_LOFT_END - 0.4), (AX, Y_LOFT_END - 0.4))):
    box(f"EX_LV_post_{k}", x - 0.09, x + 0.09, yy - 0.09, yy + 0.09, F_LIVE, UNDERLOFT_CLG, "ex_post", LV, "PHOTO-INFERRED", "post positions from photos; tape needed")
box("EX_LV_beam_loft_edge", LIVE_L, LIVE_R, Y_LOFT_END - 0.5, Y_LOFT_END - 0.3, UNDERLOFT_CLG - 0.25, UNDERLOFT_CLG, "ex_post", LV, "PHOTO-INFERRED")
# loft deck (roof-space attic)
LF = "16_EXISTING_LOFT"
box("EX_LOFT_deck", AX - 2.6, AX + 2.6, Y_PART1, Y_LOFT_END, LOFT_DECK - 0.03, LOFT_DECK, "ex_osb", LF, "SCAN-MEASURED", "deck 2.79 m above live floor; headroom >=2.1 m only ~2 m wide strip")

# roof + exterior envelope (continuous, one pitch) - EXTERIOR geometry partly PHOTO-INFERRED
ENV = "17_EXISTING_ENVELOPE"
t13 = math.tan(math.radians(ROOF_PITCH))
eave_z = ROOF_RIDGE - t13 * (AX - EXT_L + 0.4)
roof_pts = [(EXT_L - 0.4, eave_z), (AX, ROOF_RIDGE), (EXT_R + 0.4, ROOF_RIDGE - t13 * (EXT_R + 0.4 - AX)),
            (EXT_R + 0.4, ROOF_RIDGE - t13 * (EXT_R + 0.4 - AX) + 0.08), (AX, ROOF_RIDGE + 0.08), (EXT_L - 0.4, eave_z + 0.08)]
roof = poly_prism("EX_roof_metal", roof_pts, "Y", EXT_G0 - 0.35, EXT_G1 + 0.35, "ex_roof", ENV, "SCAN(loft pitch)+PHOTO", "continuous single-pitch gable roof; pitch from loft scan ~13 deg")
roof["visible_in_interiors"] = False
wall_top_L = ROOF_RIDGE - t13 * (AX - EXT_L)
wall_top_R = ROOF_RIDGE - t13 * (EXT_R - AX)
for nm, x0_, x1_, top in (("L", EXT_L, EXT_L + 0.04, wall_top_L), ("R", EXT_R - 0.04, EXT_R, wall_top_R)):
    s = box(f"EX_siding_long_{nm}", x0_, x1_, EXT_G0, EXT_G1, GROUND, top, "ex_siding", ENV, "PHOTO-OBSERVED")
gab = [(EXT_L, GROUND), (EXT_R, GROUND), (EXT_R, wall_top_R), (AX, ROOF_RIDGE), (EXT_L, wall_top_L)]
gs_c = poly_prism("EX_siding_gable_control", gab, "Y", EXT_G0 - 0.04, EXT_G0, "ex_siding", ENV, "PHOTO-OBSERVED")
gs_l = poly_prism("EX_siding_gable_live", gab, "Y", EXT_G1, EXT_G1 + 0.04, "ex_siding_live", ENV, "PHOTO-OBSERVED")
# exterior cuts matching openings
for o in [o for o in bpy.data.objects if o.name.startswith(("WINDOW_", "DOOR_"))]:
    bb = [o.matrix_world @ Vector(c) for c in o.bound_box]; xs_ = [v.x for v in bb]; ys_ = [v.y for v in bb]; zs_ = [v.z for v in bb]
    for tgt in (bpy.data.objects["EX_siding_long_L"], bpy.data.objects["EX_siding_long_R"], gs_c, gs_l):
        tb = [tgt.matrix_world @ Vector(c) for c in tgt.bound_box]
        if min(xs_) - 0.8 < max(v.x for v in tb) and max(xs_) + 0.8 > min(v.x for v in tb) and min(ys_) - 0.8 < max(v.y for v in tb) and max(ys_) + 0.8 > min(v.y for v in tb):
            cut(tgt, min(xs_) - 0.5 if tgt.name.startswith("EX_siding_long") else min(xs_), max(xs_) + 0.5 if tgt.name.startswith("EX_siding_long") else max(xs_),
                min(ys_) - (0 if tgt.name.startswith("EX_siding_long") else 0.6), max(ys_) + (0 if tgt.name.startswith("EX_siding_long") else 0.6), min(zs_), max(zs_), f"ext_{o.name}_{tgt.name[-1]}")
cut(gs_c, min(S_("CR3.xe1"), S_("CR3.xe2")), max(S_("CR3.xe1"), S_("CR3.xe2")), EXT_G0 - 0.6, EXT_G0 + 0.6, 0, S_("CR3.he"), "ext_entry")
cut(gs_l, AX - GD_W/2, AX + GD_W/2, EXT_G1 - 0.6, EXT_G1 + 0.6, F_LIVE, F_LIVE + GD_H, "ext_garage")
g = box("EX_ground", -25, 40, -25, 60, GROUND - 0.05, GROUND, "ex_ground", ENV, "INDICATIVE")
cut(g, EXT_L, EXT_R, EXT_G0, EXT_G1, GROUND - 0.1, GROUND + 0.1, "footprint")

# ================================================================== EQUIPMENT (actual gear)
EQ = "21_EQUIPMENT_ACTUAL"
IN = 0.0254
st = MG["stereo"]; C_ = MG["inputs"]["console_tape"]; R9 = MG["inputs"]["rl901k_tape"]

def console(x_c, y_front, facing=+1):
    """Spectra Sonics legacy console: tape W 62.4" D 47" H 31" front / 41" top (owner, 2026-11-08); detail from photo."""
    w, d, hf, ht = C_["width"], C_["depth"], C_["h_front"], C_["h_top"]
    x0, x1 = x_c - w/2, x_c + w/2; y0 = y_front; y1 = y_front + d * facing
    rail_d = 0.20; bridge_d = 0.16
    obs = []
    # walnut armrest rail (front), side cheeks, meter-bridge housing
    obs.append(box("SpectraSonics_armrest", x0, x1, y0, y0 + rail_d*facing, hf - 0.07, hf, "walnut", EQ, "TAPE+PHOTO", bevel=0.01))
    side = [(0, 0.66), (rail_d, hf), (d - bridge_d, ht - 0.04), (d, ht), (d, 0.66)]
    for nm, xa in (("L", x0), ("R", x1 - 0.035)):
        obs.append(poly_prism(f"SpectraSonics_cheek_{nm}", [(y0 + a*facing, z) for a, z in side], "X", xa, xa + 0.035, "walnut", EQ, "TAPE+PHOTO"))
    # sloped control surface (black panels)
    zf, zb = hf - 0.02, ht - 0.13
    surf = [(y0 + rail_d*facing, zf - 0.03), (y0 + (d - bridge_d)*facing, zb - 0.03), (y0 + (d - bridge_d)*facing, zb), (y0 + rail_d*facing, zf)]
    obs.append(poly_prism("SpectraSonics_surface", surf, "X", x0 + 0.035, x1 - 0.035, "panel_black", EQ, "TAPE+PHOTO"))
    # meter bridge: brass/wood strip with 12 VU meters (photo)
    obs.append(box("SpectraSonics_meter_bridge", x0 + 0.035, x1 - 0.035, y0 + (d - bridge_d)*facing, y1, ht - 0.13, ht, "meter_bridge", EQ, "TAPE+PHOTO"))
    mw = 0.085; n = 12; span = (x1 - x0) - 0.25
    for i in range(n):
        xm = x0 + 0.12 + (i + 0.5) * span / n + (0.04 if i >= 8 else 0)
        obs.append(box(f"SpectraSonics_VU_{i:02d}", xm - mw/2, xm + mw/2, y0 + (d - bridge_d - 0.005)*facing, y0 + (d - bridge_d + 0.01)*facing, ht - 0.105, ht - 0.035, "meter_face", EQ, "PHOTO"))
    # 16 channel strips (2 banks of 8) + master: faders and knob grid on the slope
    def on_slope(frac):  # 0 = front, 1 = back
        yy = y0 + (rail_d + frac * (d - bridge_d - rail_d)) * facing; zz = zf + frac * (zb - zf); return yy, zz
    strip_w = 0.034; bank_x = [x0 + 0.08, x0 + 0.08 + 8*strip_w + 0.03]
    for b, bx in enumerate(bank_x):
        for s in range(8):
            xx = bx + (s + 0.5) * strip_w
            yy, zz = on_slope(0.10); obs.append(box(f"SS_fader_{b}{s}", xx - 0.008, xx + 0.008, yy - 0.012, yy + 0.012, zz, zz + 0.022, "fader", EQ, "PHOTO"))
            for k in range(8):
                yy, zz = on_slope(0.30 + 0.085 * k)
                obs.append(cyl(f"SS_knob_{b}{s}{k}", 0.0075, 0.018, (xx, yy, zz + 0.009), "knob_red" if k in (2, 5) and s % 3 == 0 else "knob", EQ, verts=10))
    for s in range(6):   # master section (right of centre) - simplified
        xx = x0 + 0.08 + 16*strip_w + 0.25 + 0.15 + s * 0.04
        for k in range(6):
            yy, zz = on_slope(0.25 + 0.1 * k); obs.append(cyl(f"SS_mknob_{s}{k}", 0.008, 0.018, (xx, yy, zz + 0.009), "knob", EQ, verts=10))
    yy, zz = on_slope(0.5)
    obs.append(box("SpectraSonics_patch_well", x1 - 0.36, x1 - 0.06, yy - 0.18, yy + 0.18, zz - 0.06, zz + 0.002, "steel_black", EQ, "PHOTO", "TT patchbay well (right)"))
    # T-legs (black steel) - photo
    for nm, xa in (("L", x0 + 0.18), ("R", x1 - 0.18)):
        obs.append(box(f"SpectraSonics_leg_{nm}", xa - 0.03, xa + 0.03, y0 + 0.25*facing, y0 + 0.30*facing, 0, 0.66, "steel_black", EQ, "PHOTO"))
        obs.append(box(f"SpectraSonics_foot_{nm}", xa - 0.035, xa + 0.035, y0 + 0.02*facing, y0 + (d - 0.05)*facing, 0, 0.05, "steel_black", EQ, "PHOTO"))
    obs.append(box("SpectraSonics_body_under", x0 + 0.035, x1 - 0.035, y0 + rail_d*facing, y1, 0.62, 0.70, "walnut", EQ, "PHOTO"))
    for o in obs: o["equipment"] = "Spectra Sonics console (actual, Breakglass Sunny Suite)"
    return obs

def rl901k(name, x, y, yaw_deg, top=R9["top_on_stand"]):
    """Musikelectronic Geithain RL 901K on its steel stand (owner tape + manufacturer data)."""
    w, dd, h = R9["width"], R9["depth"], R9["height"]; zb = top - h
    parts = []
    parts.append(box(f"{name}_cabinet", -w/2, w/2, 0, dd, zb, top, "spk_cab", EQ, "TAPE+MANUFACTURER", bevel=0.008))
    ring = cyl(f"{name}_woofer_400", 0.20, 0.02, (0, -0.006, zb + h/2), "spk_cone", EQ, rot=(math.pi/2, 0, 0), verts=48)
    parts.append(ring)
    parts.append(cyl(f"{name}_coax_bar", 0.03, 0.30, (0, -0.02, zb + h/2), "spk_dome", EQ, rot=(0, math.pi/2, 0), verts=12))
    parts.append(cyl(f"{name}_mid_130", 0.065, 0.025, (0.0, -0.03, zb + h/2), "spk_dome", EQ, rot=(math.pi/2, 0, 0), verts=32))
    parts.append(cyl(f"{name}_tweeter_25", 0.02, 0.02, (-0.10, -0.03, zb + h/2), "spk_dome", EQ, rot=(math.pi/2, 0, 0), verts=16))
    # stand: two uprights, shelf, base (photo)
    for sx in (-w/2 + 0.03, w/2 - 0.03):
        parts.append(box(f"{name}_stand_up", sx - 0.015, sx + 0.015, dd/2 - 0.015, dd/2 + 0.015, 0.02, zb, "steel_black", EQ, "PHOTO"))
    parts.append(box(f"{name}_stand_shelf", -w/2 + 0.01, w/2 - 0.01, 0.05, dd - 0.05, zb - 0.32, zb - 0.30, "steel_black", EQ, "PHOTO"))
    parts.append(box(f"{name}_stand_base", -w/2, w/2, -0.02, dd + 0.02, 0, 0.02, "steel_black", EQ, "PHOTO"))
    empty = bpy.data.objects.new(name, None); col(EQ).objects.link(empty)
    for p in parts:
        p.parent = empty; p["equipment"] = "Geithain RL 901K (actual)"
    empty.location = (x, y, 0); empty.rotation_euler = (0, 0, math.radians(yaw_deg))
    return empty

# placement (monitoring_geometry.json): console faces +Y (partition); speakers face the listener, toed in
LPx, LPy, _ = st["listening_position"]
console(AX, st["console"]["front_edge_y"], +1)
for nm, (x, y, z) in (("RL901K_L", st["L"]), ("RL901K_R", st["R"])):
    # local front normal is -Y; rotating by yaw maps it to (sin yaw, -cos yaw). Solve so it points at the LP.
    dx, dy = LPx - x, LPy - y; yaw = math.degrees(math.atan2(dx, -dy))
    e = rl901k(nm, x, y, yaw)
    fwd = (math.sin(math.radians(yaw)), -math.cos(math.radians(yaw)))
    assert fwd[0]*dx + fwd[1]*dy > 0.99 * math.hypot(dx, dy), f"{nm} not facing the listening position"
    e["toe_in_deg"] = round(abs(yaw), 1); e["faces"] = "listening position (verified by assertion)"
# Clark timber rack wings (photo-inferred size) angled at console ends
for nm, sgn in (("L", -1), ("R", 1)):
    e = bpy.data.objects.new(f"ClarkRackWing_{nm}", None); col(EQ).objects.link(e)
    b_ = box(f"ClarkRackWing_{nm}_body", -0.33, 0.33, -0.30, 0.30, 0, 0.82, "walnut", EQ, "PHOTO-INFERRED", "Clark outboard rack wing; size to tape")
    f_ = box(f"ClarkRackWing_{nm}_racks", -0.24, 0.24, -0.31, -0.30, 0.30, 0.78, "panel_black", EQ, "PHOTO-INFERRED")
    b_.parent = e; f_.parent = e
    e.location = (AX + sgn * (C_["width"]/2 + 0.42), st["console"]["front_edge_y"] + 0.15, 0); e.rotation_euler = (0, 0, math.radians(-sgn * 35))

# ================================================================== PROPOSED — CONTROL ROOM "Quiet Light"
PR = "31_PROPOSED_CONTROL_ROOM"
box("PR_CR_oak_floor", 0.02, W - 0.02, 0.02, D - 0.02, 0.0, 0.012, "oak", PR, "PROPOSED")
box("PR_CR_rug_mixpos", LPx - 2.0, LPx + 2.0, LPy - 2.6, LPy + 1.8, 0.012, 0.022, "rug", PR, "PROPOSED")
# front wall: full-width deep broadband absorber (fabric), doorway kept open
fw_y = D - 0.30
STOVE_X0 = S_("g_xs") - 0.28 - 0.90   # keep ~0.9 m clear of the existing wood stove (clearances per its label / WETT)
for nm, a, b in (("L", 0.0, STOVE_X0), ("R", S_("CR1.xd2") + 0.05, W)):
    box(f"PR_front_absorber_{nm}", a, b, fw_y, D - 0.01, 0.0, 2.15, "fabric_dark", PR, "PROPOSED", "~300 mm broadband absorber, front wall; depth/spec by acoustician")
box("PR_front_absorber_header", S_("CR1.xd1") - 0.05, S_("CR1.xd2") + 0.05, fw_y, D - 0.01, S_("CR1.hd") + 0.05, 2.15, "fabric_dark", PR, "PROPOSED")
# side low zones: LF traps BELOW the sills (windows preserved), reclaimed-wood capped
for nm, x0_, x1_ in (("L", 0.0, 0.75), ("R", W - 0.75, W)):
    box(f"PR_bass_trap_{nm}", x0_, x1_, 0.6, D - 0.35, 0.0, SILL - 0.05, "fabric", PR, "PROPOSED", "LF trap under windows (~0.75 m deep); sizes by acoustician")
    box(f"PR_bass_trap_cap_{nm}", x0_, x1_, 0.6, D - 0.35, SILL - 0.05, SILL - 0.01, "reclaimed", PR, "PROPOSED", "reclaimed Clark wood cap = window bench")
# ceiling: absorptive cloud on the flat ceiling over the mix position (first-reflection zone)
box("PR_ceiling_cloud", AX - 1.55, AX + 1.55, LPy - 0.6, st["L"][1] - 0.2, G["hc"] - 0.22, G["hc"] - 0.12, "fabric", PR, "PROPOSED", "suspended absorber; height/area by reflection analysis")
# rear wall (gable): reclaimed-wood diffusion between the existing openings
import random; random.seed(7)
spans = [(0.3, min(S_("CR3.gw2a"), S_("CR3.gw2b")) - 0.1), (max(S_("CR3.gw2a"), S_("CR3.gw2b")) + 0.1, min(S_("CR3.xe1"), S_("CR3.xe2")) - 0.15),
         (max(S_("CR3.xe1"), S_("CR3.xe2")) + 0.15, min(S_("g_xi1"), S_("g_xi2")) - 0.15)]
for si, (a, b) in enumerate(spans):
    x = a
    while x + 0.09 < b:
        d_ = random.choice((0.04, 0.08, 0.12, 0.16, 0.20, 0.12, 0.06))
        box(f"PR_rear_diffuser_{si}_{x:.2f}", x, x + 0.085, 0.0, d_, 0.45, 2.25, "reclaimed", PR, "PROPOSED", "QRD-style slat diffuser from reclaimed Clark wood")
        x += 0.095
# Quiet Light: concealed cove lighting along the beam lines washing the sloped planes and flat ceiling
for nm, x, z in (("L", G["xL"] + 0.12, G["hbL"] + 0.02), ("R", G["xR"] - 0.12, G["hbR"] + 0.02)):
    box(f"PR_cove_{nm}", x - 0.03, x + 0.03, 0.15, D - 0.15, z, z + 0.02, "cove", PR, "PROPOSED", "dimmable tunable-white LED cove (Turrell-like wash)")
box("PR_cove_flat_perimeter", AX - G["wc"]/2 + 0.05, AX + G["wc"]/2 - 0.05, D - 0.45, D - 0.43, G["hc"] - 0.03, G["hc"] - 0.01, "cove_cool", PR, "PROPOSED")
# producer desk + rear sofa (client listening / screening row)
CIN = MG["cinema"]
box("PR_producer_desk", 0.85, 1.55, 1.70, 3.90, 0.70, 0.74, "reclaimed", PR, "PROPOSED", "producer/outboard desk along the left wall (under the window line); racks below")
box("PR_producer_desk_racks", 0.90, 1.50, 1.75, 3.85, 0.05, 0.70, "panel_black", PR, "PROPOSED")
SOFA_Y0 = 0.30   # against the rear diffusers: family cinema row (eyes ~1.3 m from the gable)
box("PR_sofa", AX - 1.4, AX + 1.4, SOFA_Y0, SOFA_Y0 + 0.95, 0.0, 0.45, "sofa", PR, "PROPOSED", "family cinema sofa (3-4 seats)")
box("PR_sofa_back", AX - 1.4, AX + 1.4, SOFA_Y0, SOFA_Y0 + 0.22, 0.45, 0.85, "sofa", PR, "PROPOSED")
for nm, x in (("L", AX - 1.4), ("R", AX + 1.25)):
    box(f"PR_sofa_arm_{nm}", x, x + 0.15, SOFA_Y0, SOFA_Y0 + 0.95, 0.45, 0.65, "sofa", PR, "PROPOSED")
for nm, x in (("L", AX - 2.75), ("R", AX + 2.75)):   # extra cinema seats beside the sofa
    box(f"PR_cinema_chair_{nm}", x - 0.40, x + 0.40, 1.05, 1.85, 0.0, 0.42, "sofa", PR, "PROPOSED")
    box(f"PR_cinema_chair_{nm}_back", x - 0.40, x + 0.40, 1.05, 1.25, 0.42, 0.85, "sofa", PR, "PROPOSED")
# fireside lounge around the EXISTING wood stove (kept by owner), behind the speakers
LOUNGE_Y = (st["L"][1] + D) / 2
box("PR_lounge_rug", S_("g_xs") - 2.0, S_("g_xs") + 0.6, st["L"][1] + 0.55, D - 0.75, 0.012, 0.022, "rug", PR, "PROPOSED", "fireside lounge (low, soft furniture below ~1 m)")
box("PR_hearth_pad", S_("g_xs") - 0.65, S_("g_xs") + 0.65, ys - 0.85, D - 0.02, 0.012, 0.03, "ex_concrete", PR, "PROPOSED", "non-combustible hearth pad (size per stove label / WETT)")
for k, (dx, dy, r) in enumerate(((-1.45, -0.45, -90), (-1.25, -1.45, -55))):   # left of the stove: doorway route stays clear
    e = bpy.data.objects.new(f"PR_lounge_chair_{k}", None); col(PR).objects.link(e)
    for o in (box(f"PR_lounge_chair_{k}_seat", -0.42, 0.42, -0.40, 0.40, 0.0, 0.40, "sofa", PR, "PROPOSED"),
              box(f"PR_lounge_chair_{k}_back", -0.42, 0.42, -0.40, -0.20, 0.40, 0.80, "sofa", PR, "PROPOSED")):
        o.parent = e
    e.location = (S_("g_xs") + dx, ys + dy, 0); e.rotation_euler = (0, 0, math.radians(180 + r))
box("PR_lounge_table", S_("g_xs") - 1.05, S_("g_xs") - 0.55, ys - 1.25, ys - 0.70, 0.0, 0.38, "reclaimed", PR, "PROPOSED")
# mix chair
box("PR_mix_chair_seat", LPx - 0.28, LPx + 0.28, LPy - 0.30, LPy + 0.22, 0.45, 0.55, "fabric_dark", PR, "PROPOSED")
box("PR_mix_chair_back", LPx - 0.25, LPx + 0.25, LPy - 0.36, LPy - 0.30, 0.55, 1.05, "fabric_dark", PR, "PROPOSED")
# immersive 7.1.4 (compact monitors, model TBD) + 2 subs, screen, projector
IM = MG["immersive_7_1_4"]
for k in ("C", "Ls", "Rs", "Lrs", "Rrs", "Ltf", "Rtf", "Ltr", "Rtr"):
    x, y, z = IM[k]
    yaw = math.atan2(LPx - x, LPy - y)
    e = bpy.data.objects.new(f"PR_imm_{k}", None); col(PR).objects.link(e)
    b_ = box(f"PR_imm_{k}_cab", -0.14, 0.14, -0.12, 0.12, -0.20, 0.20, "spk_small", PR, "PROPOSED", "compact coaxial monitor, model TBD (e.g. smaller Geithain family)")
    d_ = cyl(f"PR_imm_{k}_driver", 0.09, 0.01, (0, 0.121, 0.02), "spk_cone", PR, rot=(math.pi/2, 0, 0), verts=24)
    b_.parent = e; d_.parent = e; e.location = (x, y, z); e.rotation_euler = (0, 0, -yaw) if z < 2 else (-math.radians(35) * (1 if y > LPy else -1), 0, -yaw)
    if z < 2.0:
        box(f"PR_imm_{k}_stand", x - 0.12, x + 0.12, y - 0.12, y + 0.12, 0, z - 0.2, "steel_black", PR, "PROPOSED")
    else:
        box(f"PR_imm_{k}_hanger", x - 0.01, x + 0.01, y - 0.01, y + 0.01, z + 0.2, G["hc"], "steel_black", PR, "PROPOSED")
for nm, x in (("L", AX - 2.15), ("R", AX + 2.15)):
    box(f"PR_sub_{nm}", x - 0.30, x + 0.30, st["L"][1] + 0.15, st["L"][1] + 0.75, 0, 0.62, "spk_small", PR, "PROPOSED", "subwoofer (LFE/bass management) position for acoustician to optimise")
SCR_Y, SCR_W = CIN["screen_y"], CIN["screen_width"]
scr = box("PR_screen_down", AX - SCR_W/2, AX + SCR_W/2, SCR_Y, SCR_Y + 0.02, CIN["screen_bottom_z"], CIN["screen_bottom_z"] + CIN["screen_height"], "screen", "32_PROPOSED_SCREEN_MODE", "PROPOSED",
          "motorised acoustically-transparent 16:9 screen 3.0 m; drops in front of the Geithains for family film nights, retracts into the flat ceiling")
box("PR_screen_cassette", AX - SCR_W/2 - 0.1, AX + SCR_W/2 + 0.1, SCR_Y - 0.08, SCR_Y + 0.10, G["hc"] - 0.16, G["hc"] - 0.02, "steel_black", PR, "PROPOSED")
box("PR_projector", AX - 0.25, AX + 0.25, 0.70, 1.20, G["hc"] - 0.40, G["hc"] - 0.22, "steel_black", PR, "PROPOSED", "projector in hush-box on the flat ceiling above the sofa; throw ~4.3 m")
# HVAC (indicative): linear slot supplies at the slope/flat junction, low return at rear
for nm, x in (("L", AX - G["wc"]/2 - 0.25), ("R", AX + G["wc"]/2 + 0.25)):
    box(f"PR_hvac_slot_{nm}", x - 0.04, x + 0.04, 0.8, D - 0.8, G["hc"] - 0.12, G["hc"] - 0.08, "steel_black", PR, "PROPOSED", "low-velocity linear supply fed from roof void; design by mechanical engineer")

# ================================================================== PROPOSED — MIDDLE ZONE / LIVE ROOM "Farm Industrial"
PM = "33_PROPOSED_SUPPORT_ROOMS"
for k in range(3):   # machine room racks (right room nearest control room)
    box(f"PR_machine_rack_{k}", corr1 + 0.6 + k * 0.7, corr1 + 1.2 + k * 0.7, Y_PART1 + 0.15, Y_PART1 + 0.95, F_MID, F_MID + 2.0, "panel_black", PM, "PROPOSED", "machine room: computers/amps/converters out of the control room")
PL = "34_PROPOSED_LIVE_ROOM"
# central machinery aisle + storage envelopes (painted floor lines)
for nm, x in (("aisle_L", AX - GD_W/2), ("aisle_R", AX + GD_W/2)):
    box(f"PR_LV_{nm}_line", x - 0.05, x + 0.05, Y_MID1 + 0.3, Y_LIVE_G - 0.1, F_LIVE, F_LIVE + 0.004, "zone_paint", PL, "PROPOSED", "machinery route kept clear to the garage door")
bays = [("bay_L", LIVE_L + 0.3, AX - GD_W/2 - 0.3, Y_MID1 + 0.4, Y_LOFT_END - 0.7), ("bay_R", AX + GD_W/2 + 0.3, LIVE_R - 0.3, Y_MID1 + 0.4, Y_LOFT_END - 0.7)]
for nm, x0_, x1_, y0_, y1_ in bays:
    for xa, xb, ya, yb in ((x0_, x1_, y0_, y0_ + 0.08), (x0_, x1_, y1_ - 0.08, y1_), (x0_, x0_ + 0.08, y0_, y1_), (x1_ - 0.08, x1_, y0_, y1_)):
        box(f"PR_LV_{nm}_outline", xa, xb, ya, yb, F_LIVE, F_LIVE + 0.004, "zone_paint", PL, "PROPOSED", "machinery storage envelope under the loft")
# machinery placeholders (owner to supply real list/sizes) - deliberately simple, not invented models
for k, (x, y, w, l, h) in enumerate(((LIVE_L + 1.6, Y_MID1 + 2.2, 1.6, 2.6, 1.6), (LIVE_L + 1.4, Y_MID1 + 5.2, 1.3, 1.8, 1.2),
                                     (LIVE_R - 1.6, Y_MID1 + 2.4, 1.8, 2.2, 1.4), (LIVE_R - 1.4, Y_MID1 + 5.1, 1.2, 1.5, 1.1))):
    box(f"PR_machinery_placeholder_{k}", x - w/2, x + w/2, y - l/2, y + l/2, F_LIVE, F_LIVE + h, "machinery", PL, "PLACEHOLDER",
        "farm machinery envelope (actual machines/sizes from owner); covered, fuel-isolated, never run during sessions")
# grand piano (size TBD; 7' class shown) in the high tray zone, string quartet, gobos
def grand_piano(x, y, rot_deg, L=2.13, Wd=1.52):
    e = bpy.data.objects.new("PR_grand_piano", None); col(PL).objects.link(e)
    pts = [(-Wd/2, 0), (Wd/2, 0), (Wd/2, 0.55), (0.45, 1.25), (0.15, L), (-0.35, L), (-Wd/2, 1.15)]
    body = poly_prism("PR_piano_case", pts, "Z", 0.62, 0.98, "piano", PL, "PROPOSED", "7-ft class grand shown; actual piano TBD")
    lid = poly_prism("PR_piano_lid", pts, "Z", 0.0, 0.02, "piano", PL, "PROPOSED")
    lid.location = (0, 0, 0.98); lid.rotation_euler = (0, -math.radians(38), 0)
    kb = box("PR_piano_keys", -0.62, 0.62, -0.18, 0.0, 0.70, 0.74, "fader", PL, "PROPOSED")
    legs = [box(f"PR_piano_leg{i}", lx - 0.05, lx + 0.05, ly - 0.05, ly + 0.05, 0, 0.62, "piano", PL, "PROPOSED") for i, (lx, ly) in enumerate(((-0.6, 0.15), (0.6, 0.15), (-0.2, 1.75)))]
    for o in [body, lid, kb] + legs: o.parent = e
    e.location = (x, y, F_LIVE); e.rotation_euler = (0, 0, math.radians(rot_deg)); return e
grand_piano(AX - 1.4, Y_LOFT_END + 2.6, -25)
for k in range(4):   # string quartet arc facing each other
    a = math.radians(200 + k * 45); cx_, cy_ = AX + 2.2, Y_LOFT_END + 4.6
    x, y = cx_ + 1.2 * math.cos(a), cy_ + 1.2 * math.sin(a)
    box(f"PR_quartet_chair_{k}", x - 0.22, x + 0.22, y - 0.22, y + 0.22, F_LIVE + 0.44, F_LIVE + 0.48, "reclaimed", PL, "PROPOSED")
    for lx, ly in ((-0.18, -0.18), (0.18, -0.18), (-0.18, 0.18), (0.18, 0.18)):
        box(f"PR_quartet_chair_{k}_leg", x + lx - 0.015, x + lx + 0.015, y + ly - 0.015, y + ly + 0.015, F_LIVE, F_LIVE + 0.44, "steel_black", PL, "PROPOSED")
    box(f"PR_quartet_stand_{k}", x - 0.01 + 0.4*math.cos(a+math.pi), x + 0.01 + 0.4*math.cos(a+math.pi), y - 0.01 + 0.4*math.sin(a+math.pi), y + 0.01 + 0.4*math.sin(a+math.pi), F_LIVE, F_LIVE + 1.1, "steel_black", PL, "PROPOSED")
for k, (x, y, r) in enumerate(((AX - 3.4, Y_LOFT_END + 4.4, 70), (AX - 3.0, Y_LOFT_END + 5.9, 100), (AX + 0.4, Y_LOFT_END + 6.6, 0), (AX + 3.9, Y_LOFT_END + 2.6, 120))):
    e = bpy.data.objects.new(f"PR_gobo_{k}", None); col(PL).objects.link(e)
    p_ = box(f"PR_gobo_{k}_panel", -0.6, 0.6, -0.05, 0.05, 0.12, 1.92, "gobo", PL, "PROPOSED", "movable gobo: reclaimed wood one face, absorptive other")
    w_ = box(f"PR_gobo_{k}_base", -0.55, 0.55, -0.2, 0.2, 0, 0.12, "steel", PL, "PROPOSED")
    p_.parent = e; w_.parent = e; e.location = (x, y, F_LIVE); e.rotation_euler = (0, 0, math.radians(r))
# variable-acoustic hinged panels on the live-room side walls (tray zone, between windows)
for side, x in (("L", LIVE_L + 0.06), ("R", LIVE_R - 0.06)):
    for k in range(5):
        y0_ = Y_LOFT_END + 0.6 + k * 1.45
        box(f"PR_LV_varpanel_{side}{k}", x - 0.04, x + 0.04, y0_, y0_ + 1.2, F_LIVE + 0.3, F_LIVE + 2.3, "reclaimed" if k % 2 else "fabric", PL, "PROPOSED",
            "hinged variable-acoustic panel: absorptive / reflective faces")
# industrial pendants in the tray zone
for k in range(4):
    y_ = Y_LOFT_END + 1.2 + k * 1.9
    cyl(f"PR_LV_pendant_{k}", 0.16, 0.18, (AX, y_, LIVE["hc"] - 0.8), "pendant", PL)
    box(f"PR_LV_pendant_cord_{k}", AX - 0.005, AX + 0.005, y_ - 0.005, y_ + 0.005, LIVE["hc"] - 0.71, LIVE["hc"], "steel_black", PL, "PROPOSED")
box("PR_loft_guard_rail", AX - 0.95, AX + 0.95, Y_LOFT_END - 0.26, Y_LOFT_END - 0.20, LOFT_DECK + 1.02, LOFT_DECK + 1.07, "steel", PL, "PROPOSED", "guard at loft overlook (code height/infill by architect)")
for gx in (AX - 0.95, AX, AX + 0.95):
    box(f"PR_loft_guard_post_{gx:.2f}", gx - 0.025, gx + 0.025, Y_LOFT_END - 0.26, Y_LOFT_END - 0.20, LOFT_DECK, LOFT_DECK + 1.02, "steel", PL, "PROPOSED")

# ================================================================== lights, world, cameras, render
world = bpy.data.worlds.new("World"); scene.world = world; world.use_nodes = True
bg = world.node_tree.nodes["Background"]; bg.inputs["Color"].default_value = (0.55, 0.65, 0.80, 1); bg.inputs["Strength"].default_value = 0.55
sun = bpy.data.lights.new("sun", "SUN"); sun.energy = 3.0; sun.angle = math.radians(2)
so = bpy.data.objects.new("sun", sun); so.rotation_euler = (math.radians(55), 0, math.radians(-125)); scene.collection.objects.link(so)
def area(name, loc, size, energy, color=(1, 0.92, 0.82), coll="91_LIGHTS"):
    L = bpy.data.lights.new(name, "AREA"); L.size = size; L.energy = energy; L.color = color
    o = bpy.data.objects.new(name, L); o.location = loc; col(coll).objects.link(o); return o
area("cr_fill_1", (AX, LPy, G["hc"] - 0.3), 2.5, 260)
area("cr_fill_2", (AX, 2.0, G["hc"] - 0.3), 2.5, 160)
area("lv_fill_1", (AX, Y_LOFT_END + 3.5, LIVE["hc"] - 0.2), 3.0, 500)
area("lv_fill_2", (AX, Y_MID1 + 3.0, UNDERLOFT_CLG - 0.1), 3.0, 300)
for k, (x, y) in enumerate(((AX - 3.0, Y_PART1 + 2.3), (AX + 3.0, Y_PART1 + 1.0), (AX + 3.0, Y_PART1 + 3.9), (AX - 3.0, Y_PART1 + 6.2), (AX + 3.0, Y_PART1 + 6.8), (AX, Y_PART1 + 3.9))):
    area(f"mz_light_{k}", (x, y, F_MID + 2.35), 1.5, 220)
area("loft_light", (AX, Y_LOFT_END - 3.0, LOFT_DECK + 1.6), 2.0, 120)

CAMS = {
 "cr_front":      ((AX - 0.6, 0.55, 1.75), (AX + 0.1, 8.2, 1.15), 20),
 "cr_rear":       ((AX + 2.1, 7.25, 1.70), (AX - 0.6, 0.3, 0.95), 19),
 "cr_console":    ((AX - 1.55, 2.30, 1.75), (AX + 0.3, 5.3, 1.05), 28),
 "cr_cinema":     ((AX + 0.35, 1.05, 1.10), (AX, CIN["screen_y"], CIN["screen_bottom_z"] + CIN["screen_height"]/2), 24),
 "cr_fireside":   ((AX + 1.7, 6.9, 1.50), (AX - 2.2, 7.4, 0.65), 22),
 "live_piano":    ((AX + 2.7, Y_LIVE_G - 0.6, 1.70), (AX - 1.5, Y_MID1 + 2.0, 1.6), 18),
 "live_farm":     ((AX - 0.6, Y_MID1 + 0.6, 1.60), (AX + 0.3, Y_LIVE_G, 1.4), 18),
 "loft_overlook": ((AX + 0.1, Y_LOFT_END - 0.9, LOFT_DECK + 0.72), (AX - 0.6, Y_LIVE_G - 1.5, F_LIVE + 0.6), 16),
 "exterior":      ((-9.0, -12.0, 1.7), (AX, 10.0, 1.5), 26),
 "axo_cutaway":   ((-14.0, -10.0, 16.0), (AX, 15.0, 0.0), 24),
}
cam_obs = {}
for k, (loc, tgt, lens) in CAMS.items():
    c = bpy.data.cameras.new(k); c.lens = lens; c.sensor_width = 36; c.clip_start = 0.05; c.clip_end = 200
    o = bpy.data.objects.new("CAM_" + k, c); o.location = loc; col("90_CAMERAS").objects.link(o)
    t = bpy.data.objects.new("TGT_" + k, None); t.location = tgt; col("90_CAMERAS").objects.link(t)
    tc = o.constraints.new("TRACK_TO"); tc.target = t; tc.track_axis = "TRACK_NEGATIVE_Z"; tc.up_axis = "UP_Y"
    cam_obs[k] = o
cam_obs["axo_cutaway"].data.type = "ORTHO"; cam_obs["axo_cutaway"].data.ortho_scale = 34

scene.render.engine = "CYCLES"; scene.cycles.device = "CPU"
scene.cycles.samples = int(os.environ.get("BG_SAMPLES", 96)); scene.cycles.use_denoising = True
scene.cycles.max_bounces = 6
scene.render.resolution_x, scene.render.resolution_y = int(os.environ.get("BG_RES_X", 1600)), int(os.environ.get("BG_RES_Y", 900))
scene.view_settings.view_transform = "AgX"; scene.view_settings.look = "AgX - Base Contrast"
blend = os.path.join(HERE, "breakglass_east_v04.blend")
bpy.ops.wm.save_as_mainfile(filepath=blend); print("saved", blend)

INTERIOR_HIDE = ["EX_roof_metal", "EX_siding_long_L", "EX_siding_long_R", "EX_siding_gable_control", "EX_siding_gable_live", "EX_ground"]
if os.environ.get("BG_RENDER"):
    out = os.path.join(ROOT, "renders", "design"); os.makedirs(out, exist_ok=True)
    only = [s for s in os.environ.get("BG_ONLY", "").split(",") if s]
    for k, o in cam_obs.items():
        if only and k not in only: continue
        scene.camera = o
        interior = k not in ("exterior", "axo_cutaway")
        for nm in INTERIOR_HIDE:
            ob = bpy.data.objects[nm]; ob.visible_camera = not interior or nm == "EX_roof_metal" and False
            if nm == "EX_roof_metal": ob.hide_render = (k == "axo_cutaway")
        bpy.data.objects["EX_ground"].visible_camera = not interior
        for nm in ("EX_CR_ceiling", "EX_LV_tray_ceiling", "EX_MZ_ceiling", "EX_LOFT_deck", "EX_LV_underloft_foil", "EX_siding_long_L", "EX_CR_wall_X0", "EX_LV_wall_L", "EX_MZ_extwall_L", "EX_siding_gable_control"):
            if nm in bpy.data.objects:
                bpy.data.objects[nm].visible_camera = bpy.data.objects[nm].visible_camera if k != "axo_cutaway" else False
        cinema = (k == "cr_cinema")
        for ob in col("32_PROPOSED_SCREEN_MODE").objects: ob.hide_render = not cinema   # retracted except in movie mode
        for L in bpy.data.lights:
            if L.type == "AREA" and L.name.startswith("cr_fill"): L.energy = (25 if cinema else (260 if L.name.endswith("1") else 160))
        M["screen"].node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 2.5 if cinema else 0.0
        M["cove"].node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 4 if cinema else 25
        sun.energy = 3.0 if not interior else 2.0
        scene.render.filepath = os.path.join(out, f"{k}{os.environ.get('BG_TAG', '')}.png"); bpy.ops.render.render(write_still=True); print("rendered", k)
