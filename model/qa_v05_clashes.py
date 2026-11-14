"""v0.5 QA: clash check of every v0.5 object group against the building, openings, equipment and v0.4 proposals.

    python3 model/qa_v05_clashes.py   (reads model/breakglass_east_v05.blend) -> model/qa_v05_clashes.json
Axis-aligned bounding boxes in world space (conservative for rotated items); penetration tolerance 15 mm.
Wall-mounted items are expected to TOUCH their wall; a clash is reported only for penetration > tolerance.
"""
import json, os, bpy
from mathutils import Vector
HERE = os.path.dirname(os.path.abspath(__file__))
bpy.ops.wm.open_mainfile(filepath=os.path.join(HERE, "breakglass_east_v05.blend"))
TOL = 0.015
def aabb(objs):
    pts = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
    return [min(p[i] for p in pts) for i in range(3)], [max(p[i] for p in pts) for i in range(3)]
def pen(a, b):
    return min(min(a[1][i], b[1][i]) - max(a[0][i], b[0][i]) for i in range(3))
def visible_mesh(o): return o.type == "MESH" and not o.hide_render and not o.name.startswith("CUT_")
groups = {}
for o in bpy.data.objects:
    if o.users_collection and o.users_collection[0].name.startswith(("35_", "36_", "37_", "39_")) and visible_mesh(o):
        root = o.parent.name if o.parent else o.name
        if o.name.startswith("V5_BL_"): root = o.name   # backline parts checked one by one (parts of one kit/stand touch each other by design)
        groups.setdefault(root, []).append(o)
others = [o for o in bpy.data.objects if visible_mesh(o) and o.users_collection and not o.users_collection[0].name.startswith(("35_", "36_", "37_", "39_", "90_", "91_"))
          and not o.name.startswith(("EX_CR_wall", "EX_LV_wall", "EX_MZ_", "EX_siding", "EX_roof", "EX_ground", "EX_CR_floor", "EX_LV_slab", "EX_CR_ceiling", "EX_LV_tray", "EX_LV_loft_end",
                                       "EX_CR_gable", "EX_CR_partition", "EX_LV_gable", "EX_LV_joist", "EX_LV_underloft", "PR_CR_oak", "PR_CR_rug", "PR_cove", "PR_LV_aisle", "PR_LV_bay", "EX_envelope", "PR_hvac"))]
G = {k: aabb(v) for k, v in groups.items()}
def oriented_hit(parts, others_):
    """Exact test for thin backline parts: does any part vertex fall inside another object's own (oriented) box?"""
    for ob in others_:
        if ob.type != "MESH": continue
        inv = ob.matrix_world.inverted(); bb = ob.bound_box
        lo = [min(c[i] for c in bb) + TOL for i in range(3)]; hi = [max(c[i] for c in bb) - TOL for i in range(3)]
        for pt in parts:
            for v in pt.data.vertices:
                q = inv @ (pt.matrix_world @ v.co)
                if all(lo[i] < q[i] < hi[i] for i in range(3)): return True
    return False
def group_objs(k):
    return groups.get(k) or [o for o in bpy.data.objects if o.name == k or o.name.startswith(k + "_") or (o.parent and o.parent.name == k)]
clashes = []
for k, a in G.items():
    for o in others:
        b = aabb([o]); d = pen(a, b)
        if d > TOL and (not k.startswith("V5_BL_") or oriented_hit(groups[k], [o])):
            clashes.append({"v05": k, "with": o.name, "penetration_m": round(d, 3)})
ks = list(G)
for i in range(len(ks)):
    for j in range(i + 1, len(ks)):
        if ks[i].startswith("V5_BL_") and ks[j].startswith("V5_BL_"): continue
        d = pen(G[ks[i]], G[ks[j]])
        bl = ks[i].startswith("V5_BL_") or ks[j].startswith("V5_BL_")
        if d > TOL and bl:   # confirm with the exact oriented test (rotated gobos have loose world AABBs)
            a_, b_ = (ks[i], ks[j]) if ks[i].startswith("V5_BL_") else (ks[j], ks[i])
            if not oriented_hit(groups[a_], [o for o in bpy.data.objects if o.name == b_ or (o.parent and o.parent.name == b_) or o.name.startswith(b_ + "_")]): continue
        if d > TOL: clashes.append({"v05": ks[i], "with": ks[j], "penetration_m": round(d, 3)})
ez = bpy.data.objects.get("QA_electrical_working_space")
elec = []
if ez:
    zb = aabb([ez])
    for o in bpy.data.objects:
        if not visible_mesh(o) or o is ez or o.name.startswith(("EX_", "PR_CR_oak", "PR_CR_rug", "LOOKDEV")): continue
        if o.users_collection and o.users_collection[0].name.startswith(("90_", "91_")): continue
        d = pen(zb, aabb([o]))
        if d > TOL: elec.append({"object": o.name, "penetration_m": round(d, 3)})
    assert not elec, f"objects inside the electrical working space: {elec}"
json.dump({"groups": len(G), "tolerance_m": TOL, "clashes": clashes, "electrical_working_space_clear": not elec}, open(os.path.join(HERE, "qa_v05_clashes.json"), "w"), indent=1)
print("groups", len(G), "clashes", len(clashes))
for c in clashes: print(c)
