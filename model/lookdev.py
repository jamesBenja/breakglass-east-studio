"""Presentation look-development pass (BG_LOOK=photo). Materials, lighting and render settings ONLY.

No object is moved, added to the building, removed or reshaped: geometry, cameras and the saved .blend are
exactly the v0.5 model. The single added item is a fire-glow emitter inside the existing stove's door
(presentation lighting, tagged LOOKDEV). Materials express the documented design intent (oak floor, pale
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

SPEC = {
 # existing (finish unknown -> neutral matte paint, no invented texture)
 "ex_wall": ("matte", dict(rgb=(0.72, 0.68, 0.62), rough=0.9, var=0.03, bump=0.02)),
 "ex_floor_cr": ("concrete", dict(rgb=(0.45, 0.45, 0.43))),
 "ex_concrete": ("concrete", dict(rgb=(0.52, 0.51, 0.49))),
 "ex_post": ("wood", dict(rgb=(0.46, 0.31, 0.19), axis="Z", rough=0.6)),
 "ex_joist": ("wood", dict(rgb=(0.58, 0.44, 0.29), axis="Y", rough=0.65)),
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
FN = dict(matte=matte, fabric=fabric, planks=planks, wood=wood, concrete=concrete, metal=metal, satin=satin)

def apply(g):
    M, scene = g["M"], bpy.context.scene
    for key, (kind, kw) in SPEC.items():
        if key in M: FN[kind](M[key], **kw)
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
    nt.links.new(sky.outputs["Color"], bg.inputs["Color"]); nt.links.new(bg.outputs["Background"], out.inputs["Surface"])
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

def per_view(g, k, cinema):
    """Called just before each render: balance interior fill against daylight for this look."""
    M = g["M"]
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
