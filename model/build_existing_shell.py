"""Build the existing-conditions CONTROL ROOM shell in Blender from the camera solve.

    python3 model/build_existing_shell.py            # needs `pip install bpy==5.2.3`

Reads  model/solve_result.json  (written by model/camera_solve.py)
Writes model/existing_control_room_v02.blend
       renders/qa/*.png  (clay renders from the three solved photo cameras + axonometric)

Rules enforced here (see docs/STRATEGY_AND_ASSESSMENT.md):
  * No studio equipment, finishes or proposed elements.
  * Every object carries custom properties: evidence_class, source, sigma_m.
  * Material colour encodes evidence class, never aesthetics:
        SCAN-LABELLED  blue-grey   PHOTO-SOLVED  warm clay   PHOTO-INFERRED  amber
        UNKNOWN/PLACEHOLDER  magenta wire (not rendered solid)
"""
import json, math, os, sys
import bpy
from mathutils import Vector, Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SOL = json.load(open(os.path.join(HERE, "solve_result.json")))
P = {k: v["value"] for k, v in SOL["params"].items()}
S = {k: v["sigma"] for k, v in SOL["params"].items()}
IMG_W, IMG_H = 1600, 1200

W, D = P["W"], P["D"]
sys.path.insert(0, HERE)
from section import geom
G = geom(P)
hc, wc, xc1, xc2 = G["hc"], G["wc"], G["xc1"], G["xc2"]
hloL, hloR, xL, xR = G["hloL"], G["hloR"], G["xL"], G["xR"]

# ---------------------------------------------------------------- scene setup
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = "METRIC"; scene.unit_settings.length_unit = "METERS"

def collection(name):
    c = bpy.data.collections.new(name); scene.collection.children.link(c); return c

COL = {k: collection(k) for k in ("10_SCAN_LABELLED", "20_PHOTO_SOLVED", "30_PHOTO_INFERRED", "40_OPENINGS", "90_CAMERAS")}

def material(name, rgb, alpha=1.0):
    m = bpy.data.materials.new(name); m.diffuse_color = (*rgb, alpha)
    m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF"); b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = 0.8
    return m

MAT = {"PHOTO-SOLVED": material("ev_photo_solved", (0.80, 0.76, 0.70)),
       "SCAN-LABELLED": material("ev_scan_labelled", (0.55, 0.62, 0.72)),
       "PHOTO-INFERRED": material("ev_photo_inferred", (0.90, 0.65, 0.25)),
       "OPENING": material("ev_opening", (0.08, 0.10, 0.14)),
       "POST": material("ev_post", (0.55, 0.36, 0.20))}

def tag(obj, ev, source, sigma=None, note=""):
    obj["evidence_class"] = ev; obj["source"] = source
    if sigma is not None: obj["sigma_m"] = round(float(sigma), 3)
    if note: obj["note"] = note

def mesh(name, verts, faces, col, mat, ev, source, sigma=None, note=""):
    me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces); me.update()
    ob = bpy.data.objects.new(name, me); COL[col].objects.link(ob)
    ob.data.materials.append(MAT[mat]); tag(ob, ev, source, sigma, note); return ob

def box(name, x0, x1, y0, y1, z0, z1, col, mat, ev, source, sigma=None, note=""):
    v = [(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)]
    f = [(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]
    return mesh(name, v, f, col, mat, ev, source, sigma, note)

SRC_SOLVE = "fused solve: native Polycam LiDAR mesh (priors) + camera matches CR1/CR2/CR3 (camera_solve.py)"

# ---------------------------------------------------------------- floor + walls
mesh("CR_floor", [(0,0,0),(W,0,0),(W,D,0),(0,D,0)], [(0,1,2,3)], "10_SCAN_LABELLED", "SCAN-LABELLED",
     "SCAN-MEASURED", "Native LiDAR mesh wall fits (width %.2f, depth %.2f), refined by photos" % (W, D), max(S["W"], S["D"]),
     "Plan extents. Interior faces; wall thickness UNKNOWN.")
mesh("CR_wall_X0", [(0,0,0),(0,D,0),(0,D,hloL),(0,0,hloL)], [(0,1,2,3)], "20_PHOTO_SOLVED", "PHOTO-SOLVED", "SCAN-MEASURED", "native scan wall fit + low ceiling", 0.05)
mesh("CR_wall_XW", [(W,0,0),(W,D,0),(W,D,hloR),(W,0,hloR)], [(0,3,2,1)], "20_PHOTO_SOLVED", "PHOTO-SOLVED", "SCAN-MEASURED", SRC_SOLVE, S["hloR"])
# end walls follow the ceiling section (vertical walls confirmed at both ends: same top/bottom width ratio 0.55 in CR1 and CR3)
section = G["section"]
for name, y in (("CR_gable_wall_Y0", 0.0), ("CR_partition_wall_YD", D)):
    mesh(name, [(x, y, z) for x, z in section], [tuple(range(len(section)))], "20_PHOTO_SOLVED", "PHOTO-SOLVED",
         "PHOTO-SOLVED", SRC_SOLVE, max(S["hc"], S["W"]),
         "Gable wall = building end wall (exterior)." if y == 0 else "Interior partition to intermediate zone; thickness UNKNOWN.")

# ---------------------------------------------------------------- ceiling (extruded section)
ceil = G["ceil"]
verts = [(x, 0, z) for x, z in ceil] + [(x, D, z) for x, z in ceil]
n = len(ceil)
faces = [(i, i+1, n+i+1, n+i) for i in range(n-1)]
mesh("CR_ceiling", verts, faces, "20_PHOTO_SOLVED", "PHOTO-SOLVED", "PHOTO-SOLVED", SRC_SOLVE, S["hc"],
     "ASYMMETRIC section (scan-confirmed): low zones L %.2f m deep @%.2f / R %.2f m deep @%.2f; flat centre h=%.2f w=%.2f centred at X=%.2f (room centre %.2f)." % (xL, hloL, W-xR, hloR, hc, wc, G["xf"], W/2))

# beams (downstand under the low-ceiling edge, carried by posts)
bw = 0.19  # PHOTO-INFERRED width (not solved)
for name, x, hbb, hlo, sk in (("CR_beam_left", xL, G["hbbL"], hloL, "hbbL"), ("CR_beam_right", xR, G["hbbR"], hloR, "hbbR")):
    box(name, x - bw/2, x + bw/2, 0, D, hbb, hlo, "20_PHOTO_SOLVED", "PHOTO-SOLVED", "PHOTO-SOLVED", SRC_SOLVE, S[sk],
        "Underside solved; width %.2f m photo-inferred; bearing at end walls UNKNOWN." % bw)

# posts (one per side visible in CR1/CR2/CR3; further posts UNKNOWN)
ps = 0.14  # PHOTO-INFERRED section
for name, x, y, sy, hbb in (("CR_post_left", xL, P["ypl"], S["ypl"], G["hbbL"]), ("CR_post_right", xR, P["ypr"], S["ypr"], G["hbbR"])):
    box(name, x - ps/2, x + ps/2, y - ps/2, y + ps/2, 0, hbb, "20_PHOTO_SOLVED", "POST", "PHOTO-SOLVED", SRC_SOLVE, sy,
        "Position solved (Y sigma %.2f m); section %.2f m photo-inferred; footing UNKNOWN." % (sy, ps))

# ---------------------------------------------------------------- openings (dark panels 10 mm proud of wall)
def opening(name, plane, a0, a1, z0, z1, src, sig, note=""):
    e = 0.01
    if plane == "Y0":   v = [(a0, e, z0), (a1, e, z0), (a1, e, z1), (a0, e, z1)]
    elif plane == "YD": v = [(a0, D-e, z0), (a1, D-e, z0), (a1, D-e, z1), (a0, D-e, z1)]
    elif plane == "XW": v = [(W-e, a0, z0), (W-e, a1, z0), (W-e, a1, z1), (W-e, a0, z1)]
    return mesh(name, v, [(0,1,2,3)], "40_OPENINGS", "OPENING", "PHOTO-SOLVED", src, sig, note)

def g(k): return P[k]
opening("OPN_gable_entry_door", "Y0", min(g("CR3.xe1"), g("CR3.xe2")), max(g("CR3.xe1"), g("CR3.xe2")), 0, g("CR3.he"), "CR3 e1-e4", S["CR3.he"])
opening("OPN_gable_clerestory", "Y0", min(g("CR3.xw1"), g("CR3.xw2")), max(g("CR3.xw1"), g("CR3.xw2")), g("CR3.hwb"), g("CR3.hwt"), "CR3 w1-w4", S["CR3.hwt"])
opening("OPN_gable_interior_door", "Y0", min(g("g_xi1"), g("g_xi2")), max(g("g_xi1"), g("g_xi2")), 0, g("g_hi"), "CR3 i1-i4", S["g_hi"],
        "White door on gable wall: leads to a closet/vestibule? Use UNKNOWN.")
opening("OPN_partition_doorway", "YD", (g("CR1.xd1")+g("CR2.xd1"))/2, (g("CR1.xd2")+g("CR2.xd2"))/2, 0, (g("CR1.hd")+g("CR2.hd"))/2,
        "CR1/CR2 d1-d4 (mean)", S["CR1.hd"], "Curtained doorway to intermediate zone.")
y_a, y_b = sorted((g("CR1.wy1"), g("CR1.wy2")))
opening("OPN_sidewall_XW_long_window_partial", "XW", y_a, y_b, g("CR1.wsill"), g("CR1.wh"), "CR1 wn1-wn4", S["CR1.wh"],
        "Only the far end (Y=%.2f) is observed; the window continues out of frame toward the gable. Full extent UNKNOWN." % y_b)

# ---------------------------------------------------------------- cameras from the solve
def add_camera(cid, f_key):
    tx, ty, tz = P[f"{cid}.tx"], P[f"{cid}.ty"], P[f"{cid}.tz"]
    yaw, pitch, roll = P[f"{cid}.yaw"], P[f"{cid}.pitch"], P[f"{cid}.roll"]
    f = P[f_key]
    fwd = Vector((math.sin(yaw)*math.cos(pitch), math.cos(yaw)*math.cos(pitch), math.sin(pitch)))
    right0 = Vector((math.cos(yaw), -math.sin(yaw), 0.0)); up0 = right0.cross(fwd)
    cr, sr = math.cos(roll), math.sin(roll)
    right = cr*right0 + sr*up0; up = -sr*right0 + cr*up0
    R = Matrix((right, up, -fwd)).transposed()           # columns = camera local X, Y, Z in world
    cam = bpy.data.cameras.new(cid); cam.sensor_fit = "HORIZONTAL"; cam.sensor_width = 36.0
    cam.lens = f / IMG_W * 36.0; cam.clip_start = 0.05; cam.clip_end = 100
    ob = bpy.data.objects.new("CAM_" + cid, cam); COL["90_CAMERAS"].objects.link(ob)
    ob.matrix_world = Matrix.Translation((tx, ty, tz)) @ R.to_4x4()
    tag(ob, "PHOTO-SOLVED", f"camera_solve.py {cid}", None, "Matches private source photo %s" % cid)
    return ob

cams = {cid: add_camera(cid, "lens13.f") for cid in ("CR1", "CR2", "CR3")}

# cutaway axonometric review camera (not a photo match): near gable + X=0 wall hidden for this view only
axo = bpy.data.cameras.new("AXO"); axo.type = "ORTHO"; axo.ortho_scale = 15.5
ob = bpy.data.objects.new("CAM_AXO_cutaway", axo); COL["90_CAMERAS"].objects.link(ob)
ob.location = (-8.0, -9.5, 9.0)
tgt = bpy.data.objects.new("AXO_target", None); tgt.location = (W/2, D/2, 1.4); COL["90_CAMERAS"].objects.link(tgt)
c = ob.constraints.new("TRACK_TO"); c.target = tgt; c.track_axis = "TRACK_NEGATIVE_Z"; c.up_axis = "UP_Y"
cams["AXO"] = ob

# ---------------------------------------------------------------- render settings
# Cycles on CPU (this cloud container has no GPU/EGL, so Workbench/Eevee cannot run).
# QA clay only: uniform interior light so geometry, not mood, is what you see.
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"; scene.cycles.samples = int(os.environ.get("BG_SAMPLES", 48))
scene.cycles.use_denoising = True
scene.render.resolution_x, scene.render.resolution_y = IMG_W // 2, IMG_H // 2
world = bpy.data.worlds.new("World"); scene.world = world; world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.9, 0.9, 0.92, 1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.15
for i, (x, y) in enumerate(((W*0.3, D*0.3), (W*0.7, D*0.3), (W*0.3, D*0.7), (W*0.7, D*0.7))):
    L = bpy.data.lights.new(f"qa_light_{i}", "POINT"); L.energy = 140; L.shadow_soft_size = 0.8
    lo = bpy.data.objects.new(f"qa_light_{i}", L); lo.location = (x, y, 1.7); scene.collection.objects.link(lo)
scene.view_settings.view_transform = "AgX"
out_dir = os.path.join(ROOT, "renders", "qa"); os.makedirs(out_dir, exist_ok=True)
blend = os.path.join(HERE, "existing_control_room_v02.blend")
bpy.ops.wm.save_as_mainfile(filepath=blend)
sun = bpy.data.lights.new("qa_sun", "SUN"); sun.energy = 2.5
sun_ob = bpy.data.objects.new("qa_sun", sun); sun_ob.rotation_euler = (math.radians(50), 0, math.radians(-35)); scene.collection.objects.link(sun_ob)
CUTAWAY_HIDE = ("CR_gable_wall_Y0", "CR_wall_X0", "OPN_gable_entry_door", "OPN_gable_clerestory", "OPN_gable_interior_door")
for cid, ob in cams.items():
    scene.camera = ob
    for nm in CUTAWAY_HIDE: bpy.data.objects[nm].hide_render = (cid == "AXO")
    sun_ob.hide_render = (cid != "AXO")
    bpy.data.objects["CR_ceiling"].visible_camera = (cid != "AXO")   # section reads on far wall
    scene.render.filepath = os.path.join(out_dir, f"clay_{cid}.png")
    bpy.ops.render.render(write_still=True)
print("saved", blend)
