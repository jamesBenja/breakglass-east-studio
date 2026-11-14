"""Presentation look-development pass (BG_LOOK=photo). Materials, lighting and render settings ONLY.

No building object is moved, removed or reshaped: geometry and the saved .blend are exactly the v0.5 model
(the look is applied after saving). Added presentation items, all tagged LOOKDEV and never saved:
a fire-glow emitter in the existing stove door; thin white window/door casings, an eave fascia and an entry lamp
(type/colour PHOTO-OBSERVED in the owner's site photos); and indicative site context (lawn, foreground grass strands,
a distant treeline, procedural clouds) that is not surveyed. The modelled EX_ground box is swapped for a seamless
disk at the same grade in look renders only. Materials express the documented design intent (oak floor, pale
plaster tones, wool, burlap, walnut, concrete); existing-finish appearance (U9) stays a neutral matte paint
because the real lining is unknown — no panel seams or textures are invented for it.
Textures are procedural (no external downloads), mapped in world space so they are continuous across objects.
"""
import math
import bpy

def _clear(m):
    nt = m.node_tree
    for n in list(nt.nodes): nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial"); bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return nt, bsdf, out

def _pos(nt, scale):
    geo = nt.nodes.new("ShaderNodeNewGeometry"); mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = scale
    nt.links.new(geo.outputs["Position"], mp.inputs["Vector"]); return mp.outputs["Vector"]

def _bevel_bump(nt, bsdf, height=None, strength=0.15, radius=0.004, distance=0.002):
    bev = nt.nodes.new("ShaderNodeBevel"); bev.inputs["Radius"].default_value = radius; bev.samples = 4
    if height is None:
        nt.links.new(bev.outputs["Normal"], bsdf.inputs["Normal"]); return
    bump = nt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = strength; bump.inputs["Distance"].default_value = distance
    nt.links.new(height, bump.inputs["Height"]); nt.links.new(bev.outputs["Normal"], bump.inputs["Normal"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])

def _ramp(nt, fac, c0, c1):
    r = nt.nodes.new("ShaderNodeValToRGB")
    r.color_ramp.elements[0].color = (*c0, 1); r.color_ramp.elements[1].color = (*c1, 1)
    nt.links.new(fac, r.inputs["Fac"]); return r.outputs["Color"]

def _noise(nt, vec, scale, detail=6, rough=0.55):
    n = nt.nodes.new("ShaderNodeTexNoise"); n.inputs["Scale"].default_value = scale; n.inputs["Detail"].default_value = detail
    n.inputs["Roughness"].default_value = rough; nt.links.new(vec, n.inputs["Vector"]); return n.outputs["Fac"]

def matte(m, rgb, rough=0.85, var=0.04, bump=0.05, scale=6.0, sheen=0.0, metal=0.0):
    nt, b, _ = _clear(m)
    f = _noise(nt, _pos(nt, (1, 1, 1)), scale)
    nt.links.new(_ramp(nt, f, [c * (1 - var) for c in rgb], [min(1, c * (1 + var)) for c in rgb]), b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = rough; b.inputs["Metallic"].default_value = metal
    if sheen: b.inputs["Sheen Weight"].default_value = sheen
    _bevel_bump(nt, b, _noise(nt, _pos(nt, (1, 1, 1)), scale * 30, 4) if bump else None, strength=bump)

def fabric(m, rgb, weave=380.0, sheen=0.35, var=0.05):
    nt, b, _ = _clear(m)
    vec = _pos(nt, (1, 1, 1))
    w1 = nt.nodes.new("ShaderNodeTexWave"); w1.inputs["Scale"].default_value = weave; w1.bands_direction = "X"
    w2 = nt.nodes.new("ShaderNodeTexWave"); w2.inputs["Scale"].default_value = weave; w2.bands_direction = "Z"
    nt.links.new(vec, w1.inputs["Vector"]); nt.links.new(vec, w2.inputs["Vector"])
    mix = nt.nodes.new("ShaderNodeMath"); mix.operation = "MULTIPLY"
    nt.links.new(w1.outputs["Fac"], mix.inputs[0]); nt.links.new(w2.outputs["Fac"], mix.inputs[1])
    f = _noise(nt, vec, 3.0)
    nt.links.new(_ramp(nt, f, [c * (1 - var) for c in rgb], [min(1, c * (1 + var)) for c in rgb]), b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.95; b.inputs["Sheen Weight"].default_value = sheen
    _bevel_bump(nt, b, mix.outputs["Value"], strength=0.25, radius=0.008)

def planks(m, light, dark, plank_w=0.19, plank_l=1.9, rough=0.42):
    """Oak plank floor (proposed finish): brick texture on world XY + stretched grain."""
    nt, b, _ = _clear(m)
    vec = _pos(nt, (1, 1, 1))
    br = nt.nodes.new("ShaderNodeTexBrick"); br.offset = 0.37
    br.inputs["Scale"].default_value = 1.0; br.inputs["Mortar Size"].default_value = 0.0025; br.inputs["Brick Width"].default_value = plank_l
    br.inputs["Row Height"].default_value = plank_w; br.inputs["Color1"].default_value = (*light, 1); br.inputs["Color2"].default_value = (*dark, 1)
    br.inputs["Mortar"].default_value = (*[c * 0.45 for c in dark], 1)
    sw = nt.nodes.new("ShaderNodeSeparateXYZ"); cm = nt.nodes.new("ShaderNodeCombineXYZ")   # planks run along Y (the room axis)
    nt.links.new(vec, sw.inputs["Vector"]); nt.links.new(sw.outputs["Y"], cm.inputs["X"]); nt.links.new(sw.outputs["X"], cm.inputs["Y"])
    nt.links.new(cm.outputs["Vector"], br.inputs["Vector"])
    gm = nt.nodes.new("ShaderNodeMapping"); gm.inputs["Scale"].default_value = (2.0, 60.0, 2.0)
    nt.links.new(cm.outputs["Vector"], gm.inputs["Vector"])
    grain = _noise(nt, gm.outputs["Vector"], 3.0, 10, 0.6)
    mul = nt.nodes.new("ShaderNodeMixRGB"); mul.blend_type = "MULTIPLY"; mul.inputs["Fac"].default_value = 0.35
    nt.links.new(br.outputs["Color"], mul.inputs["Color1"]); nt.links.new(_ramp(nt, grain, (0.75, 0.72, 0.68), (1, 1, 1)), mul.inputs["Color2"])
    nt.links.new(mul.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = rough; b.inputs["Coat Weight"].default_value = 0.15
    _bevel_bump(nt, b, br.outputs["Fac"], strength=0.08)

def wood(m, rgb, axis="Z", rough=0.5, var=0.22, ring=40.0):
    """Long-grain wood (walnut, reclaimed, posts, joists, fins)."""
    nt, b, _ = _clear(m)
    s = {"X": (1.0, 25.0, 25.0), "Y": (25.0, 1.0, 25.0), "Z": (25.0, 25.0, 1.0)}[axis]
    vec = _pos(nt, s)
    f = _noise(nt, vec, 2.5, 12, 0.62)
    w = nt.nodes.new("ShaderNodeTexWave"); w.wave_type = "RINGS"; w.inputs["Scale"].default_value = ring / 10; w.inputs["Distortion"].default_value = 6
    nt.links.new(vec, w.inputs["Vector"])
    mx = nt.nodes.new("ShaderNodeMath"); mx.operation = "MULTIPLY"; nt.links.new(f, mx.inputs[0]); nt.links.new(w.outputs["Fac"], mx.inputs[1])
    nt.links.new(_ramp(nt, mx.outputs["Value"], [c * (1 - var) for c in rgb], [min(1, c * (1 + var)) for c in rgb]), b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = rough
    _bevel_bump(nt, b, mx.outputs["Value"], strength=0.06)

def concrete(m, rgb, rough=0.8):
    nt, b, _ = _clear(m)
    vec = _pos(nt, (1, 1, 1))
    f1 = _noise(nt, vec, 1.2, 8, 0.7); f2 = _noise(nt, vec, 18.0, 6, 0.6)
    mx = nt.nodes.new("ShaderNodeMath"); mx.operation = "MULTIPLY_ADD"; mx.inputs[1].default_value = 0.5
    nt.links.new(f1, mx.inputs[0]); nt.links.new(f2, mx.inputs[2])
    nt.links.new(_ramp(nt, mx.outputs["Value"], [c * 0.82 for c in rgb], [min(1, c * 1.12) for c in rgb]), b.inputs["Base Color"])
    rr = nt.nodes.new("ShaderNodeMapRange"); rr.inputs["To Min"].default_value = rough - 0.25; rr.inputs["To Max"].default_value = rough
    nt.links.new(f2, rr.inputs["Value"]); nt.links.new(rr.outputs["Result"], b.inputs["Roughness"])
    _bevel_bump(nt, b, f2, strength=0.05)

def metal(m, rgb, rough=0.35):
    nt, b, _ = _clear(m)
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Metallic"].default_value = 1.0
    f = _noise(nt, _pos(nt, (1, 1, 40)), 20.0)
    rr = nt.nodes.new("ShaderNodeMapRange"); rr.inputs["To Min"].default_value = rough - 0.1; rr.inputs["To Max"].default_value = rough + 0.1
    nt.links.new(f, rr.inputs["Value"]); nt.links.new(rr.outputs["Result"], b.inputs["Roughness"])
    _bevel_bump(nt, b, None, radius=0.003)

def satin(m, rgb, rough=0.4, coat=0.0):
    nt, b, _ = _clear(m)
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = rough
    if coat: b.inputs["Coat Weight"].default_value = coat
    _bevel_bump(nt, b, None)

def glass(m):
    """Window glass that lets sunlight through (shadow rays transparent; no caustics needed)."""
    nt = m.node_tree
    for n in list(nt.nodes): nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial"); g = nt.nodes.new("ShaderNodeBsdfGlass"); g.inputs["IOR"].default_value = 1.45
    g.inputs["Color"].default_value = (0.95, 0.98, 0.97, 1); g.inputs["Roughness"].default_value = 0.0
    tr = nt.nodes.new("ShaderNodeBsdfTransparent"); lp = nt.nodes.new("ShaderNodeLightPath"); mx = nt.nodes.new("ShaderNodeMixShader")
    sh = nt.nodes.new("ShaderNodeMath"); sh.operation = "MAXIMUM"
    nt.links.new(lp.outputs["Is Shadow Ray"], sh.inputs[0]); nt.links.new(lp.outputs["Is Diffuse Ray"], sh.inputs[1])
    nt.links.new(sh.outputs["Value"], mx.inputs["Fac"]); nt.links.new(g.outputs["BSDF"], mx.inputs[1]); nt.links.new(tr.outputs["BSDF"], mx.inputs[2])
    nt.links.new(mx.outputs["Shader"], out.inputs["Surface"])

def _xyz(nt):
    geo = nt.nodes.new("ShaderNodeNewGeometry"); sp = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(geo.outputs["Position"], sp.inputs["Vector"]); return sp

def _m(nt, op, a, b=None, c=None):
    n = nt.nodes.new("ShaderNodeMath"); n.operation = op
    for i, v in enumerate((a, b, c)):
        if v is None: continue
        if isinstance(v, (int, float)): n.inputs[i].default_value = v
        else: nt.links.new(v, n.inputs[i])
    return n.outputs["Value"]

def siding(m, rgb, var=0.18, board=0.305, batten=0.07, ground=-0.5):
    """Vertical board-and-batten, stained (PHOTO-OBSERVED exterior cladding). Walls are axis-aligned, so the
    horizontal coordinate along any face is x + y; battens are raised strips every `board` metres."""
    nt, b, _ = _clear(m); sp = _xyz(nt)
    u = _m(nt, "ADD", sp.outputs["X"], sp.outputs["Y"])
    q = _m(nt, "DIVIDE", u, board)
    idx = _m(nt, "FLOOR", q); fr = _m(nt, "FRACT", q)
    wn = nt.nodes.new("ShaderNodeTexWhiteNoise"); wn.noise_dimensions = "1D"; nt.links.new(idx, wn.inputs["W"])
    bat = _m(nt, "LESS_THAN", fr, batten / board)
    # vertical streaks + per-board tone + darker splash zone near grade
    mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (14, 14, 0.7)
    geo = nt.nodes.new("ShaderNodeNewGeometry"); nt.links.new(geo.outputs["Position"], mp.inputs["Vector"])
    st = _noise(nt, mp.outputs["Vector"], 3.0, 8, 0.65)
    tone = _m(nt, "MULTIPLY_ADD", wn.outputs["Value"], 0.5, st)
    col = _ramp(nt, _m(nt, "MULTIPLY", tone, 0.67), [c * (1 - var) for c in rgb], [min(1, c * (1 + var)) for c in rgb])
    splash = nt.nodes.new("ShaderNodeMapRange"); splash.inputs["From Min"].default_value = ground; splash.inputs["From Max"].default_value = ground + 0.7
    splash.inputs["To Min"].default_value = 0.55; splash.inputs["To Max"].default_value = 1.0; nt.links.new(sp.outputs["Z"], splash.inputs["Value"])
    mix = nt.nodes.new("ShaderNodeMixRGB"); mix.blend_type = "MULTIPLY"; mix.inputs["Fac"].default_value = 1.0
    nt.links.new(col, mix.inputs["Color1"])
    cmb = nt.nodes.new("ShaderNodeCombineXYZ")
    for k_ in "XYZ": nt.links.new(splash.outputs["Result"], cmb.inputs[k_])
    nt.links.new(cmb.outputs["Vector"], mix.inputs["Color2"]); nt.links.new(mix.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.88
    h = _m(nt, "ADD", bat, _m(nt, "MULTIPLY", st, 0.15))
    bump = nt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 1.0; bump.inputs["Distance"].default_value = 0.02
    nt.links.new(h, bump.inputs["Height"]); nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])

def roof_metal(m, rgb=(0.42, 0.45, 0.48), pitch=0.229, panel=0.914):
    """Galvanised ribbed steel (PHOTO-OBSERVED). Ribs run down the slope, i.e. repeat along the ridge (Y)."""
    nt, b, _ = _clear(m); sp = _xyz(nt)
    fr = _m(nt, "FRACT", _m(nt, "DIVIDE", sp.outputs["Y"], pitch))
    rib = nt.nodes.new("ShaderNodeMapRange"); rib.interpolation_type = "SMOOTHSTEP"
    rib.inputs["From Min"].default_value = 0.0; rib.inputs["From Max"].default_value = 0.12; nt.links.new(fr, rib.inputs["Value"])
    ribh = _m(nt, "SUBTRACT", 1.0, rib.outputs["Result"])
    pidx = _m(nt, "FLOOR", _m(nt, "DIVIDE", sp.outputs["Y"], panel))
    wn = nt.nodes.new("ShaderNodeTexWhiteNoise"); wn.noise_dimensions = "1D"; nt.links.new(pidx, wn.inputs["W"])
    f = _noise(nt, _pos(nt, (0.6, 0.6, 0.6)), 2.0, 8, 0.6)
    tone = _m(nt, "MULTIPLY_ADD", wn.outputs["Value"], 0.35, _m(nt, "MULTIPLY", f, 0.65))
    nt.links.new(_ramp(nt, tone, [c * 0.88 for c in rgb], [min(1, c * 1.08) for c in rgb]), b.inputs["Base Color"])
    b.inputs["Metallic"].default_value = 0.9
    rr = nt.nodes.new("ShaderNodeMapRange"); rr.inputs["To Min"].default_value = 0.28; rr.inputs["To Max"].default_value = 0.5
    nt.links.new(f, rr.inputs["Value"]); nt.links.new(rr.outputs["Result"], b.inputs["Roughness"])
    bump = nt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 1.0; bump.inputs["Distance"].default_value = 0.03
    nt.links.new(ribh, bump.inputs["Height"]); nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])

def grass(m):
    """Autumn lawn as in the site photos (indicative context, not surveyed)."""
    nt, b, _ = _clear(m)
    big = _noise(nt, _pos(nt, (1, 1, 1)), 0.12, 6, 0.6); mid = _noise(nt, _pos(nt, (1, 1, 1)), 1.5, 6, 0.6)
    c1 = _ramp(nt, big, (0.035, 0.085, 0.010), (0.11, 0.16, 0.022))
    vo = nt.nodes.new("ShaderNodeTexVoronoi"); vo.inputs["Scale"].default_value = 9.0
    nt.links.new(_pos(nt, (1, 1, 1)), vo.inputs["Vector"])
    leaf = _m(nt, "LESS_THAN", vo.outputs["Distance"], 0.13)
    leafc = nt.nodes.new("ShaderNodeMixRGB"); leafc.inputs["Fac"].default_value = 1.0
    nt.links.new(c1, leafc.inputs["Color1"]); leafc.inputs["Color2"].default_value = (0.32, 0.11, 0.03, 1)
    fac = _m(nt, "MULTIPLY", leaf, _m(nt, "GREATER_THAN", mid, 0.55)); nt.links.new(fac, leafc.inputs["Fac"])
    nt.links.new(leafc.outputs["Color"], b.inputs["Base Color"]); b.inputs["Roughness"].default_value = 0.95
    bump = nt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.6
    nt.links.new(_noise(nt, _pos(nt, (1, 1, 1)), 140.0, 4, 0.7), bump.inputs["Height"]); nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])

def _exterior_dressing(g):
    """PHOTO-OBSERVED trim (white window/door casings, light eave fascia) as thin presentation boxes on the
    existing siding faces, plus indicative context trees. Collection LOOKDEV_EXTERIOR; never saved to the model."""
    scene = bpy.context.scene
    from mathutils import Vector
    co = bpy.data.collections.new("LOOKDEV_EXTERIOR"); scene.collection.children.link(co)
    def mat(name, rgb, rough):
        mm = bpy.data.materials.new(name); mm.use_nodes = True; satin(mm, rgb, rough); return mm
    white = mat("lookdev_trim_white", (0.80, 0.80, 0.78), 0.5)
    def bx(nm, x0, x1, y0, y1, z0, z1, mm):
        me = bpy.data.meshes.new(nm)
        v = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
        me.from_pydata(v, [], [(0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)])
        me.materials.append(mm); o = bpy.data.objects.new(nm, me); co.objects.link(o)
        o["evidence_class"] = "LOOKDEV presentation trim (PHOTO-OBSERVED colour/type)"; return o
    EL, ER, G0, G1 = g["EXT_L"], g["EXT_R"], g["EXT_G0"], g["EXT_G1"]; EXT_G0 = G0
    w, t = 0.09, 0.025
    for o in [o for o in bpy.data.objects if o.name.startswith(("WINDOW_", "DOOR_"))]:
        bb = [o.matrix_world @ Vector(c) for c in o.bound_box]
        x0, x1 = min(v.x for v in bb), max(v.x for v in bb); y0, y1 = min(v.y for v in bb), max(v.y for v in bb); z0, z1 = min(v.z for v in bb), max(v.z for v in bb)
        if x1 - x0 < 0.2:   # on a long wall
            xf = EL - t if x0 < 6 else ER; xa, xb = (xf, xf + t) if x0 >= 6 else (EL - t, EL)
            if x0 >= 6: xa, xb = ER, ER + t
            for (ya, yb, za, zb) in ((y0 - w, y0, z0 - w, z1 + w), (y1, y1 + w, z0 - w, z1 + w), (y0, y1, z1, z1 + w), (y0, y1, z0 - w, z0)):
                bx(f"LOOKDEV_trim_{o.name}", xa, xb, ya, yb, za, zb, white)
        else:              # on a gable
            ya, yb = (G0 - t, G0) if y0 < 15 else (G1, G1 + t)
            for (xa, xb, za, zb) in ((x0 - w, x0, z0 - (0 if o.name.startswith("DOOR") else w), z1 + w), (x1, x1 + w, z0 - (0 if o.name.startswith("DOOR") else w), z1 + w), (x0, x1, z1, z1 + w)) + (((x0, x1, z0 - w, z0),) if o.name.startswith("WINDOW") else ()):
                bx(f"LOOKDEV_trim_{o.name}", xa, xb, ya, yb, za, zb, white)
    # eave fascia (light metal, PHOTO-OBSERVED) along both long eaves
    roof = bpy.data.objects["EX_roof_metal"]; rb = [roof.matrix_world @ Vector(c) for c in roof.bound_box]
    rx0, rx1 = min(v.x for v in rb), max(v.x for v in rb); ry0, ry1 = min(v.y for v in rb), max(v.y for v in rb)
    import math as _m_
    t13 = _m_.tan(_m_.radians(g["ROOF_PITCH"])); AX, RZ = g["AX"], g["ROOF_RIDGE"]
    for xe in (rx0, rx1):
        ze = RZ - t13 * abs(xe - AX)
        bx("LOOKDEV_fascia", xe - 0.03 if xe > AX else xe, xe if xe > AX else xe + 0.03, ry0, ry1, ze - 0.16, ze + 0.09, white)
    # indicative context trees (not surveyed; species/positions from the site photos only in spirit)
    rng = __import__("random").Random(7)
    bark = mat("lookdev_bark", (0.07, 0.05, 0.04), 0.9)
    def leaves(name, rgb):
        mm = bpy.data.materials.new(name); mm.use_nodes = True; nt, b_, _ = _clear(mm)
        f = _noise(nt, _pos(nt, (1, 1, 1)), 4.0, 6, 0.6)
        nt.links.new(_ramp(nt, f, [c * 0.6 for c in rgb], [min(1, c * 1.3) for c in rgb]), b_.inputs["Base Color"])
        b_.inputs["Roughness"].default_value = 0.8; b_.inputs["Subsurface Weight"].default_value = 0.15
        bump = nt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 1.0
        vo = nt.nodes.new("ShaderNodeTexVoronoi"); vo.inputs["Scale"].default_value = 9.0; nt.links.new(_pos(nt, (1, 1, 1)), vo.inputs["Vector"])
        nt.links.new(vo.outputs["Distance"], bump.inputs["Height"]); nt.links.new(bump.outputs["Normal"], b_.inputs["Normal"])
        return mm
    pine = leaves("lookdev_pine", (0.012, 0.03, 0.015))
    autumn = [leaves("lookdev_leaf_a", (0.16, 0.06, 0.015)), leaves("lookdev_leaf_b", (0.18, 0.11, 0.02)), leaves("lookdev_leaf_c", (0.05, 0.07, 0.015))]
    tex = bpy.data.textures.new("lookdev_clouds", "CLOUDS"); tex.noise_scale = 0.35; tex.noise_depth = 4
    tex2 = bpy.data.textures.new("lookdev_clouds_fine", "CLOUDS"); tex2.noise_scale = 0.07; tex2.noise_depth = 2
    def link_new(o): co.objects.link(o); o["evidence_class"] = "LOOKDEV context (indicative, not surveyed)"; return o
    def cone(nm, loc, r, h, mm):
        bpy.ops.mesh.primitive_cone_add(vertices=24, radius1=r, radius2=0.0, depth=h, location=loc)
        o = bpy.context.active_object; o.name = nm; o.data.materials.append(mm)
        for c_ in o.users_collection: c_.objects.unlink(o)
        sub = o.modifiers.new("s", "SUBSURF"); sub.levels = 2; sub.render_levels = 2
        d = o.modifiers.new("d", "DISPLACE"); d.texture = tex; d.strength = r * 0.35
        d2 = o.modifiers.new("d2", "DISPLACE"); d2.texture = tex2; d2.strength = r * 0.12
        return link_new(o)
    def conifer(x, y, H):
        n = 7
        for i in range(n):
            f = i / n; cone("LOOKDEV_pine", (x + rng.uniform(-.2, .2), y + rng.uniform(-.2, .2), g["GROUND"] + H * (0.18 + 0.72 * f)), H * 0.22 * (1 - 0.8 * f) + 0.3, H * 0.28, pine)
    def broadleaf(x, y, H, mm):
        for i in range(9):
            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=4, radius=H * rng.uniform(0.11, 0.19),
                location=(x + rng.uniform(-1, 1) * H * 0.2, y + rng.uniform(-1, 1) * H * 0.2, g["GROUND"] + H * rng.uniform(0.55, 0.85)))
            o = bpy.context.active_object; o.name = "LOOKDEV_crown"; o.data.materials.append(mm)
            for c_ in o.users_collection: c_.objects.unlink(o)
            d = o.modifiers.new("d", "DISPLACE"); d.texture = tex; d.strength = H * 0.07
            d2 = o.modifiers.new("d2", "DISPLACE"); d2.texture = tex2; d2.strength = H * 0.025; link_new(o)
    # entry lamp above the gable door (fixture PHOTO-OBSERVED in the owner's entry photo; lit only at dusk)
    d_ = bpy.data.objects.get("DOOR_DARK_gable_entry_door")
    if d_:
        db = [d_.matrix_world @ Vector(c) for c in d_.bound_box]
        lx = (min(v.x for v in db) + max(v.x for v in db)) / 2; lz = max(v.z for v in db) + 0.45
        bx("LOOKDEV_entry_lamp_body", lx - 0.06, lx + 0.06, EXT_G0 - 0.12, EXT_G0, lz - 0.08, lz + 0.08, mat("lookdev_lamp", (0.05, 0.05, 0.05), 0.4))
        Ld = bpy.data.lights.new("lookdev_entry_lamp", "SPOT"); Ld.energy = 0; Ld.color = (1.0, 0.75, 0.5); Ld.spot_size = math.radians(120); Ld.shadow_soft_size = 0.05
        Lo = bpy.data.objects.new("lookdev_entry_lamp", Ld); Lo.location = (lx, EXT_G0 - 0.15, lz - 0.1); Lo.rotation_euler = (math.radians(20), 0, 0); co.objects.link(Lo)
    # distant treeline ring only (context; no tree is placed near the building or in front of any camera)
    for cl in range(26):   # clumps, as on the site photos (pine stands + mixed hardwoods)
        ang = rng.uniform(0, 2 * math.pi); r = rng.uniform(50, 110); cx_, cy_ = 6 + r * math.cos(ang), 15 + r * math.sin(ang)
        pine_clump = rng.random() < 0.45
        for i in range(rng.randint(3, 8)):
            x, y = cx_ + rng.gauss(0, 6), cy_ + rng.gauss(0, 6)
            if pine_clump or rng.random() < 0.2: conifer(x, y, rng.uniform(13, 22))
            else: broadleaf(x, y, rng.uniform(10, 17), autumn[rng.randrange(3)])
    # foreground grass strands (hair) in front of the street-level cameras only
    for nm, (x0, x1, y0, y1) in (("entry", (5.0, 27.0, -17.0, -0.6)), ("live", (3.0, 27.0, 31.3, 45.0))):
        bpy.ops.mesh.primitive_plane_add(size=1, location=((x0 + x1) / 2, (y0 + y1) / 2, g["GROUND"] + 0.002))
        gp = bpy.context.active_object; gp.name = f"LOOKDEV_grass_{nm}"; gp.scale = (x1 - x0, y1 - y0, 1)
        bpy.ops.object.transform_apply(scale=True)
        bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.subdivide(number_cuts=40); bpy.ops.object.mode_set(mode="OBJECT")
        vg = gp.vertex_groups.new(name="dens")
        for v in gp.data.vertices:
            d = min(v.co.x - x0, x1 - v.co.x, v.co.y - y0, y1 - v.co.y)
            vg.add([v.index], max(0.0, min(1.0, d / 5.0)) ** 1.5, "REPLACE")
        for c_ in gp.users_collection: c_.objects.unlink(gp)
        link_new(gp); gp.data.materials.append(g["M"]["ex_ground"])
        hm = bpy.data.materials.new("lookdev_grass_blade"); hm.use_nodes = True; hnt, hb, _ = _clear(hm)
        hi = hnt.nodes.new("ShaderNodeHairInfo")
        hr = hnt.nodes.new("ShaderNodeValToRGB"); hr.color_ramp.elements[0].color = (0.03, 0.075, 0.008, 1); hr.color_ramp.elements[1].color = (0.10, 0.15, 0.02, 1)
        e = hr.color_ramp.elements.new(0.94); e.color = (0.22, 0.17, 0.05, 1)
        hnt.links.new(hi.outputs["Random"], hr.inputs["Fac"]); hnt.links.new(hr.outputs["Color"], hb.inputs["Base Color"])
        hb.inputs["Roughness"].default_value = 0.7; hb.inputs["Subsurface Weight"].default_value = 0.1
        gp.data.materials.append(hm)
        mod = gp.modifiers.new("grass", "PARTICLE_SYSTEM"); ps = mod.particle_system.settings
        ps.type = "HAIR"; ps.count = int((x1 - x0) * (y1 - y0) * 110); ps.hair_length = 0.11; ps.material = 2
        ps.child_type = "INTERPOLATED"; ps.child_percent = 10; ps.rendered_child_count = 9; ps.child_length = 1.0; ps.child_length_threshold = 0.4
        ps.roughness_1 = 0.03; ps.roughness_endpoint = 0.05; ps.roughness_2 = 0.02
        ps.use_rotations = True; ps.phase_factor_random = 2.0; ps.factor_random = 0.0; ps.hair_length = 0.10
        ps.root_radius = 1.0; ps.tip_radius = 0.0; ps.radius_scale = 0.0035; ps.display_step = 3; ps.render_step = 3
        mod.particle_system.seed = 3; mod.particle_system.vertex_group_density = "dens"
    # large ground disk under the modelled grade so wide / aerial views reach the treeline
    bpy.ops.mesh.primitive_circle_add(vertices=96, radius=260, fill_type="NGON", location=(6, 15, g["GROUND"] - 0.003))
    gd = bpy.context.active_object; gd.name = "LOOKDEV_ground_far"; gd.data.materials.append(g["M"]["ex_ground"])
    for c_ in gd.users_collection: c_.objects.unlink(gd)
    link_new(gd)
    bpy.data.objects["EX_ground"].hide_render = True   # replaced in look renders by the seamless disk above (same material, same grade)
    return co

SPEC = {
 # existing (finish unknown -> neutral matte paint, no invented texture)
 "ex_wall": ("matte", dict(rgb=(0.72, 0.68, 0.62), rough=0.9, var=0.03, bump=0.02)),
 "ex_floor_cr": ("concrete", dict(rgb=(0.45, 0.45, 0.43))),
 "ex_concrete": ("concrete", dict(rgb=(0.52, 0.51, 0.49))),
 "ex_post": ("wood", dict(rgb=(0.46, 0.31, 0.19), axis="Z", rough=0.6)),
 "ex_joist": ("wood", dict(rgb=(0.58, 0.44, 0.29), axis="Y", rough=0.65)),
 # existing exterior (PHOTO-OBSERVED cladding; colours sampled from the site photos, approximate)
 "ex_siding": ("siding", dict(rgb=(0.115, 0.075, 0.048))),
 "ex_siding_live": ("siding", dict(rgb=(0.17, 0.14, 0.115))),
 "ex_roof": ("roof_metal", dict()),
 "ex_ground": ("grass", dict()),
 "ex_osb": ("matte", dict(rgb=(0.62, 0.50, 0.33), rough=0.8, var=0.15, scale=40)),
 "stove": ("satin", dict(rgb=(0.025, 0.025, 0.025), rough=0.55)),
 "door": ("satin", dict(rgb=(0.90, 0.89, 0.86), rough=0.45)),
 "door_dark": ("satin", dict(rgb=(0.05, 0.05, 0.055), rough=0.45)),
 # actual equipment
 "walnut": ("wood", dict(rgb=(0.20, 0.10, 0.05), axis="X", rough=0.35, var=0.3)),
 "panel_black": ("satin", dict(rgb=(0.03, 0.032, 0.035), rough=0.45)),
 "spk_cab": ("satin", dict(rgb=(0.035, 0.035, 0.037), rough=0.6)),
 "spk_small": ("satin", dict(rgb=(0.035, 0.035, 0.037), rough=0.6)),
 "steel_black": ("metal", dict(rgb=(0.05, 0.05, 0.05), rough=0.45)),
 "steel": ("metal", dict(rgb=(0.55, 0.55, 0.56), rough=0.35)),
 "meter_bridge": ("metal", dict(rgb=(0.62, 0.45, 0.20), rough=0.3)),
 "piano": ("satin", dict(rgb=(0.008, 0.008, 0.008), rough=0.08, coat=1.0)),
 # proposed finishes (design intent)
 "oak": ("planks", dict(light=(0.54, 0.40, 0.26), dark=(0.45, 0.33, 0.21))),
 "plaster": ("matte", dict(rgb=(0.86, 0.83, 0.78), rough=0.95, var=0.05, bump=0.08, scale=3)),
 "fabric": ("fabric", dict(rgb=(0.48, 0.45, 0.41))),
 "fabric_dark": ("fabric", dict(rgb=(0.14, 0.14, 0.15))),
 "reclaimed": ("wood", dict(rgb=(0.47, 0.32, 0.19), axis="X", rough=0.6, var=0.35)),
 "sofa": ("fabric", dict(rgb=(0.40, 0.37, 0.33), weave=250, sheen=0.5)),
 "rug": ("fabric", dict(rgb=(0.33, 0.30, 0.26), weave=120, sheen=0.6, var=0.08)),
 "gobo": ("wood", dict(rgb=(0.55, 0.40, 0.25), axis="Z")),
 "machinery": ("satin", dict(rgb=(0.55, 0.07, 0.04), rough=0.35, coat=0.4)),
 "v5_abs_blue": ("fabric", dict(rgb=(0.10, 0.16, 0.30))),
 "v5_charcoal": ("fabric", dict(rgb=(0.13, 0.13, 0.14))),
 "v5_burlap": ("fabric", dict(rgb=(0.50, 0.41, 0.28), weave=140, sheen=0.1, var=0.1)),
 "v5_gobo": ("fabric", dict(rgb=(0.22, 0.22, 0.23))),
 "v5_tan": ("fabric", dict(rgb=(0.62, 0.52, 0.38))),
 "v5_sblue": ("fabric", dict(rgb=(0.13, 0.22, 0.40))),
 "v5_foam": ("fabric", dict(rgb=(0.23, 0.23, 0.25))),
 "v5_new": ("fabric", dict(rgb=(0.74, 0.71, 0.65), sheen=0.2)),
 "v5_curtain": ("fabric", dict(rgb=(0.28, 0.27, 0.26), weave=90, sheen=0.6)),
 "v5_lounge": ("fabric", dict(rgb=(0.56, 0.44, 0.32), weave=200, sheen=0.5)),
 "v5_leather": ("satin", dict(rgb=(0.30, 0.16, 0.08), rough=0.45, coat=0.2)),
 "v5_fin": ("wood", dict(rgb=(0.56, 0.39, 0.22), axis="Z")),
 "v5_rustic": ("wood", dict(rgb=(0.36, 0.24, 0.15), axis="X", rough=0.75, var=0.4)),
 "v5_perf": ("wood", dict(rgb=(0.62, 0.47, 0.29), axis="Y")),
 "v5_peg": ("matte", dict(rgb=(0.68, 0.55, 0.38), rough=0.7, var=0.08, bump=0.1, scale=40)),
}
FN = dict(siding=siding, roof_metal=roof_metal, grass=grass, matte=matte, fabric=fabric, planks=planks, wood=wood, concrete=concrete, metal=metal, satin=satin)

def apply(g):
    M, scene = g["M"], bpy.context.scene
    for key, (kind, kw) in SPEC.items():
        if key in M: FN[kind](M[key], **kw)
    _exterior_dressing(g)
    if "glass" in M: glass(M["glass"])
    # world: physical sky; warm late-afternoon sun from the west through the existing side windows
    world = scene.world; nt = world.node_tree
    for n in list(nt.nodes): nt.nodes.remove(n)
    sky = nt.nodes.new("ShaderNodeTexSky"); sky.sky_type = "MULTIPLE_SCATTERING"
    try:
        sky.sun_elevation = math.radians(24); sky.sun_rotation = math.radians(270); sky.sun_disc = False
    except Exception: pass
    bg = nt.nodes.new("ShaderNodeBackground"); bg.inputs["Strength"].default_value = 0.35
    out = nt.nodes.new("ShaderNodeOutputWorld")
    # soft procedural clouds projected on a high plane (direction.xy / direction.z), faded at the horizon
    tc = nt.nodes.new("ShaderNodeTexCoord"); sp = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(tc.outputs["Generated"], sp.inputs["Vector"])
    zc = nt.nodes.new("ShaderNodeMath"); zc.operation = "MAXIMUM"; zc.inputs[1].default_value = 0.04; nt.links.new(sp.outputs["Z"], zc.inputs[0])
    cx = nt.nodes.new("ShaderNodeMath"); cx.operation = "DIVIDE"; nt.links.new(sp.outputs["X"], cx.inputs[0]); nt.links.new(zc.outputs["Value"], cx.inputs[1])
    cy = nt.nodes.new("ShaderNodeMath"); cy.operation = "DIVIDE"; nt.links.new(sp.outputs["Y"], cy.inputs[0]); nt.links.new(zc.outputs["Value"], cy.inputs[1])
    cv = nt.nodes.new("ShaderNodeCombineXYZ"); nt.links.new(cx.outputs["Value"], cv.inputs["X"]); nt.links.new(cy.outputs["Value"], cv.inputs["Y"])
    cmp = nt.nodes.new("ShaderNodeMapping"); cmp.inputs["Scale"].default_value = (1.0, 2.2, 1.0); nt.links.new(cv.outputs["Vector"], cmp.inputs["Vector"])
    cn = nt.nodes.new("ShaderNodeTexNoise"); cn.inputs["Scale"].default_value = 0.9; cn.inputs["Detail"].default_value = 10; cn.inputs["Roughness"].default_value = 0.62
    nt.links.new(cmp.outputs["Vector"], cn.inputs["Vector"])
    cr = nt.nodes.new("ShaderNodeMapRange"); cr.inputs["From Min"].default_value = 0.52; cr.inputs["From Max"].default_value = 0.78; nt.links.new(cn.outputs["Fac"], cr.inputs["Value"])
    hz = nt.nodes.new("ShaderNodeMapRange"); hz.inputs["From Min"].default_value = 0.02; hz.inputs["From Max"].default_value = 0.25; nt.links.new(sp.outputs["Z"], hz.inputs["Value"])
    cm = nt.nodes.new("ShaderNodeMath"); cm.operation = "MULTIPLY"; nt.links.new(cr.outputs["Result"], cm.inputs[0]); nt.links.new(hz.outputs["Result"], cm.inputs[1])
    mixc = nt.nodes.new("ShaderNodeMixRGB"); mixc.name = "cloud_mix"; nt.links.new(cm.outputs["Value"], mixc.inputs["Fac"])
    nt.links.new(sky.outputs["Color"], mixc.inputs["Color1"])
    ccol = nt.nodes.new("ShaderNodeMath"); ccol.operation = "MULTIPLY"   # cloud brightness tracks the sky (dark at dusk)
    sk = nt.nodes.new("ShaderNodeRGBToBW"); nt.links.new(sky.outputs["Color"], sk.inputs["Color"])
    nt.links.new(sk.outputs["Val"], ccol.inputs[0]); ccol.inputs[1].default_value = 1.6
    cc = nt.nodes.new("ShaderNodeCombineXYZ")
    for k_ in "XYZ": nt.links.new(ccol.outputs["Value"], cc.inputs[k_])
    nt.links.new(cc.outputs["Vector"], mixc.inputs["Color2"])
    nt.links.new(mixc.outputs["Color"], bg.inputs["Color"]); nt.links.new(bg.outputs["Background"], out.inputs["Surface"])
    sun = g["sun"]; sun.color = (1.0, 0.86, 0.70); sun.angle = math.radians(1.2)
    g["so"].rotation_euler = (math.radians(66), 0, math.radians(-72))   # ~24 deg elevation, light travelling +X (from the X=0 side) and slightly +Y
    # fire glow behind the existing stove's door (presentation lighting only)
    xs, ys = g["xs"], g["ys"]
    me = bpy.data.meshes.new("LOOKDEV_fire_glow")
    me.from_pydata([(xs - 0.17, ys - 0.252, 0.14), (xs + 0.17, ys - 0.252, 0.14), (xs + 0.17, ys - 0.252, 0.46), (xs - 0.17, ys - 0.252, 0.46)], [], [(0, 1, 2, 3)])
    fo = bpy.data.objects.new("LOOKDEV_fire_glow", me); scene.collection.objects.link(fo); fo["evidence_class"] = "LOOKDEV presentation lighting"
    fm = bpy.data.materials.new("lookdev_fire"); fm.use_nodes = True; fnt = fm.node_tree
    for n in list(fnt.nodes): fnt.nodes.remove(n)
    fout = fnt.nodes.new("ShaderNodeOutputMaterial"); em = fnt.nodes.new("ShaderNodeEmission")
    tc = fnt.nodes.new("ShaderNodeTexCoord"); nz = fnt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 9; nz.inputs["Distortion"].default_value = 3
    fnt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    sep = fnt.nodes.new("ShaderNodeSeparateXYZ"); fnt.links.new(tc.outputs["Object"], sep.inputs["Vector"])
    hgt = fnt.nodes.new("ShaderNodeMapRange"); hgt.inputs["From Min"].default_value = 0.14; hgt.inputs["From Max"].default_value = 0.46
    hgt.inputs["To Min"].default_value = 1.0; hgt.inputs["To Max"].default_value = 0.0; fnt.links.new(sep.outputs["Z"], hgt.inputs["Value"])
    mul = fnt.nodes.new("ShaderNodeMath"); mul.operation = "MULTIPLY"; fnt.links.new(nz.outputs["Fac"], mul.inputs[0]); fnt.links.new(hgt.outputs["Result"], mul.inputs[1])
    cr = fnt.nodes.new("ShaderNodeValToRGB"); cr.color_ramp.elements[0].position = 0.12; cr.color_ramp.elements[0].color = (0.02, 0.005, 0.0, 1)
    cr.color_ramp.elements[1].position = 0.75; cr.color_ramp.elements[1].color = (1.0, 0.55, 0.15, 1)
    fnt.links.new(mul.outputs["Value"], cr.inputs["Fac"]); fnt.links.new(cr.outputs["Color"], em.inputs["Color"]); em.inputs["Strength"].default_value = 9
    fnt.links.new(em.outputs["Emission"], fout.inputs["Surface"])
    me.materials.append(fm)
    pl = bpy.data.lights.new("lookdev_fire_light", "POINT"); pl.energy = 25; pl.color = (1.0, 0.45, 0.15); pl.shadow_soft_size = 0.15
    po = bpy.data.objects.new("lookdev_fire_light", pl); po.location = (xs, ys - 0.45, 0.32); scene.collection.objects.link(po)
    # render quality
    c = scene.cycles
    c.samples = int(__import__("os").environ.get("BG_SAMPLES", 128)); c.use_adaptive_sampling = True; c.adaptive_threshold = 0.015
    c.use_denoising = True; c.max_bounces = 8; c.diffuse_bounces = 4; c.glossy_bounces = 4; c.transmission_bounces = 8
    c.caustics_reflective = False; c.caustics_refractive = False; c.sample_clamp_indirect = 8.0
    scene.render.resolution_x = int(__import__("os").environ.get("BG_RES_X", 1920)); scene.render.resolution_y = int(__import__("os").environ.get("BG_RES_Y", 1080))
    scene.view_settings.view_transform = "AgX"; scene.view_settings.look = "AgX - Medium High Contrast"
    return "photo"

def _sun_dir(g, az_deg, el_deg, sky_strength):
    """Sun shining FROM azimuth az (deg, 0 = +X, 90 = +Y) at elevation el; sky gradient follows."""
    from mathutils import Vector
    a, e = math.radians(az_deg), math.radians(el_deg)
    to_sun = Vector((math.cos(a) * math.cos(e), math.sin(a) * math.cos(e), math.sin(e)))
    g["so"].rotation_euler = (-to_sun).to_track_quat("-Z", "Y").to_euler()
    nt = g["scene"].world.node_tree
    for n in nt.nodes:
        if n.type == "TEX_SKY":
            n.sun_elevation = e; n.sun_rotation = a - math.pi / 2
        if n.type == "BACKGROUND": n.inputs["Strength"].default_value = sky_strength

EXTERIOR_LOOK = {   # view: (sun azimuth, elevation, sun energy, sky strength, exposure, interior lights on)
 "ext_entry":      (-100, 24, 3.6, 0.32, -0.55, False),
 "ext_live_gable": (125, 22, 3.6, 0.32, -0.55, False),
 "ext_aerial":     (-100, 30, 3.6, 0.32, -0.55, False),
 "ext_entry_dusk": (-150, 1.5, 0.0, 0.10, 1.3, True),
}

def per_view(g, k, cinema):
    """Called just before each render: balance interior fill against daylight for this look."""
    M = g["M"]
    for o in bpy.data.objects:   # grass strands only where a street-level exterior camera sees them
        if o.name.startswith("LOOKDEV_grass_"): o.hide_render = k not in ("ext_entry", "ext_entry_dusk", "ext_live_gable")
    if k in EXTERIOR_LOOK:
        az, el, se, sky, ex, lit = EXTERIOR_LOOK[k]
        _sun_dir(g, az, el, sky); g["sun"].energy = se; g["sun"].color = (1.0, 0.80, 0.62) if el < 5 else (1.0, 0.90, 0.78)
        g["scene"].view_settings.exposure = ex
        for n in M["cove"].node_tree.nodes:
            if n.type == "BSDF_PRINCIPLED": n.inputs["Emission Strength"].default_value = 18 if lit else 0; n.inputs["Emission Color"].default_value = (1.0, 0.72, 0.45, 1)
        for L in bpy.data.lights:
            if L.type == "AREA":
                L["base_energy"] = L.get("base_energy", L.energy); L["base_color"] = L.get("base_color", tuple(L.color)); L.energy = L["base_energy"] * (1.0 if lit else 0.0); L.color = (1.0, 0.80, 0.58)
            if L.name == "lookdev_fire_light": L.energy = 60 if lit else 0
            if L.name == "lookdev_entry_lamp": L.energy = 40 if lit else 0
        return
    # interior views: restore the original look-pass sun / sky / light colours (in case an exterior view ran first)
    g["so"].rotation_euler = (math.radians(66), 0, math.radians(-72)); g["sun"].color = (1.0, 0.86, 0.70)
    for n in g["scene"].world.node_tree.nodes:
        if n.type == "TEX_SKY": n.sun_elevation = math.radians(24); n.sun_rotation = math.radians(270)
        if n.type == "BACKGROUND": n.inputs["Strength"].default_value = 0.35
    for L in bpy.data.lights:
        if "base_color" in L: L.color = tuple(L["base_color"])
        if L.name == "lookdev_fire_light": L.energy = 25
    for L in bpy.data.lights:
        if L.type == "AREA" and L.name.startswith("cr_fill"): L.energy = 6 if cinema else (35 if L.name.endswith("1") else 22)
        if L.type == "AREA" and L.name.startswith(("lv_fill", "mz_light", "loft_light")):
            L["base_energy"] = L.get("base_energy", L.energy); L.energy = L["base_energy"] * 0.35
    M["cove"].node_tree.nodes  # cove/pendant materials are rebuilt by build_studio per view; tone them here
    for key, val in (("cove", 1.5 if cinema else 3.5), ("pendant", 12)):
        for n in M[key].node_tree.nodes:
            if n.type == "BSDF_PRINCIPLED":
                n.inputs["Emission Strength"].default_value = val
                if key == "cove": n.inputs["Emission Color"].default_value = (1.0, 0.78, 0.55, 1)
    g["sun"].energy = 0.6 if cinema else 7.0
    g["scene"].view_settings.exposure = -0.3 if cinema else -0.1
