"""v0.5 live-room backline (owner request 14 Nov): the default 'ensemble' set-up shows a band, not a string quartet.

INDICATIVE, generic gear (the owner's actual backline is not inventoried yet): a 5-piece drum kit inside the three
GOB-001 drum gobos, a guitar combo and a bass rig behind the two half-height GOB-002 screens, boom mic stands on
kit / amps / piano, and one stool + mic for acoustic guitar or vocal. Collection 39_V05_BACKLINE; every object is
prefixed V5_BL_ and tagged INDICATIVE. Farm mode (BG_LIVE_MODE=farm) puts it all away.
Positions follow acoustics/allocation.py (DRUM centre and the GOB-002 screens), so moving those moves the backline.
"""
import math
import bmesh, bpy
from mathutils import Vector

COLL = "39_V05_BACKLINE"
EV = "INDICATIVE generic backline (owner's actual gear TBD)"

def _mat(name, rgb, rough=0.4, metal=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = rough; b.inputs["Metallic"].default_value = metal
    return m

def build(g):
    col, F = g["col"], g["F_LIVE"]
    AX = g["AX"]
    coll = col(COLL)
    M = {"shell": _mat("bl_drum_shell", (0.32, 0.05, 0.04), 0.25),        # lacquered shells
         "head": _mat("bl_drum_head", (0.86, 0.84, 0.78), 0.6),
         "chrome": _mat("bl_chrome", (0.80, 0.80, 0.82), 0.15, 1.0),
         "bronze": _mat("bl_cymbal", (0.78, 0.56, 0.24), 0.25, 1.0),
         "tolex": _mat("bl_tolex", (0.03, 0.03, 0.03), 0.7),
         "grille": _mat("bl_grille", (0.55, 0.50, 0.42), 0.9),
         "black": _mat("bl_black_steel", (0.02, 0.02, 0.02), 0.45, 0.6),
         "mic": _mat("bl_mic", (0.15, 0.15, 0.16), 0.3, 0.8),
         "seat": _mat("bl_seat", (0.05, 0.05, 0.05), 0.6)}
    n = [0]
    def link(o, note):
        coll.objects.link(o); o["evidence_class"] = EV; o["note"] = note; return o
    def cyl(p0, p1, r, mat, note="", seg=24):
        p0, p1 = Vector(p0), Vector(p1); d = p1 - p0
        me = bpy.data.meshes.new("bl"); bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r, depth=d.length)
        bm.to_mesh(me); bm.free(); me.materials.append(M[mat])
        n[0] += 1; o = bpy.data.objects.new(f"V5_BL_{note or 'part'}_{n[0]}", me)
        o.location = (p0 + p1) / 2; o.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
        return link(o, note)
    def box(c, size, mat, note="", yaw=0.0):
        me = bpy.data.meshes.new("bl"); bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0); bm.to_mesh(me); bm.free()
        me.materials.append(M[mat]); n[0] += 1
        o = bpy.data.objects.new(f"V5_BL_{note or 'box'}_{n[0]}", me); o.location = c; o.scale = size; o.rotation_euler = (0, 0, math.radians(yaw))
        return link(o, note)
    def rot(cx, cy, yaw, lx, ly):   # local (lx, ly) -> world, local +Y = facing
        t = math.radians(yaw); return (cx + lx * math.cos(t) - ly * math.sin(t), cy + lx * math.sin(t) + ly * math.cos(t))
    def stand(x, y, top, note):      # tripod + pole, returns top point
        for k in range(3):
            a = math.radians(90 + k * 120); cyl((x, y, F + 0.30), (x + 0.28 * math.cos(a), y + 0.28 * math.sin(a), F + 0.01), 0.008, "black", note)
        cyl((x, y, F + 0.30), (x, y, F + top), 0.011, "black", note); return Vector((x, y, F + top))
    def boom_mic(x, y, h, target, note):
        top = stand(x, y, h, note); t = Vector(target)
        d = (t - top); d.z = 0; d = d.normalized() if d.length > 1e-6 else Vector((0, 1, 0))
        end = top + d * 0.55 + Vector((0, 0, 0.0)); end.z = top.z + 0.5 * (t.z - top.z)
        cyl(top, end, 0.008, "black", note)
        aim = (t - end).normalized(); cyl(end, end + aim * 0.16, 0.022, "mic", note)

    # ---------------------------------------------------------------- drum kit (faces -Y, drummer on the gobo side)
    import json, os
    PJ = json.load(open(os.path.join(g["ROOT"], "acoustics", "out", "placements.json")))
    DRUM = PJ["ensemble"]["drum_centre"]
    GOB002 = [(p["centre"][0], p["centre"][1], p["rot_deg"][2] if isinstance(p["rot_deg"], list) else p["rot_deg"]) for p in PJ["placements"] if p["asset"] == "GOB-002"]
    dx, dy = DRUM; yaw = 180.0                       # kit's front (kick head) points to -Y, toward the piano / room
    P = lambda lx, ly: rot(dx, dy, yaw, lx, ly)      # local +Y = toward the audience/room
    kx, ky = P(0, 0.20)
    cyl((kx, ky - 0.0, F + 0.29), (*P(0, 0.62), F + 0.29), 0.28, "shell", "kick drum")
    cyl((*P(0, 0.635), F + 0.29), (*P(0, 0.645), F + 0.29), 0.285, "head", "kick drum")
    sx, sy = P(-0.30, -0.12); cyl((sx, sy, F + 0.58), (sx, sy, F + 0.72), 0.18, "shell", "snare"); cyl((sx, sy, F + 0.72), (sx, sy, F + 0.725), 0.18, "head", "snare")
    cyl((sx, sy, F + 0.02), (sx, sy, F + 0.58), 0.01, "chrome", "snare stand")
    for lx, ly, r, z in ((-0.12, 0.42, 0.13, 0.80), (0.16, 0.42, 0.15, 0.78)):   # rack toms on the kick
        x_, y_ = P(lx, ly); cyl((x_, y_, F + z), (x_, y_, F + z + 0.20), r, "shell", "rack tom"); cyl((x_, y_, F + z + 0.20), (x_, y_, F + z + 0.205), r, "head", "rack tom")
    fx, fy = P(0.48, -0.05); cyl((fx, fy, F + 0.12), (fx, fy, F + 0.55), 0.20, "shell", "floor tom"); cyl((fx, fy, F + 0.55), (fx, fy, F + 0.555), 0.20, "head", "floor tom")
    for lx, ly in ((0.18, 0.18), (-0.18, 0.18), (0, -0.18)):
        a, b_ = P(0.48 + lx * 0.6, -0.05 + ly * 0.6); cyl((a, b_, F), (a, b_, F + 0.14), 0.01, "chrome", "floor tom")
    hx, hy = P(-0.62, 0.05); stand(hx, hy, 0.86, "hi-hat")
    cyl((hx, hy, F + 0.86), (hx, hy, F + 0.87), 0.18, "bronze", "hi-hat"); cyl((hx, hy, F + 0.885), (hx, hy, F + 0.895), 0.18, "bronze", "hi-hat")
    for lx, ly, h, r, nm in ((-0.45, 0.55, 1.35, 0.23, "crash"), (0.62, 0.40, 1.15, 0.26, "ride")):
        x_, y_ = P(lx, ly); stand(x_, y_, h, nm); cyl((x_, y_, F + h), (x_, y_, F + h + 0.01), r, "bronze", nm)
    tx, ty = P(0, -0.55); cyl((tx, ty, F), (tx, ty, F + 0.45), 0.03, "chrome", "throne"); cyl((tx, ty, F + 0.45), (tx, ty, F + 0.55), 0.19, "seat", "throne")
    # drum mics: kick, snare, two overheads
    boom_mic(*P(0.25, 1.05), 0.45, (kx, ky + 0.0, F + 0.29) if False else (*P(0, 0.66), F + 0.30), "mic stand kick")
    boom_mic(*P(-0.55, 0.40), 0.75, (sx, sy, F + 0.74), "mic stand snare")
    for lx in (-0.55, 0.55):
        boom_mic(*P(lx * 1.5, 0.95), 1.75, (*P(lx * 0.6, 0.15), F + 1.35), "mic stand overhead")

    # ---------------------------------------------------------------- amps behind the GOB-002 half-height screens
    for k, (gx, gy, gyaw) in enumerate(GOB002):
        nx_, ny_ = -math.sin(math.radians(gyaw)), math.cos(math.radians(gyaw))      # screen normal
        sgn = 1 if (gy + 0.6 * ny_) > gy else -1
        ax_, ay_ = gx + sgn * 0.55 * nx_, gy + sgn * 0.55 * ny_                       # amp sits 0.55 m behind the screen (gable side)
        face = math.degrees(math.atan2(-(gx - ax_), gy - ay_))                         # amp faces the screen
        if k == 0:   # guitar combo on a tilt-back stand
            box((ax_, ay_, F + 0.20 + 0.29), (0.65, 0.27, 0.55), "tolex", "guitar amp combo", face)
            fx_, fy_ = ax_ + 0.14 * math.sin(-math.radians(face)) * -1, ay_ + 0.14 * math.cos(math.radians(face))
            box((ax_ - 0.14 * math.sin(math.radians(face)), ay_ + 0.14 * math.cos(math.radians(face)), F + 0.20 + 0.27), (0.56, 0.01, 0.40), "grille", "guitar amp combo", face)
            box((ax_, ay_, F + 0.10), (0.5, 0.25, 0.2), "black", "amp stand", face)
            mx, my = max(((ax_ - 0.25 * math.sin(math.radians(face)) + sg * 0.50 * math.cos(math.radians(face)), ay_ + 0.25 * math.cos(math.radians(face)) + sg * 0.50 * math.sin(math.radians(face))) for sg in (-1, 1)),
                         key=lambda q: math.hypot(q[0] - gx, q[1] - gy))   # beside the amp, on the side away from the screen
            boom_mic(mx, my, 0.55, (ax_ - 0.14 * math.sin(math.radians(face)), ay_ + 0.14 * math.cos(math.radians(face)), F + 0.47), "mic stand guitar amp")
        else:        # bass rig: 4x10 cab + head
            box((ax_, ay_, F + 0.32), (0.60, 0.45, 0.62), "tolex", "bass cab 4x10", face)
            box((ax_ - 0.226 * math.sin(math.radians(face)), ay_ + 0.226 * math.cos(math.radians(face)), F + 0.32), (0.54, 0.01, 0.56), "grille", "bass cab 4x10", face)
            box((ax_, ay_, F + 0.63 + 0.13), (0.55, 0.30, 0.25), "tolex", "bass head", face)
            mx, my = max(((ax_ - 0.30 * math.sin(math.radians(face)) + sg * 0.55 * math.cos(math.radians(face)), ay_ + 0.30 * math.cos(math.radians(face)) + sg * 0.55 * math.sin(math.radians(face))) for sg in (-1, 1)),
                         key=lambda q: math.hypot(q[0] - gx, q[1] - gy))   # beside the amp, on the side away from the screen
            boom_mic(mx, my, 0.55, (ax_ - 0.23 * math.sin(math.radians(face)), ay_ + 0.23 * math.cos(math.radians(face)), F + 0.40), "mic stand bass cab")

    # ---------------------------------------------------------------- piano mics (pair over the strings) + acoustic / vocal position
    pe = bpy.data.objects["PR_grand_piano"]; pm = pe.matrix_world
    for lx in (-0.35, 0.30):
        tgt = pm @ Vector((lx * 0.8, 0.95, 1.05)); base = pm @ Vector((lx + 1.15 * (1 if lx > 0 else -1), 0.75, 0))
        boom_mic(base.x, base.y, 1.55, (tgt.x, tgt.y, F + 1.10), "mic stand piano")
    ox, oy = AX + 1.95, g["Y_LOFT_END"] + 4.5           # where the quartet was: a stool + mic for acoustic guitar / vocal
    cyl((ox, oy, F), (ox, oy, F + 0.66), 0.025, "black", "stool"); cyl((ox, oy, F + 0.66), (ox, oy, F + 0.70), 0.17, "seat", "stool")
    for k in range(3):
        a = math.radians(30 + k * 120); cyl((ox, oy, F + 0.25), (ox + 0.22 * math.cos(a), oy + 0.22 * math.sin(a), F), 0.012, "black", "stool")
    boom_mic(ox - 0.15, oy - 0.95, 1.30, (ox, oy - 0.25, F + 1.25), "mic stand vocal")
    boom_mic(ox + 0.35, oy - 0.80, 0.70, (ox + 0.05, oy - 0.30, F + 0.85), "mic stand acoustic guitar")
    return len(coll.objects)

def put_away():
    """Farm mode: backline packed away (into the support rooms / under-loft storage; not drawn)."""
    for o in bpy.data.objects:
        if o.name.startswith("V5_BL_"): o.hide_render = True
