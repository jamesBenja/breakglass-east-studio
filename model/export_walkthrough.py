"""Export the v0.5 studio for the browser walkthrough (web/walkthrough/).

    python3 model/export_walkthrough.py      (reads model/breakglass_east_v05.blend)
      -> web/walkthrough/studio_v05.glb      (geometry + flat materials, modifiers applied, glTF Y-up)
      -> web/walkthrough/studio_v05.glb.txt  (the same bytes as base64 text, for hosts that only serve text)
      -> web/walkthrough/views.json          (named viewpoints from the model cameras, glTF Y-up)

Nothing private: no property terrain or owner maps (those exist only in the private fly-through build).
The walkthrough switches modes in the browser, so every mode's objects are exported and tagged with a
custom property `wk` (exported as glTF extras):
  cinema      screen-mode objects (shown only in cinema mode)
  imm         later-phase immersive speakers and subs (hidden in phase 1)
  farm_hide   quartet + band backline (packed away in farm mode)
  farm_only   the quilted piano cover (farm mode only)
Moved items carry an alternative pose as extras: `wk_cinema` (swivel armchair A) and `wk_farm` (piano, lid, gobos),
each [x, y, z, rx_deg, ry_deg, rz_deg] in Blender Z-up world units; the viewer converts to Y-up.
The farm moves mirror model/v05_treatment.apply_scenarios (layout values are read back from the model geometry).
Every object keeps `evidence_class` so the viewer can show what is scan-measured, photo-inferred, actual or proposed.
"""
import json, math, os
import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "web", "walkthrough"); os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=os.path.join(HERE, "breakglass_east_v05.blend"))

def wbb(o):
    pts = [o.matrix_world @ Vector(c) for c in o.bound_box]
    return [min(p[i] for p in pts) for i in range(3)], [max(p[i] for p in pts) for i in range(3)]

def tag_tree(o, t):
    for x in [o, *o.children_recursive]:
        if "wk" not in x: x["wk"] = t

# --- mode tags
for o in bpy.data.objects:
    if o.users_collection and o.users_collection[0].name.startswith("32_PROPOSED_SCREEN"): tag_tree(o, "cinema")
for o in bpy.data.objects:
    if o.name.startswith(("PR_imm_", "PR_sub_")): tag_tree(o, "imm")
    if o.name.startswith(("PR_quartet_", "V5_BL_")): tag_tree(o, "farm_hide")

def pose(loc, rot): return [round(loc[0], 4), round(loc[1], 4), round(loc[2], 4), *[round(math.degrees(r), 3) for r in rot]]

# swivel armchair A: cinema pose from the lounge solver (as v05_treatment.set_mode)
A = bpy.data.objects.get("V5_swivel_armchair_A")
if A is not None and "cinema_pose" in A:
    x, y, yaw = A["cinema_pose"]; A["wk_cinema"] = pose((x, y, 0.0), (0, 0, math.radians(yaw)))

# farm mode (mirrors v05_treatment.apply_scenarios)
slab_lo, slab_hi = wbb(bpy.data.objects["EX_LV_slab"])
LIVE_L, LIVE_R, F = slab_lo[0], slab_hi[0], slab_hi[2]
YL = wbb(bpy.data.objects["EX_LV_beam_loft_edge"])[1][1] + 0.3
pe = bpy.data.objects["PR_grand_piano"]; pe["wk_farm"] = pose((LIVE_L + 1.15, YL + 3.05, F), (0, 0, 0))
lid = bpy.data.objects.get("PR_piano_lid")
if lid is not None: lid["wk_farm"] = pose(lid.location, (0, 0, 0)); lid["wk_farm_local"] = 1
gob = sorted([o for o in bpy.data.objects if o.name.startswith(("V5_GOB-001_", "V5_GOB-002_")) and o.type == "EMPTY"], key=lambda o: o.name)
for i, o in enumerate(gob):
    o["wk_farm"] = pose((LIVE_R - 0.33 - 0.17 * i, 29.05, o.location.z), (0, 0, math.radians(90)))
rug = next((m for m in bpy.data.materials if "rug" in m.name.lower()), None)
cx, cy = LIVE_L + 1.15, YL + 3.05
bpy.ops.mesh.primitive_cube_add(size=1, location=(cx, cy + (2.20 - 0.22) / 2, F + (0.60 + 1.03) / 2))
cov = bpy.context.active_object; cov.name = "FARM_piano_cover"; cov.scale = (1.64, 2.42, 0.43)
if rug: cov.data.materials.append(rug)
cov["wk"] = "farm_only"; cov["evidence_class"] = "PROPOSED"; cov["note"] = "quilted piano cover on a locked dolly (NEW-06)"

# --- selection: building, equipment, proposals; never cutters, cameras, lights, QA volumes or look-dev stand-ins
SKIP_COLS = ("19_CUTTERS", "90_CAMERAS", "91_LIGHTS")
keep = []
for o in bpy.data.objects:
    c = o.users_collection[0].name if o.users_collection else ""
    if c.startswith(SKIP_COLS) or o.name.startswith(("CUT_", "QA_", "FLY_", "LOOKDEV", "CAM_", "TGT_")): continue
    if o.type not in ("MESH", "EMPTY", "CURVE"): continue
    if o.type == "MESH" and o.hide_render and "wk" not in o: continue   # render-hidden helpers
    o.hide_set(False); o.hide_viewport = False
    keep.append(o)
bpy.ops.object.select_all(action="DESELECT")
for o in keep: o.select_set(True)
for o in keep:   # keep parents of kept children so transforms stay intact
    p = o.parent
    while p is not None: p.select_set(True); p = p.parent

glb = os.path.join(OUT, "studio_v05.glb")
bpy.ops.export_scene.gltf(filepath=glb, export_format="GLB", use_selection=True, export_apply=True, export_extras=True,
                          export_yup=True, export_cameras=False, export_lights=False, export_animations=False,
                          export_materials="EXPORT", export_image_format="NONE")
print("glb", os.path.getsize(glb) // 1024, "KB,", len(keep), "objects")
import base64   # artifact hosting serves text but not .glb, so the page fetches the same bytes as base64 text
open(os.path.join(OUT, "studio_v05.glb.txt"), "w").write(base64.b64encode(open(glb, "rb").read()).decode())

# --- viewpoints from the model's own cameras (Blender Z-up -> glTF Y-up: (x, z, -y))
NAMES = {
 "cr_front": ("From the rear toward the monitors", "Control room"), "cr_console": ("Over the console", "Control room"),
 "cr_fireside": ("Fireside lounge", "Control room"), "cr_fire_seat": ("From the fireside seat", "Control room"),
 "cr_overview_rear": ("Looking back to the entry", "Control room"), "cr_rear": ("Toward the gable", "Control room"),
 "cr_cinema": ("Cinema", "Cinema"), "cr_cinema_behind_sofa": ("Behind the sofa", "Cinema"),
 "cr_cinema_window": ("Window above the entry door", "Cinema"),
 "live_piano": ("Piano and ensemble", "Live room"), "live_band": ("Band set-up", "Live room"),
 "live_drums": ("Drum booth", "Live room"), "live_farm": ("Machinery aisle", "Live room"), "loft_overlook": ("Loft overlook", "Live room"),
 "ext_entry": ("Entry gable", "Outside"), "ext_live_gable": ("Machinery door", "Outside"), "ext_aerial": ("Aerial", "Outside"),
}
def yup(v): return [round(v.x, 3), round(v.z, 3), round(-v.y, 3)]
MG = json.load(open(os.path.join(HERE, "monitoring_geometry.json")))
lp = Vector(MG["stereo"]["listening_position"])   # engineer's ears at the stereo listening point, facing the Geithains
views = [{"id": "mix_position", "label": "Mix position (seated)", "group": "Control room", "pos": yup(lp), "dir": yup(Vector((0, 1, -0.05)).normalized()),
          "lens_mm": 18.0, "mode": "studio", "fly": True}]
for k, (label, group) in NAMES.items():
    cam = bpy.data.objects.get("CAM_" + k)
    if cam is None: continue
    mw = cam.matrix_world; fwd = (mw.to_3x3() @ Vector((0, 0, -1))).normalized()
    views.append({"id": k, "label": label, "group": group, "pos": yup(mw.translation), "dir": yup(fwd),
                  "lens_mm": round(cam.data.lens, 1), "mode": "cinema" if k.startswith("cr_cinema") else ("farm" if k == "live_farm" else "studio"),
                  "fly": k.startswith(("ext_aerial", "cr_cinema_window", "cr_overview", "cr_console", "loft_overlook", "axo"))})
lights = []   # interior area lights -> approximate point lights in the viewer (positions only; the viewer sets its own levels)
for o in bpy.data.objects:
    if o.type == "LIGHT" and o.data.type == "AREA":
        lights.append({"name": o.name, "pos": yup(o.matrix_world.translation), "zone": o.name.split("_")[0]})
json.dump({"model": "breakglass_east_v05.blend", "units": "metres", "axes": "glTF Y-up (x, z_blender, -y_blender)",
           "views": views, "lights": lights}, open(os.path.join(OUT, "views.json"), "w"), indent=1)
print("views", len(views))
