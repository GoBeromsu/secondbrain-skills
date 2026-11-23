"""Showcase render for secondbrain-skills: books flying off a moonlit stone terrace into a starry sky.

Run:  blender -b -P scripts/art/showcase.py -- <out.png> [samples] [resolution %]
Everything is procedural (geometry, materials, sky); no image, HDRI or downloaded asset is used.
Blender 5.x, Cycles.
"""
import math
import random
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector, noise

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else ["/tmp/showcase.png"]
OUT = argv[0]
SAMPLES = int(argv[1]) if len(argv) > 1 else 256
PERCENT = int(argv[2]) if len(argv) > 2 else 100
RES = (2400, 1200)


# ------------------------------------------------------------------ basics
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
    sc.cycles.max_bounces = 8
    sc.cycles.volume_bounces = 1
    sc.cycles.volume_step_rate = 3
    sc.render.resolution_x, sc.render.resolution_y = RES
    sc.render.resolution_percentage = PERCENT
    w = bpy.data.worlds.new("night")
    sc.world = w
    w.use_nodes = True
    return sc


def link(name, data):
    o = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(o)
    return o


def node(nt, kind, **inputs):
    n = nt.nodes.new(kind)
    for k, v in inputs.items():
        if k.startswith("_"):
            setattr(n, k[1:], v)
        else:
            n.inputs[k].default_value = v
    return n


def mathn(nt, op, a=None, b=None, **kw):
    n = nt.nodes.new("ShaderNodeMath")
    n.operation = op
    for i, v in enumerate((a, b)):
        if v is None:
            continue
        if isinstance(v, (int, float)):
            n.inputs[i].default_value = v
        else:
            nt.links.new(v, n.inputs[i])
    for k, v in kw.items():
        setattr(n, k, v)
    return n.outputs[0]


def principled(name, color=(0.8, 0.8, 0.8), rough=0.5, metal=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*color, 1)
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    return m, m.node_tree, p


def emissive(name, color, strength):
    m, nt, p = principled(name, color)
    p.inputs["Emission Color"].default_value = (*color, 1)
    p.inputs["Emission Strength"].default_value = strength
    return m


def bump(nt, p, height, strength, distance=0.01):
    b = node(nt, "ShaderNodeBump", Strength=strength, Distance=distance)
    nt.links.new(height, b.inputs["Height"])
    nt.links.new(b.outputs["Normal"], p.inputs["Normal"])


def box(name, size, loc, m=None, bevel=0.0, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.scale = size
    bpy.ops.object.transform_apply(scale=True)
    if bevel:
        md = o.modifiers.new("bevel", "BEVEL")
        md.width = bevel
        md.segments = 3
    if m:
        o.data.materials.append(m)
    return o


# ------------------------------------------------------------------ materials
def paper_material():
    m, nt, p = principled("paper", (0.83, 0.78, 0.66), 0.62)
    uv = node(nt, "ShaderNodeUVMap")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(uv.outputs["UV"], sep.inputs[0])
    u, v = sep.outputs["X"], sep.outputs["Y"]
    # printed lines of text: rows along v, word gaps along u, inside margins
    rows = mathn(nt, "FRACT", mathn(nt, "MULTIPLY", v, 46.0))
    row_mask = mathn(nt, "LESS_THAN", rows, 0.34)
    words = node(nt, "ShaderNodeTexNoise", Scale=1.0, Detail=0.0)
    wv = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(mathn(nt, "MULTIPLY", u, 70.0), wv.inputs["X"])
    nt.links.new(mathn(nt, "FLOOR", mathn(nt, "MULTIPLY", v, 46.0)), wv.inputs["Y"])
    nt.links.new(wv.outputs[0], words.inputs["Vector"])
    word_mask = mathn(nt, "GREATER_THAN", words.outputs["Fac"], 0.42)
    inside_u = mathn(nt, "MULTIPLY", mathn(nt, "GREATER_THAN", u, 0.14), mathn(nt, "LESS_THAN", u, 0.90))
    inside_v = mathn(nt, "MULTIPLY", mathn(nt, "GREATER_THAN", v, 0.09), mathn(nt, "LESS_THAN", v, 0.90))
    ink = mathn(nt, "MULTIPLY", mathn(nt, "MULTIPLY", row_mask, word_mask), mathn(nt, "MULTIPLY", inside_u, inside_v))
    grain = node(nt, "ShaderNodeTexNoise", Scale=180.0, Detail=6.0)
    tone = node(nt, "ShaderNodeMix", _data_type="RGBA", A=(0.80, 0.74, 0.60, 1), B=(0.88, 0.84, 0.74, 1))
    nt.links.new(grain.outputs["Fac"], tone.inputs["Factor"])
    mix = node(nt, "ShaderNodeMix", _data_type="RGBA", B=(0.16, 0.13, 0.11, 1))
    nt.links.new(mathn(nt, "MULTIPLY", ink, 0.85), mix.inputs["Factor"])
    nt.links.new(tone.outputs["Result"], mix.inputs["A"])
    nt.links.new(mix.outputs["Result"], p.inputs["Base Color"])
    # paper lets moonlight through
    tr = nt.nodes.new("ShaderNodeBsdfTranslucent")
    nt.links.new(tone.outputs["Result"], tr.inputs["Color"])
    ms = node(nt, "ShaderNodeMixShader", Fac=0.28)
    nt.links.new(p.outputs[0], ms.inputs[1])
    nt.links.new(tr.outputs[0], ms.inputs[2])
    nt.links.new(ms.outputs[0], nt.nodes["Material Output"].inputs["Surface"])
    return m


def cloth_material(name, color):
    m, nt, p = principled(name, color, 0.72)
    p.inputs["Sheen Weight"].default_value = 0.15
    p.inputs["Sheen Tint"].default_value = (*[min(1, c * 2) for c in color], 1)
    tc = node(nt, "ShaderNodeTexCoord")
    weave = node(nt, "ShaderNodeTexWave", Scale=900.0, Distortion=0.0)
    weave.bands_direction = "DIAGONAL"
    nt.links.new(tc.outputs["Object"], weave.inputs["Vector"])
    wear = node(nt, "ShaderNodeTexNoise", Scale=18.0, Detail=8.0)
    nt.links.new(tc.outputs["Object"], wear.inputs["Vector"])
    shade = node(nt, "ShaderNodeMix", _data_type="RGBA", A=(*[c * 0.65 for c in color], 1), B=(*[min(1, c * 1.25) for c in color], 1))
    nt.links.new(wear.outputs["Fac"], shade.inputs["Factor"])
    nt.links.new(shade.outputs["Result"], p.inputs["Base Color"])
    bump(nt, p, mathn(nt, "ADD", weave.outputs["Fac"], mathn(nt, "MULTIPLY", wear.outputs["Fac"], 0.5)), 0.25, 0.002)
    return m


def gold_material():
    m, nt, p = principled("gold", (0.86, 0.62, 0.28), 0.25, 1.0)
    return m


def stone_material():
    m, nt, p = principled("stone", (0.42, 0.39, 0.35), 0.82)
    tc = node(nt, "ShaderNodeTexCoord")
    brick = node(nt, "ShaderNodeTexBrick", Scale=1.2, **{"Mortar Size": 0.012})
    brick.inputs["Color1"].default_value = (0.40, 0.37, 0.33, 1)
    brick.inputs["Color2"].default_value = (0.33, 0.30, 0.27, 1)
    brick.inputs["Mortar"].default_value = (0.12, 0.11, 0.10, 1)
    nt.links.new(tc.outputs["Object"], brick.inputs["Vector"])
    grit = node(nt, "ShaderNodeTexNoise", Scale=60.0, Detail=12.0)
    nt.links.new(tc.outputs["Object"], grit.inputs["Vector"])
    moss = node(nt, "ShaderNodeTexNoise", Scale=3.0, Detail=6.0)
    nt.links.new(tc.outputs["Object"], moss.inputs["Vector"])
    mm = node(nt, "ShaderNodeMix", _data_type="RGBA", B=(0.16, 0.20, 0.10, 1))
    nt.links.new(mathn(nt, "MULTIPLY", mathn(nt, "GREATER_THAN", moss.outputs["Fac"], 0.62), 0.6), mm.inputs["Factor"])
    nt.links.new(brick.outputs["Color"], mm.inputs["A"])
    gm = node(nt, "ShaderNodeMix", _data_type="RGBA", _blend_type="MULTIPLY", Factor=0.5)
    nt.links.new(mm.outputs["Result"], gm.inputs["A"])
    nt.links.new(grit.outputs["Color"], gm.inputs["B"])
    nt.links.new(gm.outputs["Result"], p.inputs["Base Color"])
    bump(nt, p, mathn(nt, "ADD", mathn(nt, "MULTIPLY", brick.outputs["Fac"], -1.0), mathn(nt, "MULTIPLY", grit.outputs["Fac"], 0.5)), 0.5, 0.01)
    return m


def wood_material(name="oak", base=(0.20, 0.10, 0.05)):
    m, nt, p = principled(name, base, 0.45)
    tc = node(nt, "ShaderNodeTexCoord")
    mp = node(nt, "ShaderNodeMapping", Scale=(0.6, 0.6, 12.0))
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    wave = node(nt, "ShaderNodeTexWave", Scale=2.5, Distortion=8.0, Detail=6.0)
    wave.wave_type = "RINGS"
    nt.links.new(mp.outputs["Vector"], wave.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (*[c * 0.5 for c in base], 1)
    ramp.color_ramp.elements[1].color = (*[min(1, c * 1.5) for c in base], 1)
    nt.links.new(wave.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], p.inputs["Base Color"])
    bump(nt, p, wave.outputs["Fac"], 0.1, 0.003)
    return m


# ------------------------------------------------------------------ book
def strip_mesh(bm, uvl, side, w, l, th, bend, segs, flutter):
    x = z = 0.0
    ds = w / segs
    rows = []
    for s in range(segs + 1):
        rows.append(((side * x, z), s / segs))
        ang = th + (bend + flutter) * (s / segs) ** 1.6
        x += math.cos(ang) * ds
        z += math.sin(ang) * ds
    vrows = [[bm.verts.new((px, yy, pz)) for yy in (-l / 2, l / 2)] for (px, pz), _ in rows]
    for k, (a, b) in enumerate(zip(vrows, vrows[1:])):
        quad = (a[0], b[0], b[1], a[1]) if side > 0 else (a[0], a[1], b[1], b[0])
        f = bm.faces.new(quad)
        u0, u1 = rows[k][1], rows[k + 1][1]
        uvs = {a[0]: (u0, 0), b[0]: (u1, 0), b[1]: (u1, 1), a[1]: (u0, 1)}
        for loop in f.loops:
            loop[uvl].uv = uvs[loop.vert]


def book(name, loc, rot, s, cover_m, paper_m, gold_m, rnd, cover_deg, page_deg, pages=14, bend=-0.5):
    """An open book in flight: two cover wings and two fans of curved pages, spine along y."""
    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    w, l = 0.15 * s, 0.22 * s
    for side in (-1, 1):
        bm = bmesh.new()
        uvl = bm.loops.layers.uv.new("UVMap")
        lo, hi = math.radians(cover_deg) + 0.04, math.radians(page_deg)
        for i in range(pages):
            f = i / (pages - 1)
            th = lo + (hi - lo) * (f ** 0.8)
            strip_mesh(bm, uvl, side, w * 0.97, l * 0.96, th, bend * (1 - 0.6 * f), 12, rnd.uniform(-0.12, 0.12))
        me = bpy.data.meshes.new(f"{name}_pages{side}")
        bm.to_mesh(me)
        bm.free()
        po = link(f"{name}_pages{side}", me)
        po.data.materials.append(paper_m)
        po.modifiers.new("solid", "SOLIDIFY").thickness = 0.0004 * s
        po.parent = root
        # cover board
        bm = bmesh.new()
        uvl = bm.loops.layers.uv.new("UVMap")
        strip_mesh(bm, uvl, side, w * 1.03, l * 1.04, math.radians(cover_deg), bend * 0.25, 6, 0.0)
        me = bpy.data.meshes.new(f"{name}_cover{side}")
        bm.to_mesh(me)
        bm.free()
        co = link(f"{name}_cover{side}", me)
        co.data.materials.append(cover_m)
        sm = co.modifiers.new("solid", "SOLIDIFY")
        sm.thickness = 0.004 * s
        sm.offset = 1.0
        bv = co.modifiers.new("bevel", "BEVEL")
        bv.width = 0.0012 * s
        bv.segments = 2
        co.parent = root
    # rounded spine with gilt bands
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.012 * s, depth=l * 1.04, location=(0, 0, -0.006 * s), rotation=(math.pi / 2, 0, 0))
    sp = bpy.context.object
    sp.name = f"{name}_spine"
    sp.scale = (1.0, 0.55, 1.0)
    sp.data.materials.append(cover_m)
    sp.parent = root
    for yb in (-0.38, 0.30, 0.36):
        bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.0123 * s, depth=0.004 * s, location=(0, yb * l, -0.006 * s), rotation=(math.pi / 2, 0, 0))
        g = bpy.context.object
        g.scale = (1.0, 0.56, 1.0)
        g.data.materials.append(gold_m)
        g.parent = root
    root.location = loc
    root.rotation_euler = rot
    return root


def loose_page(name, loc, rot, s, paper_m, rnd):
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.new("UVMap")
    strip_mesh(bm, uvl, 1, 0.15 * s, 0.22 * s, 0.0, rnd.uniform(-0.9, 0.9), 12, 0.0)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    o = link(name, me)
    o.data.materials.append(paper_m)
    o.modifiers.new("solid", "SOLIDIFY").thickness = 0.0004
    o.location = loc
    o.rotation_euler = rot
    return o


# ------------------------------------------------------------------ sky
def night_sky(sc):
    nt = sc.world.node_tree
    bg = nt.nodes["Background"]
    tc = node(nt, "ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Window"], sep.inputs[0])
    x, y = sep.outputs["X"], sep.outputs["Y"]
    grad = nt.nodes.new("ShaderNodeValToRGB")
    e = grad.color_ramp.elements
    e[0].position, e[0].color = 0.0, (0.030, 0.034, 0.060, 1)
    e[1].position, e[1].color = 1.0, (0.0015, 0.0022, 0.0080, 1)
    m = e.new(0.30)
    m.color = (0.010, 0.013, 0.032, 1)
    nt.links.new(y, grad.inputs["Fac"])
    # milky way band from lower left to upper right, with dust lanes
    d = mathn(nt, "SUBTRACT", mathn(nt, "ADD", mathn(nt, "MULTIPLY", x, -0.62), y), 0.30)
    band = mathn(nt, "EXPONENT", mathn(nt, "MULTIPLY", mathn(nt, "MULTIPLY", d, d), -38.0))
    core = mathn(nt, "EXPONENT", mathn(nt, "MULTIPLY", mathn(nt, "MULTIPLY", d, d), -160.0))
    n1 = node(nt, "ShaderNodeTexNoise", Scale=5.0, Detail=12.0, Roughness=0.62)
    nt.links.new(tc.outputs["Window"], n1.inputs["Vector"])
    n2 = node(nt, "ShaderNodeTexNoise", Scale=11.0, Detail=10.0, Roughness=0.7)
    nt.links.new(tc.outputs["Window"], n2.inputs["Vector"])
    lanes = mathn(nt, "SUBTRACT", 1.0, mathn(nt, "MULTIPLY", core, mathn(nt, "POWER", mathn(nt, "MAXIMUM", mathn(nt, "SUBTRACT", n2.outputs["Fac"], 0.45), 0.0), 0.6)))
    glow = mathn(nt, "MULTIPLY", mathn(nt, "MULTIPLY", band, n1.outputs["Fac"]), lanes)
    mw = node(nt, "ShaderNodeMix", _data_type="RGBA", _blend_type="ADD")
    nt.links.new(mathn(nt, "MULTIPLY", glow, 2.4), mw.inputs["Factor"])
    nt.links.new(grad.outputs["Color"], mw.inputs["A"])
    mw.inputs["B"].default_value = (0.060, 0.055, 0.075, 1)
    warm = node(nt, "ShaderNodeMix", _data_type="RGBA", _blend_type="ADD")
    nt.links.new(mathn(nt, "MULTIPLY", mathn(nt, "MULTIPLY", core, n1.outputs["Fac"]), 0.9), warm.inputs["Factor"])
    nt.links.new(mw.outputs["Result"], warm.inputs["A"])
    warm.inputs["B"].default_value = (0.085, 0.060, 0.045, 1)
    nt.links.new(warm.outputs["Result"], bg.inputs["Color"])


def stars(rnd, cam, radius, n, at):
    bm = bmesh.new()
    col = bm.loops.layers.color.new("starcol")
    temps = [(0.62, 0.72, 1.0), (0.85, 0.90, 1.0), (1.0, 1.0, 1.0), (1.0, 0.92, 0.78), (1.0, 0.78, 0.55)]
    bright = []
    for _ in range(n):
        u, v = rnd.random(), rnd.uniform(0.25, 1.05)
        # denser along the milky way band
        dband = (-0.62 * u + v - 0.30)
        if abs(dband) > 0.12 and rnd.random() < 0.55:
            continue
        p = cam + (at(u, v, 1.0) - cam).normalized() * radius
        mag = rnd.random() ** 9
        r = radius * (0.00018 + 0.0013 * mag)
        res = bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r, matrix=Matrix.Translation(p))
        c = rnd.choice(temps)
        k = 0.6 + 0.4 * rnd.random()
        for vtx in res["verts"]:
            for f in vtx.link_faces:
                for loop in f.loops:
                    loop[col] = (c[0] * k, c[1] * k, c[2] * k, 1)
        if mag > 0.12:
            bright.append((p, u, v))
    me = bpy.data.meshes.new("stars")
    bm.to_mesh(me)
    bm.free()
    o = link("stars", me)
    m, nt, p = principled("star", (0, 0, 0), 1.0)
    a = node(nt, "ShaderNodeAttribute", _attribute_name="starcol")
    nt.links.new(a.outputs["Color"], p.inputs["Emission Color"])
    p.inputs["Emission Strength"].default_value = 16.0
    o.data.materials.append(m)
    o.visible_shadow = False
    return bright


def constellation(rnd, bright, u0, v0, count, radius, name):
    near = sorted(bright, key=lambda b: (b[1] - u0) ** 2 + ((b[2] - v0) * 2) ** 2)[:count]
    near = [b for b in near if abs(b[1] - u0) < 0.12 and abs(b[2] - v0) < 0.14]
    if len(near) < 3:
        return
    pts = [b[0] for b in near]
    inside, edges = {0}, []
    while len(inside) < len(pts):
        i, j = min(((i, j) for i in inside for j in range(len(pts)) if j not in inside), key=lambda e: (pts[e[0]] - pts[e[1]]).length)
        edges.append((i, j))
        inside.add(j)
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = radius * 0.00028
    for i, j in edges:
        a, b = pts[i], pts[j]
        sp = cu.splines.new("POLY")
        sp.points.add(1)
        sp.points[0].co = (*(a + (b - a) * 0.06), 1)
        sp.points[1].co = (*(b + (a - b) * 0.06), 1)
    o = link(name, cu)
    o.data.materials.append(emissive(name + "_m", (0.62, 0.66, 1.0), 1.1))
    o.visible_shadow = False


def moon(cam, at, radius):
    p = cam + (at(0.70, 0.90, 1.0) - cam).normalized() * radius
    bpy.ops.mesh.primitive_uv_sphere_add(segments=64, ring_count=32, radius=radius * 0.011, location=p)
    o = bpy.context.object
    m, nt, pr = principled("moon", (0.8, 0.8, 0.8), 0.9)
    tc = node(nt, "ShaderNodeTexCoord")
    maria = node(nt, "ShaderNodeTexNoise", Scale=2.2, Detail=6.0)
    craters = node(nt, "ShaderNodeTexVoronoi", Scale=9.0)
    nt.links.new(tc.outputs["Object"], maria.inputs["Vector"])
    nt.links.new(tc.outputs["Object"], craters.inputs["Vector"])
    tone = node(nt, "ShaderNodeMix", _data_type="RGBA", A=(0.55, 0.56, 0.60, 1), B=(0.95, 0.95, 0.92, 1))
    nt.links.new(maria.outputs["Fac"], tone.inputs["Factor"])
    nt.links.new(tone.outputs["Result"], pr.inputs["Emission Color"])
    pr.inputs["Emission Strength"].default_value = 3.5
    bump(nt, pr, craters.outputs["Distance"], 0.6, radius * 0.0005)
    o.data.materials.append(m)
    # halo
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=24, radius=radius * 0.05, location=p)
    h = bpy.context.object
    hm = bpy.data.materials.new("moonhalo")
    hm.use_nodes = True
    hn = hm.node_tree
    hn.nodes.remove(hn.nodes["Principled BSDF"])
    lw = node(hn, "ShaderNodeLayerWeight", Blend=0.5)
    em = node(hn, "ShaderNodeEmission", Color=(0.60, 0.68, 1.0, 1))
    nt2 = hn
    fac = mathn(nt2, "POWER", mathn(nt2, "SUBTRACT", 1.0, lw.outputs["Facing"]), 6.0)
    nt2.links.new(mathn(nt2, "MULTIPLY", fac, 0.35), em.inputs["Strength"])
    tr = hn.nodes.new("ShaderNodeBsdfTransparent")
    add = hn.nodes.new("ShaderNodeAddShader")
    hn.links.new(tr.outputs[0], add.inputs[0])
    hn.links.new(em.outputs[0], add.inputs[1])
    hn.links.new(add.outputs[0], hn.nodes["Material Output"].inputs["Surface"])
    h.data.materials.append(hm)
    h.visible_shadow = False
    return p


# ------------------------------------------------------------------ land
def ridge(name, y, base, height, xspan, seed, mat_):
    bm = bmesh.new()
    nx, ny = 360, 14
    verts = []
    for j in range(ny + 1):
        row = []
        yy = y + j * (height * 0.6) / ny
        for i in range(nx + 1):
            xx = -xspan / 2 + xspan * i / nx
            h = noise.fractal(Vector((xx / (height * 2.2) + seed, seed * 3.1, 0)), 0.9, 2.1, 6) * 0.5 + 0.5
            ridge_h = base + height * (0.35 + 0.65 * h) * (1 - (j / ny) ** 2 * 0.0)
            z = base + (ridge_h - base) * math.sin(min(1.0, (j + 1) / ny) * math.pi / 2)
            row.append(bm.verts.new((xx, yy, z if j else base - 40)))
        verts.append(row)
    for j in range(ny):
        for i in range(nx):
            bm.faces.new((verts[j][i], verts[j][i + 1], verts[j + 1][i + 1], verts[j + 1][i]))
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    o = link(name, me)
    o.data.materials.append(mat_)
    for pl in me.polygons:
        pl.use_smooth = True
    return o


def volume(name, size, loc, density, color, falloff_z=None):
    o = box(name, size, loc)
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    v = node(nt, "ShaderNodeVolumePrincipled", Color=(*color, 1), Anisotropy=0.45)
    if falloff_z:
        tc = node(nt, "ShaderNodeTexCoord")
        sep = nt.nodes.new("ShaderNodeSeparateXYZ")
        nt.links.new(tc.outputs["Object"], sep.inputs[0])
        # thick at the bottom of the box, fading upward, broken up by noise
        h = mathn(nt, "POWER", mathn(nt, "MAXIMUM", mathn(nt, "SUBTRACT", 0.5, sep.outputs["Z"]), 0.0), falloff_z)
        nz = node(nt, "ShaderNodeTexNoise", Scale=0.08, Detail=4.0)
        nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
        dens = mathn(nt, "MULTIPLY", mathn(nt, "MULTIPLY", h, nz.outputs["Fac"]), density)
        nt.links.new(dens, v.inputs["Density"])
    else:
        v.inputs["Density"].default_value = density
    nt.links.new(v.outputs[0], nt.nodes["Material Output"].inputs["Volume"])
    o.data.materials.append(m)
    o.visible_shadow = False
    return o


def baluster(x, y, stone):
    for (r, h, z) in ((0.075, 0.08, 0.04), (0.05, 0.10, 0.13), (0.085, 0.22, 0.30), (0.045, 0.12, 0.47), (0.07, 0.06, 0.56)):
        bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=r, depth=h, location=(x, y, z))
        o = bpy.context.object
        md = o.modifiers.new("bevel", "BEVEL")
        md.width = 0.02
        md.segments = 4
        bpy.ops.object.shade_smooth()
        o.data.materials.append(stone)


# ------------------------------------------------------------------ scene
def build():
    sc = reset()
    rnd = random.Random(12)
    night_sky(sc)
    paper = paper_material()
    gold = gold_material()
    stone = stone_material()
    oak = wood_material()
    covers = [cloth_material(f"cloth{k}", c) for k, c in enumerate(
        [(0.20, 0.025, 0.02), (0.03, 0.06, 0.18), (0.035, 0.12, 0.07), (0.34, 0.19, 0.05), (0.14, 0.05, 0.18), (0.06, 0.12, 0.16), (0.30, 0.24, 0.16)])]

    cam = Vector((-1.1, -1.7, 1.25))
    target = Vector((1.4, 6.0, 2.05))
    fwd = (target - cam).normalized()
    right = fwd.cross(Vector((0, 0, 1))).normalized()
    up = right.cross(fwd).normalized()
    tan_h = 18 / 26
    tan_v = tan_h / 2

    def at(u, v, depth):
        return cam + (fwd + right * ((u - 0.5) * 2 * tan_h) + up * ((v - 0.5) * 2 * tan_v)) * depth

    # terrace: stone floor, balustrade, desk with candle lantern and books
    floor = box("terrace", (8, 5, 0.2), (0.5, 0.2, -0.1), stone, bevel=0.02)
    rail_y = 2.4
    box("rail", (8, 0.28, 0.1), (0.5, rail_y, 0.65), stone, bevel=0.02)
    box("plinth", (8, 0.3, 0.06), (0.5, rail_y, 0.03), stone, bevel=0.01)
    for k in range(-14, 18):
        baluster(0.5 + k * 0.24, rail_y, stone)
    top = 0.78
    box("desk_top", (1.5, 0.75, 0.05), (-1.25, 0.9, top - 0.025), oak, bevel=0.01)
    for lx in (-1.92, -0.58):
        for ly in (0.6, 1.2):
            box("leg", (0.06, 0.06, top - 0.05), (lx, ly, (top - 0.05) / 2), oak, bevel=0.006)
    # a closed stack and an open book on the desk
    for k, c in enumerate((covers[2], covers[0], covers[5])):
        h = (0.045, 0.035, 0.05)[k]
        z = top + sum((0.045, 0.035, 0.05)[:k]) + h / 2
        box(f"stack{k}", (0.24 - 0.015 * k, 0.17, h), (-1.7, 1.0, z), c, bevel=0.004, rot=(0, 0, 0.25 - 0.2 * k))
        box(f"stackp{k}", (0.23 - 0.015 * k, 0.172, h - 0.008), (-1.695, 1.0, z), paper, bevel=0.002, rot=(0, 0, 0.25 - 0.2 * k))
    book("deskbook", (-1.05, 0.85, top + 0.012), (0, 0, 0.3), 1.25, covers[1], paper, gold, rnd, 4, 12, pages=10, bend=0.0)
    # candle lantern
    brass = principled("brass", (0.78, 0.55, 0.25), 0.3, 1.0)[0]
    glass = principled("glass", (1, 1, 1), 0.02)[0]
    glass.node_tree.nodes["Principled BSDF"].inputs["Transmission Weight"].default_value = 1.0
    glass.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.08
    lx, ly = -1.45, 1.12
    box("lantern_base", (0.11, 0.11, 0.02), (lx, ly, top + 0.01), brass[0] if isinstance(brass, tuple) else brass, bevel=0.003)
    box("lantern_top", (0.11, 0.11, 0.02), (lx, ly, top + 0.19), brass, bevel=0.003)
    for dx in (-0.05, 0.05):
        for dy in (-0.05, 0.05):
            box("lantern_post", (0.008, 0.008, 0.17), (lx + dx, ly + dy, top + 0.1), brass)
    box("lantern_glass", (0.095, 0.095, 0.16), (lx, ly, top + 0.10), glass)
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.018, depth=0.07, location=(lx, ly, top + 0.055))
    bpy.context.object.data.materials.append(principled("wax", (0.9, 0.85, 0.75), 0.5)[0])
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.008, location=(lx, ly, top + 0.10))
    fl = bpy.context.object
    fl.scale = (1, 1, 2.2)
    fl.data.materials.append(emissive("flame", (1.0, 0.55, 0.18), 25))
    cl = bpy.data.lights.new("candle", "POINT")
    cl.energy = 14
    cl.color = (1.0, 0.55, 0.25)
    cl.shadow_soft_size = 0.01
    link("candle", cl).location = (lx, ly, top + 0.10)

    # land: valley mist and ridges fading into the night
    rock = principled("rock", (0.05, 0.055, 0.065), 0.9)[0]
    ridge("ridge1", 40, -30, 22, 260, 1.3, rock)
    ridge("ridge2", 85, -30, 34, 420, 4.7, rock)
    ridge("ridge3", 150, -30, 48, 700, 9.1, rock)
    volume("haze", (700, 260, 90), (0, 120, 10), 0.0016, (0.55, 0.62, 0.85))

    # sky objects
    bright = stars(rnd, cam, 900.0, 4200, at)
    for k, (u, v, n) in enumerate(((0.60, 0.90, 7), (0.90, 0.62, 6), (0.40, 0.95, 5), (0.97, 0.93, 5))):
        constellation(rnd, bright, u, v, n, 900.0, f"const{k}")
    moon(cam, at, 880.0)
    sun = bpy.data.lights.new("moonlight", "SUN")
    sun.energy = 0.35
    sun.color = (0.62, 0.70, 1.0)
    sun.angle = math.radians(0.8)
    so = link("moonlight", sun)
    so.rotation_euler = (math.radians(62), 0, math.radians(200))

    # books in flight: from the desk over the balustrade toward the moon
    n = 11
    for k in range(n):
        tt = k / (n - 1)
        u = 0.26 + 0.66 * tt + 0.03 * math.sin(tt * 11.0) + rnd.uniform(-0.015, 0.015)
        v = 0.50 + 0.30 * tt + 0.10 * math.sin(tt * 5.5) + rnd.uniform(-0.02, 0.02)
        depth = 3.0 + 14.0 * tt ** 1.5 + rnd.uniform(-0.2, 0.2)
        p = at(u, v, depth)
        rot = (math.radians(rnd.uniform(-30, 10)), math.radians(rnd.uniform(-20, 20)), math.radians(rnd.uniform(-50, 50)))
        cd = rnd.uniform(4, 22)
        book(f"fly{k}", p, rot, rnd.uniform(1.4, 1.8), covers[k % len(covers)], paper, gold, rnd, cd, cd + rnd.uniform(18, 38), bend=-0.35)
    for k in range(9):
        tt = rnd.uniform(0.02, 0.75)
        p = at(0.27 + 0.6 * tt + rnd.uniform(-0.07, 0.07), 0.42 + 0.4 * tt + rnd.uniform(-0.08, 0.08), 2.3 + 9 * tt ** 1.4)
        loose_page(f"loose{k}", p, (rnd.uniform(0, 6), rnd.uniform(0, 6), rnd.uniform(0, 6)), 1.5, paper, rnd)
    # warm bounce from the lantern side onto the nearest books
    fill = bpy.data.lights.new("lanternfill", "AREA")
    fill.energy = 38
    fill.size = 1.0
    fill.color = (1.0, 0.6, 0.32)
    fo = link("lanternfill", fill)
    fo.location = (-1.4, 0.8, 1.1)
    fo.rotation_euler = (at(0.4, 0.55, 3.5) - fo.location).to_track_quat("-Z", "Y").to_euler()

    key = bpy.data.lights.new("skykey", "AREA")
    key.energy = 55
    key.size = 6.0
    key.color = (0.55, 0.62, 1.0)
    ko = link("skykey", key)
    ko.location = cam + Vector((-2.5, -4.0, 4.0))
    ko.rotation_euler = (at(0.55, 0.6, 5.0) - ko.location).to_track_quat("-Z", "Y").to_euler()
    cd_ = bpy.data.cameras.new("cam")
    cd_.lens = 26
    cd_.dof.use_dof = True
    cd_.dof.focus_distance = 3.0
    cd_.dof.aperture_fstop = 5.6
    co = link("cam", cd_)
    co.location = cam
    co.rotation_euler = fwd.to_track_quat("-Z", "Y").to_euler()
    sc.camera = co
    sc.view_settings.exposure = 0.6
    return sc


if __name__ == "__main__":
    sc = build()
    sc.render.filepath = OUT
    sc.render.image_settings.file_format = "PNG"
    bpy.ops.render.render(write_still=True)
    print("WROTE", OUT)
