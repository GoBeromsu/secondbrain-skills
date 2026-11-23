"""Procedural Blender scenes for secondbrain-skills art. No external assets.

The splash: threads of light rise from several open books into a constellation of linked stars.

Run:  blender -b -P scripts/art/library.py -- <scene> <out.png> [samples] [resolution %]
Scenes: splash (README banner, 2400x1200), icon (1024 square); hero, icon_book, drop, archive,
catalogue and reading are earlier studies kept for reuse.
Env: FOG=<density> sets the volumetric haze (the published renders use 0.014);
HIDE=<prefix,...> hides objects by name prefix for debugging.
Blender 5.x, Cycles. Every mesh, material and light is built here from primitives.
"""
import math
import random
import sys

import bmesh
import bpy
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else ["hero", "/tmp/hero.png"]
SCENE, OUT = argv[0], argv[1]
SAMPLES = int(argv[2]) if len(argv) > 2 else 192
PERCENT = int(argv[3]) if len(argv) > 3 else 100

BOOK_COLORS = [
    (0.42, 0.04, 0.04), (0.05, 0.10, 0.32), (0.05, 0.24, 0.12), (0.62, 0.38, 0.10),
    (0.62, 0.55, 0.42), (0.20, 0.10, 0.06), (0.30, 0.14, 0.36), (0.12, 0.12, 0.13),
    (0.45, 0.12, 0.10), (0.10, 0.22, 0.28),
]


# ---------------------------------------------------------------- utilities
def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.samples = SAMPLES
    sc.cycles.use_denoising = True
    try:
        prefs = bpy.context.preferences.addons["cycles"].preferences
        prefs.compute_device_type = "METAL"
        prefs.get_devices()
        for d in prefs.devices:
            d.use = True
        sc.cycles.device = "GPU"
    except Exception:
        pass
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Medium High Contrast"
    sc.render.film_transparent = False
    sc.cycles.max_bounces = 8
    sc.cycles.volume_bounces = 1
    w = bpy.data.worlds.new("world")
    sc.world = w
    w.use_nodes = True
    bg = w.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (0.010, 0.012, 0.022, 1)
    bg.inputs[1].default_value = 1.0
    return sc


def mat(name, color=(0.8, 0.8, 0.8), rough=0.5, metal=0.0, emit=None, strength=0.0, attr=None, bump=None):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    p = nt.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*color, 1)
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    if emit:
        p.inputs["Emission Color"].default_value = (*emit, 1)
        p.inputs["Emission Strength"].default_value = strength
    if attr:
        a = nt.nodes.new("ShaderNodeAttribute")
        a.attribute_name = attr
        nt.links.new(a.outputs["Color"], p.inputs["Base Color"])
    if bump:
        tex = nt.nodes.new("ShaderNodeTexNoise")
        tex.inputs["Scale"].default_value = bump[0]
        tex.inputs["Detail"].default_value = 8
        b = nt.nodes.new("ShaderNodeBump")
        b.inputs["Strength"].default_value = bump[1]
        nt.links.new(tex.outputs["Fac"], b.inputs["Height"])
        nt.links.new(b.outputs["Normal"], p.inputs["Normal"])
    return m


def wood_mat(name="walnut", base=(0.16, 0.065, 0.028), scale=2.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    p = nt.nodes["Principled BSDF"]
    p.inputs["Roughness"].default_value = 0.42
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (scale * 0.3, scale * 0.3, scale * 6)
    wave = nt.nodes.new("ShaderNodeTexWave")
    wave.wave_type = "RINGS"
    wave.inputs["Scale"].default_value = 3.0
    wave.inputs["Distortion"].default_value = 6.0
    wave.inputs["Detail"].default_value = 4
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (*[c * 0.6 for c in base], 1)
    ramp.color_ramp.elements[1].color = (*[min(1, c * 1.6) for c in base], 1)
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    nt.links.new(mp.outputs["Vector"], wave.inputs["Vector"])
    nt.links.new(wave.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], p.inputs["Base Color"])
    b = nt.nodes.new("ShaderNodeBump")
    b.inputs["Strength"].default_value = 0.08
    nt.links.new(wave.outputs["Fac"], b.inputs["Height"])
    nt.links.new(b.outputs["Normal"], p.inputs["Normal"])
    return m


def box(name, size, loc, material=None, bevel=0.0, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.scale = size
    bpy.ops.object.transform_apply(scale=True)
    if bevel:
        mod = o.modifiers.new("bevel", "BEVEL")
        mod.width = bevel
        mod.segments = 2
    if material:
        o.data.materials.append(material)
    return o


def link_obj(name, mesh):
    o = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(o)
    return o


# ---------------------------------------------------------------- books
def books_mesh(name, rows, rnd, gilt=True):
    """rows: list of (origin Vector, direction Vector along shelf, length, max_h, depth, facing +1/-1 on x).
    Builds one mesh of bevel-ready book boxes with a per-book colour attribute, plus a gilt label mesh."""
    bm = bmesh.new()
    gm = bmesh.new()
    col_layer = bm.loops.layers.color.new("book")
    tops = []

    def add_box(target, cx, cy, cz, sx, sy, sz, tilt=0.0, color=None, layer=None):
        hx, hy, hz = sx / 2, sy / 2, sz / 2
        corners = [(-hx, -hy, -hz), (hx, -hy, -hz), (hx, hy, -hz), (-hx, hy, -hz),
                   (-hx, -hy, hz), (hx, -hy, hz), (hx, hy, hz), (-hx, hy, hz)]
        ct, st = math.cos(tilt), math.sin(tilt)
        vs = []
        for x, y, z in corners:
            # tilt around the x axis (lean along the shelf) pivoting at the bottom
            y2, z2 = y * ct - (z + hz) * st, y * st + (z + hz) * ct - hz
            vs.append(target.verts.new((cx + x, cy + y2, cz + z2)))
        faces = [(0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
        for f in faces:
            face = target.faces.new([vs[i] for i in f])
            if layer is not None:
                for loop in face.loops:
                    loop[layer] = (*color, 1)

    for origin, length, max_h, depth, facing in rows:
        y = 0.0
        while y < length - 0.03:
            t = rnd.choice([0.022, 0.028, 0.032, 0.038, 0.045, 0.055, 0.065])
            h = rnd.uniform(max_h * 0.66, max_h * 0.96)
            d = rnd.uniform(depth * 0.72, depth)
            base = rnd.choice(BOOK_COLORS)
            v = rnd.uniform(0.7, 1.25)
            color = tuple(min(1.0, c * v) for c in base)
            if rnd.random() < 0.06:  # a gap
                y += rnd.uniform(0.03, 0.12)
                continue
            tilt = 0.0
            if rnd.random() < 0.035 and y > 0.1:
                tilt = rnd.uniform(0.12, 0.30)
            cx = origin.x + facing * (-(depth - d) / 2)
            cy = origin.y + y + t / 2
            cz = origin.z + h / 2
            add_box(bm, cx, cy, cz, d, t, h, tilt, color, col_layer)
            if gilt and rnd.random() < 0.55 and tilt == 0.0:
                for band in ([0.82] if rnd.random() < 0.6 else [0.80, 0.18]):
                    add_box(gm, cx + facing * (d / 2 + 0.0008), cy, origin.z + h * band, 0.0016, t * 0.8, 0.008)
            tops.append(Vector((cx + facing * d / 2, cy, origin.z + h)))
            y += t + (0.03 * math.sin(tilt) if tilt else 0.0005)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    gme = bpy.data.meshes.new(name + "_gilt")
    gm.to_mesh(gme)
    gm.free()
    cloth = mat("cloth", rough=0.62, attr="book", bump=(380, 0.18))
    o = link_obj(name, me)
    o.data.materials.append(cloth)
    mod = o.modifiers.new("bevel", "BEVEL")
    mod.width = 0.0025
    mod.segments = 2
    g = link_obj(name + "_gilt", gme)
    g.data.materials.append(mat("gilt", (0.83, 0.62, 0.30), rough=0.28, metal=1.0))
    for p in me.polygons:
        p.use_smooth = False
    return o, tops


def bookcase(x, y0, length, height, facing, shelf_gap, rnd, name, wood):
    """A run of bookcase along y at wall x; facing=+1 means books face +x (left wall)."""
    depth = 0.30
    cx = x - facing * depth / 2
    box(f"{name}_back", (0.03, length, height), (x - facing * (depth - 0.015), y0 + length / 2, height / 2), wood)
    rows = []
    n_shelves = int(height / shelf_gap)
    bays = max(1, round(length / 1.1))
    bay = length / bays
    for b in range(bays + 1):
        box(f"{name}_div{b}", (depth, 0.04, height), (cx, y0 + b * bay, height / 2), wood, bevel=0.004)
    for s in range(n_shelves + 1):
        z = 0.08 + s * shelf_gap
        box(f"{name}_shelf{s}", (depth + 0.02, length, 0.03), (cx + facing * 0.01, y0 + length / 2, z), wood, bevel=0.003)
        if s < n_shelves:
            for b in range(bays):
                rows.append((Vector((cx, y0 + b * bay + 0.025, z + 0.015)), bay - 0.05, shelf_gap - 0.05, depth - 0.04, facing))
    # crown
    box(f"{name}_crown", (depth + 0.08, length, 0.10), (cx, y0 + length / 2, height + 0.05), wood, bevel=0.01)
    return books_mesh(name + "_books", rows, rnd)


# ---------------------------------------------------------------- brain
def brain_points(center, scale, n, rnd):
    pts = []
    tries = 0
    while len(pts) < n and tries < 40000:
        tries += 1
        x, y, z = rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1)
        side = 1 if x >= 0 else -1
        # two hemispheres: ellipsoids offset in x, flattened at the bottom
        hx = x - side * 0.48
        r = (hx / 0.58) ** 2 + (y / 0.98) ** 2 + (z / 0.78) ** 2
        if r > 1 or r < 0.55 or abs(x) < 0.05 or z < -0.55 + 0.25 * (y > 0.4):
            continue
        p = Vector((center.x + x * scale.x, center.y + y * scale.y, center.z + z * scale.z))
        if all((p - q).length > scale.x * 0.11 for q in pts):
            pts.append(p)
    return pts


def curve_obj(name, paths, radius, material):
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = radius
    cu.bevel_resolution = 2
    for pts in paths:
        sp = cu.splines.new("BEZIER")
        sp.bezier_points.add(len(pts) - 1)
        for bp, p in zip(sp.bezier_points, pts):
            bp.co = p
            bp.handle_left_type = bp.handle_right_type = "AUTO"
    o = link_obj(name, cu)
    o.data.materials.append(material)
    return o


def brain(center, scale, rnd, threads_to=(), n=70, node_r=0.018):
    pts = brain_points(center, scale, n, rnd)
    node_m = mat("node", (1, 0.85, 0.6), emit=(1.0, 0.72, 0.38), strength=28)
    edge_m = mat("synapse", (0.6, 0.5, 1), emit=(0.55, 0.42, 1.0), strength=5)
    thread_m = mat("thread", (1, 0.8, 0.5), emit=(1.0, 0.66, 0.30), strength=3.5)
    bm = bmesh.new()
    for p in pts:
        r = node_r * rnd.uniform(0.7, 1.5)
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=r, matrix=__import__("mathutils").Matrix.Translation(p))
    me = bpy.data.meshes.new("nodes")
    bm.to_mesh(me)
    bm.free()
    o = link_obj("nodes", me)
    o.data.materials.append(node_m)
    edges = set()
    for i, p in enumerate(pts):
        near = sorted(range(len(pts)), key=lambda j: (pts[j] - p).length)[1:4]
        for j in near:
            if (pts[j] - p).length < scale.x * 0.45:
                edges.add(tuple(sorted((i, j))))
    paths = []
    for i, j in edges:
        a, b = pts[i], pts[j]
        mid = (a + b) / 2 + Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1))) * 0.03
        paths.append([a, mid, b])
    curve_obj("synapses", paths, node_r * 0.16, edge_m)
    if threads_to:
        low = sorted(pts, key=lambda p: p.z)[: max(6, len(threads_to))]
        tpaths = []
        for k, t in enumerate(threads_to):
            a = low[k % len(low)]
            m1 = a + (t - a) * 0.5 + Vector((0, 0, -0.18))
            tpaths.append([a, m1, t])
        curve_obj("threads", tpaths, node_r * 0.08, thread_m)
    return pts


def volume_box(size, loc, density=0.02, color=(0.9, 0.85, 0.8)):
    o = box("fog", size, loc)
    m = bpy.data.materials.new("fog")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    v = nt.nodes.new("ShaderNodeVolumePrincipled")
    v.inputs["Density"].default_value = density
    v.inputs["Color"].default_value = (*color, 1)
    v.inputs["Anisotropy"].default_value = 0.35
    nt.links.new(v.outputs[0], nt.nodes["Material Output"].inputs["Volume"])
    o.data.materials.append(m)
    o.visible_shadow = False
    return o


def camera(loc, target, lens=35, dof=None, fstop=2.8):
    cam = bpy.data.cameras.new("cam")
    cam.lens = lens
    o = link_obj("cam", cam)
    o.location = loc
    d = Vector(target) - Vector(loc)
    o.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    if dof:
        cam.dof.use_dof = True
        cam.dof.focus_distance = dof
        cam.dof.aperture_fstop = fstop
    bpy.context.scene.camera = o
    return o


def light(kind, loc, energy, color=(1, 0.8, 0.6), size=0.2, rot=None, spot=None):
    ld = bpy.data.lights.new(kind, kind)
    ld.energy = energy
    ld.color = color
    if kind in ("AREA",):
        ld.size = size
    if kind in ("POINT", "SPOT"):
        ld.shadow_soft_size = size
    if spot:
        ld.spot_size = spot
        ld.spot_blend = 0.6
    o = link_obj(kind, ld)
    o.location = loc
    if rot:
        o.rotation_euler = rot
    return o


def pendant(loc):
    shade = mat("brass", (0.75, 0.52, 0.25), rough=0.3, metal=1)
    glow = mat("bulb", (1, 0.8, 0.6), emit=(1.0, 0.68, 0.36), strength=40)
    bpy.ops.mesh.primitive_cone_add(radius1=0.22, radius2=0.05, depth=0.18, location=loc, end_fill_type="NOTHING")
    c = bpy.context.object
    c.data.materials.append(shade)
    c.modifiers.new("solid", "SOLIDIFY").thickness = 0.004
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.05, location=(loc[0], loc[1], loc[2] - 0.07))
    bpy.context.object.data.materials.append(glow)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.004, depth=3, location=(loc[0], loc[1], loc[2] + 1.55))
    bpy.context.object.data.materials.append(shade)
    light("POINT", (loc[0], loc[1], loc[2] - 0.12), 160, (1.0, 0.62, 0.32), size=0.05)


# ---------------------------------------------------------------- scenes
def library_aisle(rnd, length=13.0, height=4.6, half=1.35):
    wood = wood_mat()
    floor = box("floor", (6, length + 6, 0.05), (0, length / 2, -0.025), wood_mat("floor", (0.07, 0.035, 0.02), 4))
    floor.data.materials[0].node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.22
    box("ceiling", (6, length + 6, 0.1), (0, length / 2, height + 0.9), mat("ceil", (0.05, 0.04, 0.035), 0.8))
    _, left_tops = bookcase(-half, 0, length, height, +1, 0.40, rnd, "L", wood)
    _, right_tops = bookcase(half, 0, length, height, -1, 0.40, rnd, "R", wood)
    # end wall with a tall arched window of cool moonlight
    box("endwall", (6, 0.2, height + 1), (0, length + 0.4, (height + 1) / 2), mat("plaster", (0.18, 0.16, 0.14), 0.9))
    win = mat("window", (0.6, 0.7, 1.0), emit=(0.45, 0.58, 1.0), strength=2.2)
    box("window", (1.1, 0.05, 2.6), (0, length + 0.28, 2.2), win)
    light("AREA", (0, length + 0.1, 2.2), 320, (0.45, 0.58, 1.0), size=1.2, rot=(math.radians(-90), 0, 0))
    frame = mat("frame", (0.05, 0.03, 0.02), 0.5)
    for zz in (1.0, 1.9, 2.8):
        box("mullion_h", (1.14, 0.06, 0.04), (0, length + 0.24, zz), frame)
    box("mullion_v", (0.04, 0.06, 2.64), (0, length + 0.24, 2.2), frame)
    for xx in (-0.57, 0.57):
        box("jamb", (0.06, 0.08, 2.64), (xx, length + 0.24, 2.2), frame)
    box("head", (1.2, 0.08, 0.08), (0, length + 0.24, 3.52), frame)
    return left_tops, right_tops


def hero(aspect=(2560, 800), brain_scale=(0.80, 0.72, 0.56)):
    sc = reset()
    sc.render.resolution_x, sc.render.resolution_y = aspect
    rnd = random.Random(42)
    L, R = library_aisle(rnd)
    for y in (2.2, 5.4, 8.6, 11.6):
        pendant((0, y, 3.65))
    volume_box((2.6, 15, 5.6), (0, 6.5, 2.8), density=0.014, color=(1.0, 0.88, 0.75))
    targets = [t for t in L + R if 2.0 < t.y < 9.0 and t.z > 1.0]
    rnd.shuffle(targets)
    brain(Vector((0, 6.4, 2.45)), Vector(brain_scale), rnd, threads_to=targets[:12], n=150, node_r=0.014)
    camera((0, -1.4, 1.5), (0, 8, 2.2), lens=22, dof=7.8, fstop=4.0)
    return sc


def icon():
    sc = reset()
    sc.render.resolution_x = sc.render.resolution_y = 1024
    rnd = random.Random(7)
    sc.world.node_tree.nodes["Background"].inputs[0].default_value = (0.012, 0.010, 0.020, 1)
    desk = box("desk", (3, 3, 0.06), (0, 0, -0.03), wood_mat("desk", (0.10, 0.05, 0.03), 3), bevel=0.01)
    # open hardcover: two boards and page blocks with a gentle V
    cloth = mat("cover", (0.30, 0.05, 0.06), rough=0.6, bump=(400, 0.2))
    paper = mat("paper", (0.86, 0.80, 0.68), rough=0.7, bump=(900, 0.05))
    for side in (-1, 1):
        ang = side * math.radians(9)
        box(f"board{side}", (0.30, 0.42, 0.006), (side * 0.152, 0, 0.012), cloth, bevel=0.002, rot=(0, ang, 0))
        box(f"pages{side}", (0.285, 0.40, 0.024), (side * 0.146, 0, 0.032), paper, bevel=0.004, rot=(0, ang, 0))
    brain(Vector((0, 0.0, 0.40)), Vector((0.21, 0.19, 0.15)), rnd, n=46, node_r=0.010)
    # threads rising from the pages
    thread_m = mat("thread2", (1, 0.8, 0.5), emit=(1.0, 0.66, 0.30), strength=6)
    paths = []
    for k in range(8):
        x = rnd.uniform(-0.22, 0.22)
        yv = rnd.uniform(-0.14, 0.14)
        paths.append([Vector((x, yv, 0.06)), Vector((x * 0.7, yv, 0.16)), Vector((x * 0.4, yv * 0.6, 0.28))])
    curve_obj("risers", paths, 0.0012, thread_m)
    light("AREA", (0.8, -0.9, 1.4), 60, (1.0, 0.78, 0.55), size=0.6, rot=(math.radians(50), 0, math.radians(40)))
    light("AREA", (-1.0, 0.6, 0.8), 18, (0.5, 0.55, 1.0), size=1.0, rot=(math.radians(60), 0, math.radians(-120)))
    camera((0, -1.05, 0.78), (0, 0, 0.24), lens=50, dof=1.2, fstop=2.8)
    return sc


def studio(res=(900, 720), key=(1.0, 0.76, 0.5)):
    sc = reset()
    sc.render.resolution_x, sc.render.resolution_y = res
    box("table", (4, 4, 0.06), (0, 0, -0.03), wood_mat("table", (0.10, 0.05, 0.03), 3), bevel=0.01)
    box("wall", (4, 0.06, 3), (0, 1.2, 1.5), mat("wall", (0.07, 0.065, 0.08), 0.95))
    light("AREA", (0.9, -1.0, 1.5), 120, key, size=0.8, rot=(math.radians(50), 0, math.radians(40)))
    light("AREA", (-1.2, 0.2, 1.0), 25, (0.5, 0.55, 1.0), size=1.2, rot=(math.radians(60), 0, math.radians(-110)))
    return sc


def paper_sheet(name, loc, rot, size=(0.21, 0.297), m=None, bend=0.0):
    bpy.ops.mesh.primitive_plane_add(size=1, location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.scale = (size[0], size[1], 1)
    bpy.ops.object.transform_apply(scale=True)
    if bend:
        sub = o.modifiers.new("sub", "SUBSURF")
        sub.levels = 3
        sub.subdivision_type = "SIMPLE"
        dm = o.modifiers.new("bend", "SIMPLE_DEFORM")
        dm.deform_method = "BEND"
        dm.angle = bend
        dm.deform_axis = "X"
    o.modifiers.new("solid", "SOLIDIFY").thickness = 0.0006
    o.data.materials.append(m)
    return o


def scene_drop():
    sc = studio()
    rnd = random.Random(3)
    paper = mat("paper", (0.88, 0.84, 0.74), rough=0.75, bump=(900, 0.04))
    tray_m = wood_mat("tray", (0.16, 0.08, 0.04), 5)
    # wooden in-tray
    box("tray_base", (0.42, 0.32, 0.012), (0, 0, 0.006), tray_m, bevel=0.003)
    for sx, sy, lx, ly in ((0.42, 0.012, 0, -0.154), (0.42, 0.012, 0, 0.154), (0.012, 0.32, -0.204, 0), (0.012, 0.32, 0.204, 0)):
        box("tray_wall", (sx, sy, 0.07), (lx, ly, 0.035), tray_m, bevel=0.003)
    for k in range(6):
        paper_sheet(f"stack{k}", (rnd.uniform(-0.01, 0.01), rnd.uniform(-0.01, 0.01), 0.014 + k * 0.0016), (0, 0, rnd.uniform(-0.06, 0.06) + math.pi / 2), (0.21, 0.297), paper)
    # sheets drifting in from above
    for k, (x, z, rx) in enumerate(((-0.10, 0.30, 0.35), (0.08, 0.46, -0.5), (-0.02, 0.62, 0.8))):
        paper_sheet(f"fall{k}", (x, -0.02, z), (rx, rnd.uniform(-0.3, 0.3), rnd.uniform(0, 3)), (0.21, 0.297), paper, bend=0.5)
    # envelope and a tab card
    env = mat("envelope", (0.72, 0.58, 0.40), rough=0.7)
    box("envelope", (0.22, 0.11, 0.004), (0.05, 0.02, 0.03), env, bevel=0.001, rot=(0, 0, 0.25))
    camera((0.0, -0.95, 0.62), (0, 0, 0.18), lens=50, dof=0.98, fstop=4)
    return sc


def scene_archive():
    sc = studio()
    rnd = random.Random(5)
    card = mat("cardboard", (0.42, 0.30, 0.18), rough=0.85, bump=(300, 0.15))
    paper = mat("paper", (0.88, 0.84, 0.74), rough=0.75)
    # archival box, open, lid leaning behind
    w, d, h, t = 0.40, 0.28, 0.22, 0.006
    box("bottom", (w, d, t), (0, 0, t / 2), card)
    box("front", (w, t, h), (0, -d / 2, h / 2), card)
    box("back", (w, t, h), (0, d / 2, h / 2), card)
    box("left", (t, d, h), (-w / 2, 0, h / 2), card)
    box("right", (t, d, h), (w / 2, 0, h / 2), card)
    box("lid", (w + 0.02, 0.03, d + 0.02), (0.05, d / 2 + 0.09, (d + 0.02) / 2 + 0.004), card, rot=(math.radians(-12), 0, 0.12))
    label = mat("label", (0.92, 0.89, 0.80), rough=0.6)
    box("label", (0.14, 0.002, 0.06), (0, -d / 2 - 0.004, h * 0.6), label)
    # files standing in the box, each a folder with a tab
    folder_cols = [(0.62, 0.50, 0.30), (0.55, 0.44, 0.26), (0.30, 0.36, 0.45), (0.58, 0.48, 0.30)]
    x = -w / 2 + 0.03
    while x < w / 2 - 0.03:
        th = rnd.uniform(0.008, 0.018)
        hh = rnd.uniform(0.20, 0.24)
        m = mat("folder", rnd.choice(folder_cols), rough=0.8)
        box("folder", (th, d - 0.03, hh), (x, 0, hh / 2 + t), m, bevel=0.001, rot=(0, rnd.uniform(-0.05, 0.05), 0))
        if rnd.random() < 0.5:
            box("tab", (th * 0.6, 0.05, 0.02), (x, rnd.uniform(-0.08, 0.08), hh + t + 0.01), label)
        x += th + 0.004
    camera((0.35, -0.85, 0.62), (0, 0.02, 0.12), lens=50, dof=0.98, fstop=4)
    return sc


def scene_catalogue():
    sc = studio()
    rnd = random.Random(9)
    wood = wood_mat()
    box("shelf", (0.9, 0.24, 0.025), (0, 0, 0.0125), wood, bevel=0.003)
    rows = [(Vector((0, -0.38, 0.025)), 0.76, 0.30, 0.20, 1)]
    # rotate books so their spines face the camera (-y): build along y then rotate the objects
    o, tops = books_mesh("cat_books", rows, rnd)
    g = bpy.data.objects["cat_books_gilt"]
    for ob in (o, g):
        ob.rotation_euler = (0, 0, math.radians(-90))
        ob.location = (0, -0.1, 0)
    bpy.context.view_layer.update()
    # brass bookend
    brass = mat("brass", (0.75, 0.52, 0.25), rough=0.3, metal=1)
    box("bookend", (0.012, 0.16, 0.16), (0.42, 0.0, 0.105), brass, bevel=0.002)
    # catalogue card links: glowing threads hopping between spine tops
    wt = [o.matrix_world @ t for t in tops]
    wt = sorted(wt, key=lambda p: p.x)
    rnd.shuffle(wt)
    thread_m = mat("thread", (1, 0.8, 0.5), emit=(1.0, 0.66, 0.30), strength=8)
    paths = []
    for a, b in zip(wt[:7], wt[7:14]):
        mid = (a + b) / 2 + Vector((0, 0, 0.12 + 0.08 * rnd.random()))
        paths.append([a, mid, b])
    curve_obj("links", paths, 0.0012, thread_m)
    node_m = mat("node", (1, 0.85, 0.6), emit=(1.0, 0.72, 0.38), strength=25)
    for p in wt[:14]:
        bpy.ops.mesh.primitive_ico_sphere_add(radius=0.006, location=p)
        bpy.context.object.data.materials.append(node_m)
    camera((0.05, -1.25, 0.42), (0, -0.1, 0.17), lens=50, dof=1.15, fstop=4)
    return sc


def scene_reading():
    sc = studio(key=(1.0, 0.7, 0.45))
    rnd = random.Random(11)
    cloth = mat("cover", (0.07, 0.12, 0.26), rough=0.6, bump=(400, 0.2))
    paper = mat("paper", (0.90, 0.85, 0.74), rough=0.7, bump=(900, 0.04))
    for side in (-1, 1):
        ang = side * math.radians(8)
        box(f"board{side}", (0.24, 0.34, 0.005), (side * 0.122, 0, 0.008), cloth, bevel=0.002, rot=(0, ang, 0))
        box(f"pages{side}", (0.228, 0.32, 0.02), (side * 0.117, 0, 0.025), paper, bevel=0.004, rot=(0, ang, 0))
    # printed lines and a footnote marker on the pages
    ink = mat("ink", (0.05, 0.04, 0.04), rough=0.7)
    for side in (-1, 1):
        ang = side * math.radians(8)
        for k in range(14):
            wline = rnd.uniform(0.12, 0.18) if k % 5 != 4 else 0.08
            zl = 0.036 + abs(side * 0.117 + side * 0) * math.sin(abs(ang)) * 0
            box("line", (wline, 0.004, 0.0006), (side * 0.117, 0.13 - k * 0.018, 0.0355 + side * 0 + 0.000), ink, rot=(0, ang, 0))
    gold = mat("cite", (1, 0.8, 0.5), emit=(1.0, 0.7, 0.35), strength=12)
    box("citation", (0.05, 0.005, 0.0008), (0.10, -0.12, 0.036), gold, rot=(0, math.radians(8), 0))
    # brass desk lamp: base, arm, shade, bulb
    brass = mat("brass", (0.75, 0.52, 0.25), rough=0.3, metal=1)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.07, depth=0.02, location=(0.32, 0.18, 0.01))
    bpy.context.object.data.materials.append(brass)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.006, depth=0.46, location=(0.30, 0.14, 0.23), rotation=(math.radians(10), math.radians(-8), 0))
    bpy.context.object.data.materials.append(brass)
    shade_m = mat("shade", (0.10, 0.25, 0.14), rough=0.25, metal=0.0)
    bpy.ops.mesh.primitive_cone_add(radius1=0.10, radius2=0.03, depth=0.10, location=(0.22, 0.06, 0.44), rotation=(math.radians(-25), math.radians(30), 0), end_fill_type="NOTHING")
    s = bpy.context.object
    s.data.materials.append(shade_m)
    s.modifiers.new("solid", "SOLIDIFY").thickness = 0.003
    glow = mat("bulb", (1, 0.8, 0.6), emit=(1.0, 0.68, 0.36), strength=60)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.022, location=(0.20, 0.04, 0.41))
    bpy.context.object.data.materials.append(glow)
    light("SPOT", (0.20, 0.04, 0.40), 25, (1.0, 0.70, 0.42), size=0.02, rot=(math.radians(25), math.radians(-25), 0), spot=math.radians(80))
    camera((-0.15, -0.80, 0.62), (0.02, 0.02, 0.08), lens=45, dof=0.98, fstop=3.5)
    return sc



# ---------------------------------------------------------------- splash: open books feeding a constellation of linked stars
def splash(res=(2400, 1200), close=False):
    sc = reset()
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.cycles.max_bounces = 6
    rnd = random.Random(21)
    sc.world.node_tree.nodes["Background"].inputs[0].default_value = (0.006, 0.006, 0.012, 1)
    wood = wood_mat()
    # floor and back library wall of books, far enough to fall into bokeh
    box("floor", (20, 20, 0.05), (0, 0, -0.025), wood_mat("floor", (0.07, 0.035, 0.02), 4))
    # back shelves: a bookcase facing -y built by rotating a +x facing run
    _, tops = bookcase(0.0, -3.5, 7.0, 3.6, +1, 0.40, rnd, "B", wood)
    pivot = bpy.data.objects.new("pivot", None)
    bpy.context.collection.objects.link(pivot)
    for ob in [o for o in bpy.data.objects if o.name.startswith("B_")]:
        ob.parent = pivot
    pivot.rotation_euler = (0, 0, math.radians(-90))
    pivot.location = (0, 3.2, 0)
    # reading desk
    desk_m = wood_mat("desk", (0.13, 0.055, 0.025), 3)
    box("desk", (2.4, 1.1, 0.06), (0.35, 0.0, 0.76), desk_m, bevel=0.012)
    for lx in (-0.75, 1.45):
        for ly in (-0.45, 0.45):
            box("leg", (0.07, 0.07, 0.73), (lx, ly, 0.365), desk_m, bevel=0.006)
    top = 0.79
    # an old open book
    cover = mat("cover", (0.22, 0.04, 0.035), rough=0.55, bump=(420, 0.25))
    paper = mat("paper", (0.82, 0.74, 0.58), rough=0.75, bump=(900, 0.06))
    bx, by = 0.62, -0.05
    for side in (-1, 1):
        ang = side * math.radians(7)
        box(f"board{side}", (0.24, 0.34, 0.006), (bx + side * 0.122, by, top + 0.004), cover, bevel=0.002, rot=(0, ang, 0))
        box(f"pages{side}", (0.23, 0.325, 0.03), (bx + side * 0.118, by, top + 0.022), paper, bevel=0.006, rot=(0, ang, 0))
    gilt = mat("gilt", (0.83, 0.62, 0.30), rough=0.28, metal=1.0)
    # a closed stack beside it, a brass lamp off, a candle-warm key light
    stack_cols = ((0.06, 0.16, 0.12), (0.42, 0.20, 0.08), (0.10, 0.10, 0.30))
    z0 = top
    for k, (h, c) in enumerate(zip((0.05, 0.04, 0.06), stack_cols)):
        w, d = 0.30 - k * 0.02, 0.22 - k * 0.01
        rz = 0.12 - k * 0.09
        cm = mat(f"st{k}", c, 0.55, bump=(380, 0.25))
        box(f"stack{k}_cover", (w, d, h), (-0.25 + k * 0.01, 0.05, z0 + h / 2), cm, bevel=0.003, rot=(0, 0, rz))
        box(f"stack{k}_pages", (w - 0.012, d + 0.002, h - 0.01), (-0.25 + k * 0.01 + 0.007, 0.05, z0 + h / 2), paper, bevel=0.002, rot=(0, 0, rz))
        box(f"stack{k}_band", (0.012, d + 0.004, h * 0.25), (-0.25 + k * 0.01 - w / 2 + 0.03, 0.05, z0 + h * 0.7), gilt, rot=(0, 0, rz))
        z0 += h
    # ribbon bookmark lying across the right page and over the edge
    rib = mat("ribbon", (0.45, 0.04, 0.05), 0.45)
    paper_sheet("ribbon", (bx + 0.06, by - 0.10, top + 0.0385), (0, math.radians(-7), 0.15), (0.012, 0.22), rib)
    # pages lifting off the open book
    lift = mat("page_glow", (0.85, 0.78, 0.62), rough=0.7, emit=(1.0, 0.7, 0.4), strength=0.25)
    for k, ry in enumerate((-0.16, -0.34, -0.55)):
        hw = 0.112
        loc = (bx + hw * math.cos(ry), by, top + 0.04 - hw * math.sin(ry))
        paper_sheet(f"lift{k}", loc, (0, ry, 0), (0.224, 0.31), lift)
    # more open books around the first one, each a source the constellation draws from
    def open_book(x, y, rz, s, cover_color, name):
        cm = mat(f"cover_{name}", cover_color, rough=0.55, bump=(420, 0.25))
        R = lambda dx, dy: (x + dx * math.cos(rz) - dy * math.sin(rz), y + dx * math.sin(rz) + dy * math.cos(rz))
        for side in (-1, 1):
            ang = side * math.radians(8)
            px, py = R(side * 0.122 * s, 0)
            box(f"{name}_board{side}", (0.24 * s, 0.34 * s, 0.006), (px, py, top + 0.004), cm, bevel=0.002, rot=(0, ang, rz))
            px, py = R(side * 0.118 * s, 0)
            box(f"{name}_pages{side}", (0.23 * s, 0.325 * s, 0.026 * s), (px, py, top + 0.006 + 0.013 * s), paper, bevel=0.005, rot=(0, ang, rz))
        return Vector((x, y, top + 0.02 + 0.026 * s)), s
    sources = [(Vector((bx, by, top + 0.04)), 1.0)]
    sources.append(open_book(bx + 0.42, by + 0.34, math.radians(-28), 0.74, (0.08, 0.16, 0.30), "bookB"))
    sources.append(open_book(bx - 0.48, by + 0.26, math.radians(22), 0.72, (0.10, 0.22, 0.12), "bookC"))
    sources.append(open_book(bx + 0.18, by + 0.55, math.radians(6), 0.62, (0.36, 0.22, 0.08), "bookD"))
    # the constellation: stars linked by their nearest neighbours, loosely a two-lobed cloud
    c = Vector((bx + 0.0, by + 0.30, top + 0.46))
    size = Vector((0.52, 0.30, 0.30))
    pts = brain_points(c, size, 90, rnd)
    pts = [Vector((p.x, c.y + (p.y - c.y) * 0.7, p.z)) for p in pts]
    edges = set()
    for i, p in enumerate(pts):
        for j in sorted(range(len(pts)), key=lambda j: (pts[j] - p).length)[1:4]:
            if (pts[j] - p).length < 0.16:
                edges.add(tuple(sorted((i, j))))
    degree = [0] * len(pts)
    for i, j in edges:
        degree[i] += 1
        degree[j] += 1
    link_m = mat("link", (0.8, 0.7, 1), emit=(0.58, 0.46, 1.0), strength=2.6)
    curve_obj("links", [[pts[i], pts[j]] for i, j in edges], 0.0005, link_m)
    import mathutils
    star_m = mat("star", (1, 0.92, 0.8), emit=(1.0, 0.84, 0.60), strength=22)
    halo_m = mat("halo", (1, 0.8, 0.5), emit=(1.0, 0.66, 0.32), strength=4)
    bm = bmesh.new()
    bh = bmesh.new()
    for i, p in enumerate(pts):
        r = 0.0022 + 0.0011 * degree[i] + rnd.uniform(0, 0.0015)
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=r, matrix=mathutils.Matrix.Translation(p))
        if degree[i] >= 6 or rnd.random() < 0.06:
            bmesh.ops.create_icosphere(bh, subdivisions=3, radius=r * 5.0, matrix=mathutils.Matrix.Translation(p))
    for k in range(160):  # faint unlinked stars give the cloud depth
        v = Vector((rnd.gauss(0, 1), rnd.gauss(0, 1), rnd.gauss(0, 1)))
        q = c + Vector((v.x * size.x * 0.55, v.y * size.y * 0.45, v.z * size.z * 0.5))
        bmesh.ops.create_icosphere(bm, subdivisions=1, radius=rnd.uniform(0.0007, 0.0016), matrix=mathutils.Matrix.Translation(q))
    for nm, bmx, m in (("stars", bm, star_m), ("halos", bh, halo_m)):
        me = bpy.data.meshes.new(nm)
        bmx.to_mesh(me)
        bmx.free()
        o = link_obj(nm, me)
        o.data.materials.append(m)
        for poly in me.polygons:
            poly.use_smooth = True
    # soft halos: emission that fades by facing so they read as glow, not spheres
    nt = halo_m.node_tree
    pr = nt.nodes["Principled BSDF"]
    lw = nt.nodes.new("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = 0.5
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (1.0, 0.62, 0.3, 1)
    inv = nt.nodes.new("ShaderNodeMath")
    inv.operation = "POWER"
    inv.inputs[1].default_value = 3.0
    oneminus = nt.nodes.new("ShaderNodeMath")
    oneminus.operation = "SUBTRACT"
    oneminus.inputs[0].default_value = 1.0
    nt.links.new(lw.outputs["Facing"], oneminus.inputs[1])
    nt.links.new(oneminus.outputs[0], inv.inputs[0])  # 1 - facing: 0 at the silhouette, 1 at the centre
    inv.inputs[1].default_value = 4.0
    mul = nt.nodes.new("ShaderNodeMath")
    mul.operation = "MULTIPLY"
    mul.inputs[1].default_value = 0.9
    nt.links.new(inv.outputs[0], mul.inputs[0])
    nt.links.new(mul.outputs[0], em.inputs["Strength"])
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    add = nt.nodes.new("ShaderNodeAddShader")
    nt.links.new(tr.outputs[0], add.inputs[0])
    nt.links.new(em.outputs[0], add.inputs[1])
    nt.links.new(add.outputs[0], nt.nodes["Material Output"].inputs["Surface"])
    for o in bpy.data.objects:
        if o.name == "halos":
            o.visible_shadow = False
    # threads of light rising from every open book into the lowest stars
    stream_m = mat("stream", (1, 0.7, 0.4), emit=(1.0, 0.56, 0.24), strength=2.2)
    low = sorted(range(len(pts)), key=lambda i: pts[i].z)[:30]
    paths = []
    for src, s in sources:
        near = sorted(range(len(pts)), key=lambda i: abs(pts[i].x - src.x) + abs(pts[i].y - src.y) * 0.5 + (pts[i].z - c.z) * 0.8)[:10]
        for k in range(int(14 * s)):
            p0 = src + Vector((rnd.uniform(-0.16, 0.16) * s, rnd.uniform(-0.10, 0.10) * s, 0.0))
            p3 = pts[rnd.choice(near)]
            twist = Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), 0)) * 0.05
            p1 = p0.lerp(p3, 0.3) + twist + Vector((0, 0, 0.04))
            p2 = p0.lerp(p3, 0.7) - twist * 0.5
            paths.append([p0, p1, p2, p3])
    curve_obj("streams", paths, 0.0002, stream_m)
    # dust: faint motes drifting through the scene
    spark = mat("spark", (1, 0.9, 0.7), emit=(1.0, 0.8, 0.5), strength=14)
    bm = bmesh.new()
    for k in range(260):
        q = c + Vector((rnd.uniform(-1.3, 1.3), rnd.uniform(-0.6, 0.8), rnd.uniform(-0.7, 0.6)))
        bmesh.ops.create_icosphere(bm, subdivisions=1, radius=rnd.uniform(0.0006, 0.0018), matrix=mathutils.Matrix.Translation(q))
    me = bpy.data.meshes.new("dust")
    bm.to_mesh(me)
    bm.free()
    link_obj("dust", me).data.materials.append(spark)
    light("POINT", (c.x, c.y, c.z - 0.1), 18, (1.0, 0.66, 0.38), size=0.4)
    light("POINT", (bx, by, top + 0.15), 1.5, (1.0, 0.7, 0.4), size=0.1)
    # high window: cold moonlight shafts through dust
    sp = light("SPOT", (-2.6, 2.4, 3.8), 800, (0.55, 0.66, 1.0), size=0.25, spot=math.radians(18))
    dvec = Vector((bx - 0.6, by, top)) - sp.location
    sp.rotation_euler = dvec.to_track_quat("-Z", "Y").to_euler()
    # far pendant lamps for bokeh
    for x, y in ((-1.6, 2.4), (-0.4, 2.8), (1.9, 2.5), (-2.6, 2.9)):
        glow = mat("bulb", (1, 0.8, 0.6), emit=(1.0, 0.62, 0.32), strength=60)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.05, location=(x, y, 1.75 + 0.25 * math.sin(x * 3)))
        bpy.context.object.data.materials.append(glow)
        light("POINT", (x, y, 1.65), 10, (1.0, 0.62, 0.32), size=0.05)
    volume_box((7, 6, 4.2), (0, 0.8, 2.1), density=float(__import__("os").environ.get("FOG", "0.006")), color=(1.0, 0.92, 0.85))
    sc.view_settings.look = "AgX - Punchy"
    if close:
        cam_loc = Vector((bx - 0.2, by - 1.75, top + 0.40))
        camera(cam_loc, (bx + 0.02, by + 0.2, top + 0.30), lens=50, dof=(cam_loc - c).length, fstop=2.2)
        return sc
    cam_loc = Vector((bx - 0.95, by - 2.35, top + 0.62))
    camera(cam_loc, (bx - 0.40, by + 0.2, top + 0.28), lens=50, dof=(cam_loc - c).length, fstop=1.4)
    return sc


SCENES = {
    "splash": lambda: splash((2400, 1200)),
    "splash_wide": lambda: splash((2560, 1067)),
    "hero": lambda: hero(),
    "social": lambda: hero((1280, 640), (0.70, 0.62, 0.48)),
    "icon": lambda: splash((1024, 1024), close=True),
    "icon_book": icon,
    "drop": scene_drop,
    "archive": scene_archive,
    "catalogue": scene_catalogue,
    "reading": scene_reading,
}

if __name__ == "__main__":
    sc = SCENES[SCENE]()
    sc.render.resolution_percentage = PERCENT
    import os
    for key in filter(None, os.environ.get("HIDE", "").split(",")):
        for ob in bpy.data.objects:
            if ob.name.startswith(key):
                ob.hide_render = True
        if key == "hair":
            for ob in bpy.data.objects:
                for m in list(ob.modifiers):
                    if m.type == "PARTICLE_SYSTEM":
                        m.show_render = False
    sc.cycles.volume_step_rate = 4
    sc.render.filepath = OUT
    sc.render.image_settings.file_format = "PNG"
    bpy.ops.render.render(write_still=True)
    print("WROTE", OUT)
