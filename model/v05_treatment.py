"""v0.5 additions to the approved v0.4 model (called from build_studio.py when BG_VERSION=v05).

Everything placed here comes from acoustics/out/placements.json (Clark assets, owner-measured body sizes),
acoustics/out/placements.json:new_items (NEW purpose-built treatment) and acoustics/out/lounge_layout.json
(owner-authorised fireside correction). No building geometry is changed.

Evidence tags on every object:
  asset_id, verification (owner sheet status), depth_provisional (True when the sheet has no depth -> 0.05 m),
  evidence_class = "PROPOSED placement; asset body OWNER-MEASURED" | "... body PROVISIONAL" | "PROPOSED (new build)".
Indicative detail (flagged in 'note'): DIF fin order, HYB perforation, wood-box wall thickness, gobo frames/casters.
"""
import json, math, os, random
import bpy

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
PLC = json.load(open(os.path.join(ROOT, "acoustics/out/placements.json")))
LNG = json.load(open(os.path.join(ROOT, "acoustics/out/lounge_layout.json")))
IN = 0.0254
CA = "35_V05_CLARK_ASSETS"; NW = "36_V05_NEW_TREATMENT"; LG = "37_V05_LOUNGE"

def build(g):
    box, poly_prism, cyl, col, mat, M = g["box"], g["poly_prism"], g["cyl"], g["col"], g["mat"], g["M"]
    W, D, AX = g["W"], g["D"], g["AX"]
    M.update({
     "v5_abs_blue": mat("v5_dead_room_blue_fabric", (0.10, 0.17, 0.33), 0.95, noise=(90, 0.05)),
     "v5_charcoal": mat("v5_charcoal_fabric", (0.13, 0.13, 0.14), 0.95, noise=(90, 0.05)),
     "v5_burlap": mat("v5_burlap", (0.52, 0.43, 0.30), 0.98, noise=(140, 0.12)),
     "v5_gobo": mat("v5_gobo_fabric", (0.22, 0.22, 0.23), 0.95, noise=(90, 0.05)),
     "v5_peg": mat("v5_pegboard", (0.70, 0.57, 0.40), 0.7, noise=(200, 0.15)),
     "v5_tan": mat("v5_sunny_tan", (0.64, 0.54, 0.40), 0.95, noise=(90, 0.05)),
     "v5_sblue": mat("v5_sunny_blue", (0.14, 0.24, 0.44), 0.95, noise=(90, 0.05)),
     "v5_fin": mat("v5_fin_wood", (0.56, 0.39, 0.22), 0.55, noise=(40, 0.2, (1, 1, 10))),
     "v5_foam": mat("v5_trap_fabric", (0.24, 0.24, 0.26), 0.95, noise=(90, 0.05)),
     "v5_perf": mat("v5_perforated_wood", (0.62, 0.47, 0.29), 0.6, noise=(260, 0.22)),
     "v5_rustic": mat("v5_rustic_wood", (0.38, 0.26, 0.16), 0.75, noise=(30, 0.3, (1, 1, 8))),
     "v5_new": mat("v5_new_lime_fabric", (0.74, 0.71, 0.65), 0.97, noise=(90, 0.03)),
     "v5_curtain": mat("v5_wool_curtain", (0.30, 0.29, 0.28), 1.0, noise=(30, 0.08, (1, 1, 0.2))),
     "v5_lounge": mat("v5_lounge_wool", (0.55, 0.42, 0.30), 0.95, noise=(60, 0.06)),
     "v5_leather": mat("v5_leather", (0.32, 0.18, 0.10), 0.5, noise=(20, 0.1)),
    })
    FABRIC = {"ABS-003": "v5_abs_blue", "PAN-001": "v5_charcoal", "PAN-002": "v5_charcoal", "ABS-001": "v5_charcoal", "ABS-015": "v5_charcoal", "ABS-016": "v5_charcoal",
              "ABS-005": "v5_tan", "ABS-008": "v5_tan", "ABS-011": "v5_tan", "ABS-007": "v5_tan", "ABS-009": "v5_sblue", "ABS-010": "v5_sblue",
              "ABS-012": "v5_sblue", "ABS-013": "v5_sblue"}
    def tag(o, p, extra=""):
        o["asset_id"] = p["asset"]; o["verification"] = p["verification"]; o["depth_provisional"] = bool(p["depth_provisional"])
        o["evidence_class"] = "PROPOSED placement; asset body " + ("PROVISIONAL depth" if p["depth_provisional"] else "OWNER-MEASURED")
        o["mount"] = p["install"]; o["air_gap_m"] = p["air_gap_m"]; o["reuse_mode"] = p["mode"]
        if p["note"] or extra: o["note"] = (p["note"] + " " + extra).strip()
        return o
    def holder(name, p):
        e = bpy.data.objects.new(name, None); col(CA).objects.link(e)
        e.location = p["centre"]; e.rotation_euler = [math.radians(a) for a in p["rot_deg"]]; return tag(e, p)
    def child(o, e, p, extra=""):
        o.parent = e; return tag(o, p, extra)
    count = {}
    for p in PLC["placements"]:
        a = p["asset"]; count[a] = count.get(a, 0) + 1; nm = f"V5_{a}_{count[a]}"
        sx, sy, sz = p["size"]; sh = p["shape"]; e = holder(nm, p)
        if sh == "panel":
            m = FABRIC.get(a, "v5_burlap" if a.startswith("GOB") else "v5_charcoal")
            child(box(nm + "_body", -sx/2, sx/2, -sy/2, sy/2, -sz/2, sz/2, m, CA, bevel=0.006), e, p)
            if p["zone"].endswith("cloud") or "ceiling" in p["zone"]:      # aircraft cables / cleat blocks to the structure above
                for cx, cy in ((-sx/2 + 0.08, -sy/2 + 0.15), (sx/2 - 0.08, -sy/2 + 0.15), (-sx/2 + 0.08, sy/2 - 0.15), (sx/2 - 0.08, sy/2 - 0.15)):
                    child(box(nm + "_hanger", cx - 0.003, cx + 0.003, cy - 0.003, cy + 0.003, sz/2, sz/2 + max(p["air_gap_m"], 0.02), "steel_black", CA), e, p)
        elif sh == "btr":    # tapered trap: 12 in deep at the floor -> 6.2 in at the top, solid wood back
            d0, d1 = 12 * IN, 6.2 * IN
            child(poly_prism(nm + "_foam", [(0.019, 0), (d0, 0), (d1, sz), (0.019, sz)], "X", -sx/2, sx/2, "v5_foam", CA), e, p)
            child(box(nm + "_back", -sx/2, sx/2, 0, 0.019, 0, sz, "v5_fin", CA), e, p)
        elif sh == "diffuser":   # wooden fin diffuser 52 x 80 x 5 in: back + frame + vertical fins (fin order INDICATIVE)
            dd = sy; child(box(nm + "_back", -sx/2, sx/2, -dd/2, -dd/2 + 0.012, -sz/2, sz/2, "v5_fin", CA), e, p)
            for xa, xb in ((-sx/2, -sx/2 + 0.025), (sx/2 - 0.025, sx/2)):
                child(box(nm + "_stile", xa, xb, -dd/2, dd/2, -sz/2, sz/2, "v5_fin", CA), e, p)
            for za, zb in ((-sz/2, -sz/2 + 0.025), (sz/2 - 0.025, sz/2)):
                child(box(nm + "_rail", -sx/2, sx/2, -dd/2, dd/2, za, zb, "v5_fin", CA), e, p)
            rnd = random.Random(a); n = 13
            for i in range(n):
                x = -sx/2 + 0.045 + i * (sx - 0.09) / (n - 1); proj = rnd.choice((0.35, 0.55, 0.75, 1.0, 0.65, 0.45))
                child(box(nm + "_fin", x - 0.009, x + 0.009, -dd/2 + 0.012, -dd/2 + 0.012 + proj * (dd - 0.012), -sz/2 + 0.025, sz/2 - 0.025, "v5_fin", CA), e, p,
                      "fin layout INDICATIVE: rebuild from DIF photos/fin schedule")
        elif sh == "hyb":    # perforated-wood barrel: 4 in at the edges, 9 in at the centre, open rear (local -Z = curved face)
            w, L, t = sx, sy, 0.019; e0, e1 = 4 * IN, 9 * IN
            outer = [(-w/2 + w * i / 24, -(e0 + (e1 - e0) * (1 - (2 * (-w/2 + w * i / 24) / w) ** 2))) for i in range(25)]
            inner = [(x * (w/2 - t) / (w/2), z + t) for x, z in outer][::-1]
            pts = [(-w/2, 0)] + outer + [(w/2, 0), (w/2 - t, 0)] + inner + [(-w/2 + t, 0)]
            o = poly_prism(nm + "_shell", pts, "Y", -L/2, L/2, "v5_perf", CA); o.location = (0, 0, sz/2)
            child(o, e, p, "barrel profile from 4/9 in depths (parabolic approximation of the curve); perforation not modelled")
            for yy in (-L/2 + 0.01, 0, L/2 - 0.01):
                o = poly_prism(nm + "_rib", [(-w/2, 0)] + outer + [(w/2, 0)], "Y", yy - 0.01, yy + 0.01, "v5_fin", CA); o.location = (0, 0, sz/2); child(o, e, p)
            if p["rot_deg"][0] == 0:   # horizontal: 30 in chains up to the ceiling
                for cx, cy in ((-w/2 + 0.05, -L/2 + 0.2), (w/2 - 0.05, -L/2 + 0.2), (-w/2 + 0.05, L/2 - 0.2), (w/2 - 0.05, L/2 - 0.2)):
                    child(box(nm + "_chain", cx - 0.005, cx + 0.005, cy - 0.005, cy + 0.005, sz/2, sz/2 + 30 * IN, "steel", CA), e, p)
        elif sh == "gobo_wheeled":   # panel + two feet + casters (frame INDICATIVE)
            under = 0.15 if a == "GOB-001" else 0.17
            m = "v5_peg" if a == "GOB-002" else "v5_gobo"
            child(box(nm + "_panel", -sx/2, sx/2, -sy/2, sy/2, -sz/2, sz/2, m, CA, bevel=0.005), e, p)
            for xs_ in (-sx/2 + 0.06, sx/2 - 0.06):
                child(box(nm + "_foot", xs_ - 0.025, xs_ + 0.025, -0.28, 0.28, -sz/2 - under + 0.06, -sz/2 - under + 0.10, "steel_black", CA), e, p)
                child(box(nm + "_upright", xs_ - 0.02, xs_ + 0.02, -0.02, 0.02, -sz/2 - under + 0.10, -sz/2, "steel_black", CA), e, p)
                for ys_ in (-0.25, 0.25):
                    o = cyl(nm + "_caster", 0.03, 0.025, (xs_, ys_, -sz/2 - under + 0.03), "steel_black", CA, rot=(0, math.pi/2, 0), verts=12); child(o, e, p)
        elif sh == "wood_box":   # open-backed hollow rustic box; open back to the wall (+X here), 15 mm boards (nominal)
            t = 0.015; fx = -sx/2   # room-facing side
            child(box(nm + "_face", fx, fx + t, -sy/2, sy/2, -sz/2, sz/2, "v5_rustic", CA), e, p, "board thickness nominal 15 mm (unknown)")
            for a0, a1 in ((-sy/2, -sy/2 + t), (sy/2 - t, sy/2)):
                child(box(nm + "_side", fx, sx/2, a0, a1, -sz/2, sz/2, "v5_rustic", CA), e, p)
            for a0, a1 in ((-sz/2, -sz/2 + t), (sz/2 - t, sz/2)):
                child(box(nm + "_rim", fx, sx/2, -sy/2, sy/2, a0, a1, "v5_rustic", CA), e, p)
    assert sum(count.values()) == PLC["allocated_units"], "model asset count != allocation"

    # ---------------------------------------------------------------- NEW purpose-built treatment
    for it in PLC["new_items"]:
        for k, gm in enumerate(it["geom"]):
            nm = f"V5_{it['id']}_{k}"
            if "tri" in gm:
                x0, y0, L = gm["tri"]; sxn = 1 if x0 == 0 else -1
                pts = [(x0, y0), (x0 + sxn * L, y0), (x0, y0 - L)]
                o = poly_prism(nm, pts if sxn < 0 else pts[::-1], "Z", 0, gm["h"], "v5_new", NW)
            else:
                (cx, cy, cz), (sx, sy, sz) = gm["centre"], gm["size"]
                mtl = {"NEW-03": "v5_curtain", "NEW-07": "fabric_dark"}.get(it["id"], "v5_new")
                o = box(nm, cx - sx/2, cx + sx/2, cy - sy/2, cy + sy/2, cz - sz/2, cz + sz/2, mtl, NW)
                if it["id"] == "NEW-01":   # reclaimed-wood bench cap (window bench), as v0.4
                    box(nm + "_cap", cx - sx/2, cx + sx/2, cy - sy/2, cy + sy/2, cz + sz/2, cz + sz/2 + 0.04, "reclaimed", NW, "PROPOSED (new build)", "reclaimed Clark wood cap / window bench")
                if it["id"] == "NEW-03":
                    box(nm + "_track", cx - sx/2 - 0.2, cx + sx/2 + 0.2, cy - 0.02, cy + 0.02, cz + sz/2, cz + sz/2 + 0.03, "steel_black", NW, "PROPOSED (new build)")
            o["evidence_class"] = "PROPOSED (new build)"; o["new_item"] = it["id"]; o["note"] = it["item"] + " — " + it["build"]

    # ---------------------------------------------------------------- corrected fireside lounge (faces the stove)
    def seat(name, cx, cy, yaw, w, d, kind):
        e = bpy.data.objects.new(name, None); col(LG).objects.link(e)
        parts = []
        if kind == "loveseat":
            parts += [box(name + "_base", -w/2, w/2, -d/2, d/2, 0.08, 0.42, "v5_lounge", LG), box(name + "_back", -w/2, w/2, -d/2, -d/2 + 0.20, 0.42, 0.80, "v5_lounge", LG)]
            parts += [box(name + "_arm", sx_ - 0.09, sx_ + 0.09, -d/2, d/2, 0.42, 0.62, "v5_lounge", LG) for sx_ in (-w/2 + 0.09, w/2 - 0.09)]
            parts += [box(name + "_leg", lx - 0.02, lx + 0.02, ly - 0.02, ly + 0.02, 0, 0.08, "walnut", LG) for lx in (-w/2 + 0.06, w/2 - 0.06) for ly in (-d/2 + 0.06, d/2 - 0.06)]
        else:   # swivel armchair on a pedestal with glides
            parts += [box(name + "_seat", -w/2 + 0.04, w/2 - 0.04, -d/2 + 0.04, d/2 - 0.04, 0.28, 0.44, "v5_leather", LG, bevel=0.03),
                      box(name + "_back", -w/2 + 0.04, w/2 - 0.04, -d/2 + 0.04, -d/2 + 0.18, 0.44, 0.80, "v5_leather", LG, bevel=0.03)]
            parts += [box(name + "_arm", sx_ - 0.05, sx_ + 0.05, -d/2 + 0.04, d/2 - 0.10, 0.44, 0.60, "v5_leather", LG) for sx_ in (-w/2 + 0.09, w/2 - 0.09)]
            parts += [cyl(name + "_pedestal", 0.05, 0.26, (0, 0, 0.15), "steel_black", LG, verts=16), cyl(name + "_disc", 0.30, 0.02, (0, 0, 0.01), "steel_black", LG, verts=32)]
        for o in parts: o.parent = e; o["evidence_class"] = "PROPOSED (owner-authorised lounge correction)"
        e.location = (cx, cy, 0); e.rotation_euler = (0, 0, math.radians(yaw)); e["evidence_class"] = "PROPOSED (owner-authorised lounge correction)"
        return e
    fs = LNG["fireside_mode"]; cm = LNG["cinema_mode"]
    ls = fs["loveseat"]; seat("V5_lounge_loveseat", *ls["centre"], ls["yaw_deg"], *ls["size"], "loveseat")
    ch = fs["swivel armchair A"]; A = seat("V5_swivel_armchair_A", *ch["centre"], ch["yaw_deg"], *ch["size"], "swivel")
    A["fireside_pose"] = [*ch["centre"], ch["yaw_deg"]]
    cA = cm["swivel armchair A (rolls back from the fire)"]; A["cinema_pose"] = [*cA["centre"], cA["yaw_deg"]]
    cB = cm["swivel armchair B (stays in the rear row)"]; seat("V5_swivel_armchair_B", *cB["centre"], cB["yaw_deg"], 0.80, 0.80, "swivel")
    tb = fs["side table"]["centre"]
    cyl("V5_lounge_side_table_top", 0.25, 0.03, (tb[0], tb[1], 0.50), "walnut", LG, verts=32); cyl("V5_lounge_side_table_stem", 0.03, 0.49, (tb[0], tb[1], 0.245), "steel_black", LG, verts=12)
    box("V5_lounge_rug", 1.45, 3.62, 5.05, 7.85, 0.012, 0.022, "rug", LG, "PROPOSED", "wool rug kept OFF the non-combustible hearth pad")
    return A

def set_mode(A, cinema):
    x, y, yaw = A["cinema_pose"] if cinema else A["fireside_pose"]
    A.location = (x, y, 0); A.rotation_euler = (0, 0, math.radians(yaw))

# ---------------------------------------------------------------- render-time scenarios (owner request 14 Nov)
# Applied AFTER the .blend is saved, so the saved v0.5 model always holds the full design.
#   BG_PHASE=1        control room phase 1: stereo only (the actual RL 901K pair); immersive 7.1.4 speakers and subs hidden
#   BG_LIVE_MODE=farm live room farm mode: piano on its dolly against the west wall, lid down, covered; gobos nested on the
#                     east wall; quartet chairs/stands put away; the painted 3.7 m aisle to the garage door is left clear
def _hide(ob):
    ob.hide_render = True
    for c in ob.children_recursive: c.hide_render = True
def apply_scenarios(g):
    box, col, AX = g["box"], g["col"], g["AX"]
    tags = []
    if os.environ.get("BG_PHASE") == "1":
        for ob in list(bpy.data.objects):
            if ob.name.startswith(("PR_imm_", "PR_sub_")): _hide(ob)
        tags.append("phase1")
    if os.environ.get("BG_LIVE_MODE") == "farm":
        F, LL, LR, YL = g["F_LIVE"], g["LIVE_L"], g["LIVE_R"], g["Y_LOFT_END"]
        pe = bpy.data.objects["PR_grand_piano"]
        pe.location = (LL + 1.15, YL + 3.05, F); pe.rotation_euler = (0, 0, 0)   # tail toward the garage end, flat side to the wall
        bpy.data.objects["PR_piano_lid"].rotation_euler = (0, 0, 0)
        box("FARM_piano_cover", LL + 1.15 - 0.82, LL + 1.15 + 0.82, YL + 3.05 - 0.22, YL + 3.05 + 2.20, F + 0.60, F + 1.03, "rug", "38_V05_SCENARIOS", "PROPOSED",
            "quilted piano cover on a locked dolly (NEW-06)")
        for ob in bpy.data.objects:
            if ob.name.startswith(("PR_quartet_", "V5_BL_")): ob.hide_render = True   # quartet (v0.4) / band backline packed away
        gob = sorted([o for o in bpy.data.objects if o.name.startswith(("V5_GOB-001_", "V5_GOB-002_")) and o.type == "EMPTY"], key=lambda o: o.name)
        for i, o in enumerate(gob):   # nested on the east wall of the tray zone, clear of the rustic wood wall and the aisle
            o.location = (LR - 0.33 - 0.17 * i, 29.05, o.location.z); o.rotation_euler = (0, 0, math.radians(90))
        tags.append("farm")
    return tags
