"""Fly-through animation: approach the entry, glide through the control room, corridor and live room, out of the
machinery door, then rise to a top-down reveal of the barn and the whole property.

    BG_VERSION=v05 BG_PHASE=1 BG_LOOK=photo BG_FLY=1 BG_PROPERTY_DIR=inputs/private/property python3 model/build_studio.py
      -> inputs/private/flythrough/frames/####.png  (then: python3 model/flythrough.py encode)

The property (fields, woods, pond, roads, trails, boundary) is read from a PRIVATE, gitignored folder: it is the
owner's layout, hand-traced from the owner's own maps and GPS track, INDICATIVE only (not a survey). Nothing about the
property is stored in this public script. Satellite imagery is not used. The barn and its interior are the v0.5 model.
Render-time only: nothing here is saved into the .blend.
Env: BG_FLY_RES (e.g. 1280x720), BG_FLY_SAMPLES (24), BG_FLY_FRAMES (e.g. 0-1199 or a comma list for tests).
"""
import json, math, os, sys
import bpy
from mathutils import Vector, Matrix

FPS = 24

def _layout(g):
    d = os.environ.get("BG_PROPERTY_DIR")
    if not d:
        return None, None
    d = d if os.path.isabs(d) else os.path.join(g["ROOT"], d)
    return json.load(open(os.path.join(d, "layout.json"))), d

def _to_world(L, u, v):
    s = L["m_per_px"]; b = L["barn"]
    return Vector(((v - b["centre_v"]) * s + 5.8, (u - b["entry_gable_u"]) * s - 0.25))   # +X = map down (south), +Y = map right (east)

def _height(x, y, g, L):
    """Gentle indicative relief (no survey): flat around the barn, a shallow basin at the pond, soft rolling elsewhere."""
    r = math.hypot(x - 5.8, y - 15.0)
    z = 2.2 * math.sin(x / 140.0 + 0.7) * math.cos(y / 170.0 - 0.3) + 1.2 * math.sin((x + y) / 75.0)
    flat = max(0.0, min(1.0, (r - 35.0) / 60.0))
    z *= flat
    pc = _to_world(L, *L["pond"]["c"]); pr = L["pond"]["r"][1] * L["m_per_px"]
    dp = math.hypot(x - pc.x, y - pc.y)
    if dp < pr * 2.2:
        z -= 2.5 * (1 - dp / (pr * 2.2)) ** 2
    return g["GROUND"] - 0.01 + z

def build_property(g):
    L, d = _layout(g)
    if not L:
        print("flythrough: no BG_PROPERTY_DIR; property not built"); return None
    W0, H0 = L["px_size"]; s = L["m_per_px"]
    # --- terrain grid over the map extent (5 m), landcover image draped by UV
    step = 6.0; margin = Vector((900.0, 1150.0))   # generic woods beyond the traced map so the ~3 km-wide overhead frame is filled edge to edge
    c0 = _to_world(L, 0, 0) - margin; c1 = _to_world(L, W0, H0) + margin
    xs = [c0.x + i * step for i in range(int((c1.x - c0.x) / step) + 1)]; ys = [c0.y + j * step for j in range(int((c1.y - c0.y) / step) + 1)]
    verts, uvs, faces = [], [], []
    for i, x in enumerate(xs):
        for j, y in enumerate(ys):
            verts.append((x, y, _height(x, y, g, L)))
    nx, ny = len(xs), len(ys)
    for i in range(nx - 1):
        for j in range(ny - 1):
            a = i * ny + j; faces.append((a, a + ny, a + ny + 1, a + 1))
    me = bpy.data.meshes.new("FLY_terrain"); me.from_pydata(verts, [], faces); me.update()
    uvl = me.uv_layers.new(name="map")
    for p in me.polygons:
        for li in p.loop_indices:
            vx, vy, _ = verts[me.loops[li].vertex_index]
            u = (vy + 0.25) / s + L["barn"]["entry_gable_u"]; v = (vx - 5.8) / s + L["barn"]["centre_v"]
            uvl.data[li].uv = (u / W0, 1.0 - v / H0)
    for p in me.polygons: p.use_smooth = True
    ter = bpy.data.objects.new("FLY_terrain", me); bpy.context.scene.collection.objects.link(ter)
    ter["evidence_class"] = "INDICATIVE property context (owner maps, hand-traced; private)"
    # forest weight per vertex from the landcover raster (dark green = woods)
    from PIL import Image
    lc = Image.open(os.path.join(d, "landcover.png")).convert("RGB"); LW, LH = lc.size; px = lc.load()
    fw = me.attributes.new("forest", "FLOAT", "POINT")
    barn_c = Vector((5.8, 15.0))
    for k, (vx, vy, _) in enumerate(verts):
        u = ((vy + 0.25) / s + L["barn"]["entry_gable_u"]) / W0 * LW; v = ((vx - 5.8) / s + L["barn"]["centre_v"]) / H0 * LH
        if 0 <= u < LW and 0 <= v < LH:
            r_, g_, b_ = px[int(u), int(v)]
            f = 1.0 if (g_ < 75 and r_ < 60) else 0.0
        else:
            f = 1.0
        if (Vector((vx, vy)) - barn_c).length < 30: f = 0.0
        fw.data[k].value = f
    # terrain material: landcover colours x photo grass detail
    m = bpy.data.materials.new("fly_terrain"); m.use_nodes = True; nt = m.node_tree
    for n in list(nt.nodes): nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial"); bs = nt.nodes.new("ShaderNodeBsdfPrincipled"); nt.links.new(bs.outputs["BSDF"], out.inputs["Surface"])
    tex = nt.nodes.new("ShaderNodeTexImage"); tex.image = bpy.data.images.load(os.path.join(d, "landcover.png")); tex.interpolation = "Cubic"
    uvn = nt.nodes.new("ShaderNodeUVMap"); uvn.uv_map = "map"; nt.links.new(uvn.outputs["UV"], tex.inputs["Vector"])
    tex.extension = "CLIP"   # no tiling: outside the traced map the ground reads as generic woods (QA: the map tiled into a ghost copy)
    fpx = [px[i, j] for i in range(0, LW, 7) for j in range(0, LH, 7) if px[i, j][1] < 75 and px[i, j][0] < 60]
    fcol = tuple(sum(c[k] for c in fpx) / len(fpx) / 255.0 for k in range(3)) if fpx else (0.157, 0.235, 0.118)
    fcol = tuple(((c + 0.055) / 1.055) ** 2.4 for c in fcol)   # sRGB -> linear, as the image texture is decoded
    outside = nt.nodes.new("ShaderNodeMixRGB"); outside.inputs["Color1"].default_value = (*fcol, 1.0)
    nt.links.new(tex.outputs["Alpha"], outside.inputs["Fac"]); nt.links.new(tex.outputs["Color"], outside.inputs["Color2"])
    ramp_in = outside.outputs["Color"]
    grass = bpy.data.materials.get("ex_ground_grass") or None
    det = nt.nodes.new("ShaderNodeTexNoise"); det.inputs["Scale"].default_value = 0.08; det.inputs["Detail"].default_value = 8
    geo = nt.nodes.new("ShaderNodeNewGeometry"); nt.links.new(geo.outputs["Position"], det.inputs["Vector"])
    mr = nt.nodes.new("ShaderNodeMapRange"); mr.inputs["To Min"].default_value = 0.75; mr.inputs["To Max"].default_value = 1.2; nt.links.new(det.outputs["Fac"], mr.inputs["Value"])
    import lookdev as _ld
    gp = _ld._asset("textures", "leafy_grass", "Diffuse")
    if gp:   # close-range detail: photo grass luminance (world-mapped, 4 m tile) modulates the landcover colour
        sp_ = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(geo.outputs["Position"], sp_.inputs["Vector"])
        cxy = nt.nodes.new("ShaderNodeCombineXYZ"); nt.links.new(sp_.outputs["X"], cxy.inputs["X"]); nt.links.new(sp_.outputs["Y"], cxy.inputs["Y"])
        mpg = nt.nodes.new("ShaderNodeMapping"); mpg.inputs["Scale"].default_value = (0.25, 0.25, 0.25); nt.links.new(cxy.outputs["Vector"], mpg.inputs["Vector"])
        gt = nt.nodes.new("ShaderNodeTexImage"); gt.image = bpy.data.images.load(gp, check_existing=True); nt.links.new(mpg.outputs["Vector"], gt.inputs["Vector"])
        bw = nt.nodes.new("ShaderNodeRGBToBW"); nt.links.new(gt.outputs["Color"], bw.inputs["Color"])
        mr2 = nt.nodes.new("ShaderNodeMapRange"); mr2.inputs["From Min"].default_value = 0.05; mr2.inputs["From Max"].default_value = 0.35
        mr2.inputs["To Min"].default_value = 0.55; mr2.inputs["To Max"].default_value = 1.45; nt.links.new(bw.outputs["Val"], mr2.inputs["Value"])
        mm_ = nt.nodes.new("ShaderNodeMath"); mm_.operation = "MULTIPLY"; nt.links.new(mr.outputs["Result"], mm_.inputs[0]); nt.links.new(mr2.outputs["Result"], mm_.inputs[1])
        mr = type("R", (), {"outputs": {"Result": mm_.outputs["Value"]}})()
    mul = nt.nodes.new("ShaderNodeMixRGB"); mul.blend_type = "MULTIPLY"; mul.inputs["Fac"].default_value = 1.0
    gm = nt.nodes.new("ShaderNodeGamma"); gm.inputs["Gamma"].default_value = 2.2; nt.links.new(ramp_in, gm.inputs["Color"])
    cb = nt.nodes.new("ShaderNodeCombineXYZ")
    for k_ in "XYZ": nt.links.new(mr.outputs["Result"], cb.inputs[k_])
    nt.links.new(gm.outputs["Color"], mul.inputs["Color1"]); nt.links.new(cb.outputs["Vector"], mul.inputs["Color2"])
    nt.links.new(mul.outputs["Color"], bs.inputs["Base Color"]); bs.inputs["Roughness"].default_value = 0.95
    me.materials.append(m)
    # far ground: a wide plane just below the terrain so the top-down reveal never shows the terrain's edge (same material, woods colour)
    R = 6000.0; mc = (c0 + c1) / 2; fz = g["GROUND"] - 6.0
    fv = [(mc.x - R, mc.y - R, fz), (mc.x + R, mc.y - R, fz), (mc.x + R, mc.y + R, fz), (mc.x - R, mc.y + R, fz)]
    fme = bpy.data.meshes.new("FLY_far_ground"); fme.from_pydata(fv, [], [(0, 1, 2, 3)]); fme.update()
    ful = fme.uv_layers.new(name="map")
    for li, lp in enumerate(fme.loops):
        vx, vy, _ = fv[lp.vertex_index]
        u = (vy + 0.25) / s + L["barn"]["entry_gable_u"]; v = (vx - 5.8) / s + L["barn"]["centre_v"]
        ful.data[li].uv = (u / W0, 1.0 - v / H0)
    fme.materials.append(m); far = bpy.data.objects.new("FLY_far_ground", fme); bpy.context.scene.collection.objects.link(far)
    far["evidence_class"] = "INDICATIVE context (generic woods beyond the traced map)"
    # pond water
    pc = _to_world(L, *L["pond"]["c"]); pr = (L["pond"]["r"][1] * s, L["pond"]["r"][0] * s)
    bpy.ops.mesh.primitive_circle_add(vertices=64, radius=1.0, fill_type="NGON", location=(pc.x, pc.y, g["GROUND"] - 1.4))
    pond = bpy.context.active_object; pond.name = "FLY_pond"; pond.scale = (pr[0], pr[1], 1)
    wm = bpy.data.materials.new("fly_water"); wm.use_nodes = True
    wb = next(n for n in wm.node_tree.nodes if n.type == "BSDF_PRINCIPLED"); wb.inputs["Base Color"].default_value = (0.02, 0.05, 0.05, 1)
    wb.inputs["Roughness"].default_value = 0.04; wb.inputs["Specular IOR Level"].default_value = 0.6; pond.data.materials.append(wm)
    # other buildings: neutral massing only (indicative; no invented architecture)
    bm_ = bpy.data.materials.new("fly_building"); bm_.use_nodes = True
    next(n for n in bm_.node_tree.nodes if n.type == "BSDF_PRINCIPLED").inputs["Base Color"].default_value = (0.55, 0.53, 0.50, 1)
    for k, b in enumerate(L["buildings"]):
        c = _to_world(L, *b["c"]); sx, sy = b["s"][1] * s, b["s"][0] * s
        bpy.ops.mesh.primitive_cube_add(size=1, location=(c.x, c.y, _height(c.x, c.y, g, L) + 2.5))
        o = bpy.context.active_object; o.name = f"FLY_building_{k}"; o.scale = (sx, sy, 5.0); o.rotation_euler = (0, 0, math.radians(b["rot"])); o.data.materials.append(bm_)
    # trees: CC0 fir variants + hardwood (autumn variants) instanced on the woods by geometry nodes
    tcoll = bpy.data.collections.new("FLY_tree_templates"); bpy.context.scene.collection.children.link(tcoll)
    for o in [o for o in bpy.data.objects if o.get("evidence_class", "").startswith("LOOKDEV context") and o.type == "MESH" and o.data.users > 1]:
        pass
    src = {}
    for o in bpy.data.objects:   # one template per distinct tree mesh used by the look-dev treeline
        if o.get("evidence_class", "").startswith("LOOKDEV context") and o.type == "MESH" and o.name.split(".")[0] not in ("LOOKDEV_ground_far",) \
                and not o.name.startswith(("LOOKDEV_grass", "LOOKDEV_ground")) and o.data.name not in src:
            src[o.data.name] = o
    for k, o in enumerate(src.values()):
        t = o.copy(); t.location = (0, 0, 0); t.rotation_euler = (0, 0, 0)
        t.scale = (2.6, 2.6, 2.6) if "tree_small" in o.data.name else (1.0, 1.0, 1.0)
        tcoll.objects.link(t)
    tcoll.hide_render = True
    ng = bpy.data.node_groups.new("FLY_forest", "GeometryNodeTree")
    ng.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    N = ng.nodes; Lk = ng.links
    gi = N.new("NodeGroupInput"); go = N.new("NodeGroupOutput")
    na = N.new("GeometryNodeInputNamedAttribute"); na.data_type = "FLOAT"; na.inputs["Name"].default_value = "forest"
    dp = N.new("GeometryNodeDistributePointsOnFaces"); dp.distribute_method = "RANDOM"; dp.inputs["Density"].default_value = 0.035; dp.inputs["Seed"].default_value = 11
    Lk.new(gi.outputs[0], dp.inputs["Mesh"]); Lk.new(na.outputs["Attribute"], dp.inputs["Selection"])   # woods only (attribute 1/0)
    ci = N.new("GeometryNodeCollectionInfo"); ci.inputs["Collection"].default_value = tcoll; ci.inputs["Separate Children"].default_value = True; ci.inputs["Reset Children"].default_value = True
    io = N.new("GeometryNodeInstanceOnPoints"); io.inputs["Pick Instance"].default_value = True
    rv = N.new("FunctionNodeRandomValue"); rv.data_type = "INT"; rv.inputs["Min"].default_value = 0; rv.inputs["Max"].default_value = max(0, len(src) - 1)
    rr = N.new("FunctionNodeRandomValue"); rr.data_type = "FLOAT_VECTOR"; rr.inputs["Min"].default_value = (0, 0, 0); rr.inputs["Max"].default_value = (0, 0, 6.283)
    rs = N.new("FunctionNodeRandomValue"); rs.data_type = "FLOAT"; rs.inputs["Min"].default_value = 0.75; rs.inputs["Max"].default_value = 1.15
    Lk.new(dp.outputs["Points"], io.inputs["Points"]); Lk.new(ci.outputs[0], io.inputs["Instance"])
    Lk.new(rv.outputs["Value"], io.inputs["Instance Index"]); Lk.new(rr.outputs["Value"], io.inputs["Rotation"]); Lk.new(rs.outputs["Value"], io.inputs["Scale"])
    jn = N.new("GeometryNodeJoinGeometry"); Lk.new(gi.outputs[0], jn.inputs[0]); Lk.new(io.outputs["Instances"], jn.inputs[0]); Lk.new(jn.outputs[0], go.inputs[0])
    mod = ter.modifiers.new("forest", "NODES"); mod.node_group = ng
    # owner's boundary as a floating map annotation above the canopy (fades in at the end)
    bnd = [_to_world(L, u, v) for u, v in L["boundary"]]
    cu = bpy.data.curves.new("FLY_boundary", "CURVE"); cu.dimensions = "3D"; cu.bevel_depth = 1.6
    sp = cu.splines.new("POLY"); sp.points.add(len(bnd)); sp.use_cyclic_u = True
    for i, p in enumerate(bnd + [bnd[0]]): sp.points[i].co = (p.x, p.y, g["GROUND"] + 32.0, 1)
    bo = bpy.data.objects.new("FLY_boundary", cu); bpy.context.scene.collection.objects.link(bo)
    bmat = bpy.data.materials.new("fly_boundary"); bmat.use_nodes = True; bnt = bmat.node_tree
    for n in list(bnt.nodes): bnt.nodes.remove(n)
    bout = bnt.nodes.new("ShaderNodeOutputMaterial"); em = bnt.nodes.new("ShaderNodeEmission"); em.inputs["Color"].default_value = (0.95, 0.12, 0.08, 1); em.inputs["Strength"].default_value = 6
    tr = bnt.nodes.new("ShaderNodeBsdfTransparent"); mx = bnt.nodes.new("ShaderNodeMixShader"); mx.name = "fade"
    bnt.links.new(tr.outputs[0], mx.inputs[1]); bnt.links.new(em.outputs[0], mx.inputs[2]); bnt.links.new(mx.outputs[0], bout.inputs["Surface"])
    cu.materials.append(bmat)
    # hide the look-dev stand-ins that the real property replaces
    for o in bpy.data.objects:
        if o.name.startswith("LOOKDEV_ground_far") or (o.get("evidence_class", "").startswith("LOOKDEV context") and o.type == "MESH"
                                                       and not o.name.startswith("LOOKDEV_grass")):
            o.hide_render = True
    centre = _to_world(L, *[sum(c) / len(c) for c in zip(*L["boundary"])])
    ext = [_to_world(L, u, v) for u, v in L["boundary"]]
    return {"centre": centre, "span_x": max(p.x for p in ext) - min(p.x for p in ext), "span_y": max(p.y for p in ext) - min(p.y for p in ext),
            "fade": mx}

def camera_path(g, prop):
    """Waypoints (seconds, camera, look-at). Interior heights stay under the doorway / loft / middle-zone ceilings."""
    AX, D, F_MID, F_LIVE = g["AX"], g["D"], g["F_MID"], g["F_LIVE"]
    P = g["P"]; xd = (P["CR1.xd1"] + P["CR1.xd2"]) / 2
    yM1, yLE, yLG = g["Y_MID1"], g["Y_LOFT_END"], g["Y_LIVE_G"]
    ent = 5.885
    W = [
     (0.0,  (ent - 7.0, -26.0, 1.9), (ent, 0.0, 1.8)),
     (5.0,  (ent - 0.6, -6.5, 1.75), (ent, 2.0, 1.6)),
     (8.0,  (ent, -0.6, 1.62), (ent, 4.0, 1.45)),
     (11.5, (ent - 0.2, 2.2, 1.75), (AX, 7.8, 1.25)),           # over the sofa toward the console and the Geithains
     (15.5, (AX - 0.3, 4.4, 1.55), (AX, 8.0, 1.35)),             # at the mix position
     (19.5, (xd - 0.9, 6.0, 1.5), (g["xs"], g["ys"], 0.6)),     # turn to the fireside
     (23.0, (xd, D - 0.6, 1.5), (xd, D + 3.0, 1.45)),            # line up on the doorway
     (25.0, (xd + 0.15, D + 0.9, 1.45 + F_MID), (AX, D + 5.0, 1.4 + F_MID)),
     (29.0, (AX, (D + yM1) / 2, 1.45 + F_MID), (AX, yM1 + 3.0, 1.4 + F_LIVE)),
     (32.5, (AX, yM1 + 1.6, 1.55 + F_LIVE), (AX + 3.2, yLE + 1.4, 0.6 + F_LIVE)),   # into the live room, toward the band
     (37.0, (AX + 0.3, yLE - 0.6, 1.85 + F_LIVE), (AX + 3.4, yLE + 1.5, 0.6 + F_LIVE)),    # beside the drum booth
     (41.0, (AX - 0.4, yLG - 2.2, 1.9 + F_LIVE), (AX, yLG + 12.0, 1.6 + F_LIVE)),    # toward the open machinery door
     (44.0, (AX, yLG + 6.0, 3.5), (AX, yLG + 30.0, 2.0)),        # out into the field
     (49.0, (AX + 22.0, yLG + 40.0, 45.0), (AX, 15.0, 0.0)),     # rise and turn back to the barn
    ]
    if prop:
        c = prop["centre"]; half = max(prop["span_x"] * 0.58, prop["span_y"] * 1.0)
        alt = half / math.tan(math.radians(16.1))                  # 35 mm on a 36 mm sensor, 16:9 vertical half-FOV
        W += [(55.0, (c.x * 0.4 + 5.8 * 0.6, c.y * 0.4 + 15 * 0.6, alt * 0.35), (5.8, 15.0, 0.0)),
              (62.0, (c.x + 2.0, c.y, alt), (c.x - 2.0, c.y, 0.0)),   # top-down, north up (target nudged north to fix the roll)
              (66.0, (c.x + 2.0, c.y, alt), (c.x - 2.0, c.y, 0.0))]
    return W

def setup_animation(g, prop):
    scene = bpy.context.scene; scene.render.fps = FPS
    cam = bpy.data.objects.new("CAM_fly", bpy.data.cameras.new("CAM_fly")); scene.collection.objects.link(cam)
    tgt = bpy.data.objects.new("TGT_fly", None); scene.collection.objects.link(tgt)
    cam.data.sensor_width = 36; cam.data.clip_start = 0.05; cam.data.clip_end = 20000
    tc = cam.constraints.new("TRACK_TO"); tc.target = tgt; tc.track_axis = "TRACK_NEGATIVE_Z"; tc.up_axis = "UP_Y"
    W = camera_path(g, prop)
    for t, loc, look in W:
        f = round(t * FPS); cam.location = loc; tgt.location = look
        cam.keyframe_insert("location", frame=f); tgt.keyframe_insert("location", frame=f)
        cam.data.lens = 22.0 if t < 47 else 35.0; cam.data.keyframe_insert("lens", frame=f)
    for ob in (cam, tgt, cam.data):
        ad = ob.animation_data
        if ad and ad.action:
            for fc in getattr(ad.action, "fcurves", []):
                for kp in fc.keyframe_points: kp.interpolation = "BEZIER"; kp.handle_left_type = kp.handle_right_type = "AUTO"
    scene.camera = cam; scene.frame_start = 0; scene.frame_end = round(W[-1][0] * FPS)
    # exposure / sky: exterior -> interior -> exterior
    vs = scene.view_settings
    for t, ex in ((0, -0.55), (7.0, -0.55), (9.5, 0.5), (40.5, 0.5), (43.5, -0.45), (50.0, 0.1), (58.0, 0.9), (66, 0.9)):
        vs.exposure = ex; vs.keyframe_insert("exposure", frame=round(t * FPS))
    wnt = scene.world.node_tree; bgn = next((n for n in wnt.nodes if n.type == "BACKGROUND"), None)
    if bgn:   # sky fill: exterior calibration outside, interior calibration inside (see lookdev HDRI gains)
        out_s = bgn.inputs["Strength"].default_value
        for t, v in ((0, out_s), (7.0, out_s), (9.5, out_s * 4.5), (40.5, out_s * 4.5), (43.5, out_s), (50.0, out_s * 1.6), (58.0, out_s * 3.0), (66, out_s * 3.0)):
            bgn.inputs["Strength"].default_value = v; bgn.inputs["Strength"].keyframe_insert("default_value", frame=round(t * FPS))
    if prop:
        fade = prop["fade"]
        for t, v in ((0, 0.0), (57.0, 0.0), (61.0, 1.0)):
            fade.inputs["Fac"].default_value = v; fade.inputs["Fac"].keyframe_insert("default_value", frame=round(t * FPS))
    cam.data.dof.use_dof = False
    return cam

def prepare(g):
    """Called by build_studio after the look pass when BG_FLY=1."""
    import lookdev
    lookdev.per_view(g, "ext_entry", False)                      # exterior daylight sun + sky
    for L_ in bpy.data.lights:                                      # interior lights on (studio in use)
        if L_.type == "AREA": L_.energy = L_.get("base_energy", L_.energy)
    for n in g["M"]["cove"].node_tree.nodes:
        if n.type == "BSDF_PRINCIPLED": n.inputs["Emission Strength"].default_value = 3.5
    for nm in ("DOOR_DARK_gable_entry_door",):                    # entry door stands open for the walk-in
        o = bpy.data.objects.get(nm)
        if o: o.hide_render = True
    for o in bpy.data.objects:                                      # door curtain drawn back; screen retracted; look-dev lawn patches off
        if o.name.startswith(("V5_NEW-03", "LOOKDEV_grass")): o.hide_render = True
        if o.users_collection and o.users_collection[0].name.startswith("32_PROPOSED_SCREEN"): o.hide_render = True
    for o in bpy.data.objects:                                      # interior/exterior shell visible as in exterior views
        if o.name.startswith(("EX_roof_metal", "EX_siding")): o.visible_camera = True
    prop = build_property(g)
    cam = setup_animation(g, prop)
    sc = bpy.context.scene; c = sc.cycles
    rx, ry = os.environ.get("BG_FLY_RES", "1280x720").split("x"); sc.render.resolution_x, sc.render.resolution_y = int(rx), int(ry)
    c.samples = int(os.environ.get("BG_FLY_SAMPLES", 24)); c.use_denoising = True; c.adaptive_threshold = 0.03
    sc.render.use_persistent_data = True
    return cam

def render(g):
    sc = bpy.context.scene
    out = os.path.join(g["ROOT"], "inputs", "private", "flythrough", "frames"); os.makedirs(out, exist_ok=True)
    spec = os.environ.get("BG_FLY_FRAMES", f"{sc.frame_start}-{sc.frame_end}")
    frames = []
    for part in spec.split(","):
        st = 1
        if ":" in part: part, st = part.split(":"); st = int(st)
        if "-" in part: a, b = map(int, part.split("-")); frames += list(range(a, b + 1, st))
        else: frames.append(int(part))
    for f in frames:
        p = os.path.join(out, f"{f:04d}.png")
        if os.path.exists(p) and not os.environ.get("BG_FLY_OVERWRITE"): continue   # resumable
        sc.frame_set(f); sc.render.filepath = p; bpy.ops.render.render(write_still=True); print("frame", f, flush=True)

def encode(root, step=2):
    """Frames rendered every `step` frames are re-numbered and motion-interpolated back to 24 fps."""
    base = os.path.join(root, "inputs", "private", "flythrough"); fr = os.path.join(base, "frames"); seq = os.path.join(base, "seq")
    os.makedirs(seq, exist_ok=True)
    for f in os.listdir(seq): os.remove(os.path.join(seq, f))
    names = sorted(f for f in os.listdir(fr) if f.endswith(".png"))
    for i, n in enumerate(names): os.symlink(os.path.join(fr, n), os.path.join(seq, f"{i:04d}.png"))
    mp4 = os.path.join(base, "breakglass_east_flythrough.mp4")
    vf = f'-vf "minterpolate=fps={FPS}:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1"' if step > 1 else ""
    os.system(f'ffmpeg -y -framerate {FPS / step} -i "{seq}/%04d.png" {vf} -c:v libx264 -pix_fmt yuv420p -crf 18 -preset slow "{mp4}"'); print(mp4)

if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "encode":
    encode(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
