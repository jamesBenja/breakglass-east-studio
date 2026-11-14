"""v0.5 lounge furniture detail (owner request 14 Nov): black leather sofa / loveseat / swivel armchairs with real cushion
shapes, linen throw cushions, cushions on the window benches (NEW-01 bench traps) and two floor cushions by the fireside.

Footprints and positions are unchanged: they come from acoustics/out/lounge_layout.json (the lounge solver) and the
v0.4 cinema-sofa envelope. Only the box stand-ins are replaced by detailed geometry. PROPOSED furniture, generic models.
Soft furnishings obey the same stove clearance as the seats (solver). Window-bench cushions are breathable linen over
open-cell foam so the bass traps beneath keep working (leather/vinyl would seal the top face).
"""
import json, math, os
import bmesh, bpy
from mathutils import Matrix, Vector

LG = "37_V05_LOUNGE"
EV = "PROPOSED (owner-requested furniture detail; generic)"

def build(g):
    col, M, mat = g["col"], g["M"], g["mat"]
    for k, rgb, r in (("v5_black_leather", (0.018, 0.018, 0.02), 0.42), ("v5_linen_oat", (0.60, 0.55, 0.47), 0.9),
                      ("v5_linen_charcoal", (0.10, 0.10, 0.105), 0.9), ("v5_linen_rust", (0.36, 0.15, 0.07), 0.9)):
        if k not in M: M[k] = mat(k, rgb, r)
    coll = col(LG); n = [0]

    def rbox(name, c, s, m, parent=None, bevel=0.03, puff=0.0, rot=(0, 0, 0)):
        """Rounded box (bevelled; 'puff' bulges it like a filled cushion)."""
        me = bpy.data.meshes.new(name); bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Diagonal((*s, 1.0)))   # real size in the mesh: bevel widths stay true
        if puff:
            bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=4, use_grid_fill=True)
        bm.to_mesh(me); bm.free()
        me.materials.append(M[m]); n[0] += 1
        o = bpy.data.objects.new(f"{name}", me); coll.objects.link(o)
        o.location = c; o.rotation_euler = rot
        if puff:
            cs = o.modifiers.new("puff", "CAST"); cs.cast_type = "SPHERE"; cs.factor = puff; cs.use_x = cs.use_y = True; cs.use_z = True
        bv = o.modifiers.new("round", "BEVEL"); bv.width = bevel; bv.segments = 5; bv.limit_method = "ANGLE"; bv.use_clamp_overlap = True
        if puff:
            ss = o.modifiers.new("smooth", "SUBSURF"); ss.levels = 1; ss.render_levels = 2
        for p in me.polygons: p.use_smooth = True
        o["evidence_class"] = EV
        if parent: o.parent = parent
        return o

    def upholstered(e, w, d, kind, pillows=()):
        """Leather seating built in the parent's local frame (local +Y = facing, back at -d/2)."""
        arm = 0.17 if kind != "chair" else 0.13
        h0 = 0.10 if kind != "chair" else 0.30            # plinth bottom (chairs sit on the swivel pedestal)
        nseat = {"sofa": 3, "loveseat": 2, "chair": 1}[kind]
        rbox(e.name + "_plinth", (0, 0.02, h0 + 0.10), (w - 0.04, d - 0.06, 0.20), "v5_black_leather", e, 0.025)
        rbox(e.name + "_backframe", (0, -d / 2 + 0.08, h0 + 0.33), (w, 0.16, 0.66), "v5_black_leather", e, 0.035)
        for sx in (-1, 1):
            rbox(e.name + "_arm", (sx * (w / 2 - arm / 2), 0.0, h0 + 0.24), (arm, d, 0.48), "v5_black_leather", e, 0.045)
        inner = w - 2 * arm; cw = inner / nseat
        for i in range(nseat):
            x = -inner / 2 + cw * (i + 0.5)
            rbox(e.name + "_seatcushion", (x, 0.07, h0 + 0.27), (cw - 0.012, d - 0.26, 0.15), "v5_black_leather", e, 0.04, puff=0.12)
            rbox(e.name + "_backcushion", (x, -d / 2 + 0.25, h0 + 0.55), (cw - 0.012, 0.17, 0.42), "v5_black_leather", e, 0.05, puff=0.16,
                 rot=(math.radians(-10), 0, 0))
        for k, (fx, m) in enumerate(pillows):   # linen throw cushions leaning on the back cushions
            x = fx * (inner / 2 - 0.22)
            rbox(e.name + "_pillow", (x, -d / 2 + 0.40, h0 + 0.53), (0.44, 0.13, 0.42), m, e, 0.06, puff=0.35,
                 rot=(math.radians(-18), 0, math.radians(8 * (1 if fx < 0 else -1))))
        if kind != "chair":
            for lx in (-w / 2 + 0.08, w / 2 - 0.08):
                for ly in (-d / 2 + 0.08, d / 2 - 0.08):
                    rbox(e.name + "_leg", (lx, ly, h0 / 2), (0.04, 0.04, h0), "steel_black", e, 0.005)

    def strip(e):
        for c in list(e.children):
            if not c.name.endswith(("_pedestal", "_disc")): bpy.data.objects.remove(c, do_unlink=True)

    # fireside loveseat + swivel armchairs (positions/poses unchanged; only the geometry is detailed)
    ls = bpy.data.objects["V5_lounge_loveseat"]; strip(ls)
    upholstered(ls, 1.45, 0.85, "loveseat", pillows=((-1, "v5_linen_oat"), (1, "v5_linen_rust")))
    for nm, pl in (("V5_swivel_armchair_A", ((0, "v5_linen_oat"),)), ("V5_swivel_armchair_B", ())):
        e = bpy.data.objects[nm]; strip(e); upholstered(e, 0.80, 0.80, "chair", pillows=pl)
    # cinema sofa: same envelope as the v0.4 box sofa (AX +/- 1.4, SOFA_Y0 .. +0.95), facing the screen
    AX, SY = g["AX"], g["SOFA_Y0"]
    for o in [o for o in bpy.data.objects if o.name.startswith("PR_sofa")]: bpy.data.objects.remove(o, do_unlink=True)
    sf = bpy.data.objects.new("V5_cinema_sofa", None); coll.objects.link(sf); sf.location = (AX, SY + 0.475, 0); sf["evidence_class"] = EV
    upholstered(sf, 2.80, 0.95, "sofa", pillows=((-1, "v5_linen_oat"), (1, "v5_linen_charcoal")))

    # window-bench cushions on the NEW-01 bench traps (padded ledge; breathable linen)
    for cap in [o for o in bpy.data.objects if o.name.startswith("V5_NEW-01") and o.name.endswith("_cap")]:
        bb = [cap.matrix_world @ Vector(c) for c in cap.bound_box]
        x0, x1 = min(v.x for v in bb), max(v.x for v in bb); y0, y1 = min(v.y for v in bb), max(v.y for v in bb); zt = max(v.z for v in bb)
        segs = max(1, round((y1 - y0) / 1.25)); L = (y1 - y0) / segs
        wl = x0 < 1                                                   # wall on the low-x side (left bench) or high-x side
        cx0, cx1 = (x0 + 0.13, x1 - 0.015) if wl else (x0 + 0.015, x1 - 0.13)   # 0.13 m off the wall: clears wall-hung GOB-005
        for i in range(segs):
            rbox(cap.name + "_cushion", ((cx0 + cx1) / 2, y0 + L * (i + 0.5), zt + 0.045), (cx1 - cx0, L - 0.02, 0.08), "v5_linen_oat", None, 0.03, puff=0.10)
        wall_x = x0 + 0.07 if x0 < 1 else x1 - 0.07                   # pillows against the wall at the bench ends, beside the cushions
        for k, y in enumerate((y0 + 0.35, y1 - 0.35)):
            rbox(cap.name + "_pillow", (wall_x, y, zt + 0.205), (0.12, 0.40, 0.36), ("v5_linen_charcoal", "v5_linen_rust")[k], None, 0.05, puff=0.35,
                 rot=(0, math.radians(12 if x0 < 1 else -12), 0))

    # floor cushions by the fireside (positions from the lounge solver: stove clearance, kept-clear zones, legroom)
    LNG = json.load(open(os.path.join(g["ROOT"], "acoustics", "out", "lounge_layout.json")))["fireside_mode"]
    for k in ("floor cushion 1", "floor cushion 2"):
        if k in LNG:
            c = LNG[k]; o = rbox("V5_" + k.replace(" ", "_"), (c["centre"][0], c["centre"][1], 0.10), (c["size"][0], c["size"][1], 0.17),
                                 "v5_linen_charcoal" if k.endswith("1") else "v5_linen_oat", None, 0.05, puff=0.22, rot=(0, 0, math.radians(c["yaw_deg"])))
    return len([o for o in coll.objects if o.get("evidence_class") == EV])
