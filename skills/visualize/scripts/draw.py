import hashlib, json, os, re, string, sys, unicodedata, uuid
from collections import Counter

PAL = {"blue": ("#a5d8ff", "#1971c2"), "green": ("#b2f2bb", "#2f9e44"), "yellow": ("#ffec99", "#f08c00"),
       "red": ("#ffc9c9", "#e03131"), "purple": ("#d0bfff", "#6741d9"), "gray": ("#e9ecef", "#495057"),
       "note": ("#fff3bf", "#e67700")}
SHAPES = ("rectangle", "ellipse", "diamond", "text", "note")
HEADS = {"arrow": "arrow", "triangle": "triangle", "bar": "bar", "dot": "dot", "none": None}
def head(sig):
    return "---\nexcalidraw-plugin: parsed\n%s: %s\n---\n\n# Excalidraw Data\n\n## Text Elements\n" % ("draw-py", sig)


B64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="


def lz_decode(b64):
    """LZString decompressFromBase64, the format the Excalidraw plugin saves."""
    vals = [B64.index(c) for c in re.sub(r"\s", "", b64)]
    pos, bit, n = 0, 0, 0

    def read(k):
        nonlocal pos, bit, n
        r = 0
        for i in range(k):
            r |= ((vals[n] >> (5 - pos)) & 1) << i
            pos += 1
            if pos == 6:
                pos, n = 0, n + 1
        return r

    dic, enlarge, nbits = {0: 0, 1: 1, 2: 2}, 4, 3
    first = read(2)
    if first == 2:
        return ""
    w = chr(read(8 if first == 0 else 16))
    dic[3] = w
    out = [w]
    while n < len(vals):
        c = read(nbits)
        if c in (0, 1):
            dic[len(dic)] = chr(read(8 if c == 0 else 16))
            c = len(dic) - 1
            enlarge -= 1
            if enlarge == 0:
                enlarge, nbits = 1 << nbits, nbits + 1
        elif c == 2:
            break
        entry = dic[c] if c in dic else w + w[0]
        out.append(entry)
        dic[len(dic)] = w + entry[0]
        enlarge -= 1
        w = entry
        if enlarge == 0:
            enlarge, nbits = 1 << nbits, nbits + 1
    return "".join(out)


def signature(els):
    """Hash of what a person would change by editing: ids, kinds, text and box geometry. Text and arrow sizes are left out because the plugin re-measures them on save."""
    rows = []
    for e in els:
        if e.get("isDeleted"):
            continue
        r = [e["id"], e["type"], e.get("text") or e.get("name") or ""]
        if e["type"] not in ("text", "arrow", "line"):
            r += [round(e.get(k, 0)) for k in ("x", "y", "width", "height")]
        rows.append(r)
    return hashlib.sha256(json.dumps(sorted(rows), ensure_ascii=False).encode()).hexdigest()[:16]


GAPC, BANDGAP, PAD, GAP = 50, 160, 40, 4
INK, BG, STICKY = "#1e1e1e", "#ffffff", "#ffdf6b"
ROT = ((-.574, 1.43, .144), (.426, .43, .144), (.426, 1.43, -.856))
KEYS = {"top": ("direction", "frames", "nodes", "edges", "title", "palette", "ink", "background", "dark"), "frames": ("id", "label"),
        "nodes": ("id", "label", "shape", "color", "roughness", "strokeStyle", "frame", "icon", "group", "link"),
        "edges": ("from", "to", "head", "dashed", "label")}
B62 = string.digits + string.ascii_letters



def sha(s):
    return hashlib.sha1(s.encode()).hexdigest()


def eid(key, kind):
    n, out = int(sha(key + "|" + kind), 16), ""
    for _ in range(8):
        n, r = divmod(n, 62)
        out += B62[r]
    return out


def up20(v):
    return int(-(-v // 20) * 20)


def num(v):
    return int(v) if v == int(v) else round(v, 1)


def meas(t, fs=20):
    w = max(sum(fs if unicodedata.east_asian_width(c) in ("W", "F") else fs * 0.6 for c in ln) for ln in t.split("\n"))
    return int(w + 0.999), int(fs * 1.25 * (t.count("\n") + 1))


def mix(a, b, t):
    return "#" + "".join("%02x" % round(int(a[i:i + 2], 16) * (1 - t) + int(b[i:i + 2], 16) * t) for i in (1, 3, 5))


def light(c):
    v = [int(c[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join("%02x" % max(0, min(255, round((237.15 - sum(m * x for m, x in zip(r, v))) / .86))) for r in ROT)


def el(key, kind, typ, x, y, w, h, **k):
    s = sha(key + "|" + kind)
    d = dict(id=eid(key, kind), type=typ, x=num(x), y=num(y), width=num(w), height=num(h), angle=0,
             strokeColor=INK, backgroundColor="transparent", fillStyle="solid", strokeWidth=2,
             strokeStyle="solid", roughness=0, opacity=100, groupIds=[], frameId=None, roundness=None,
             seed=int(s[:8], 16), version=1, versionNonce=int(s[8:16], 16), isDeleted=False, boundElements=[],
             updated=1, link=None, locked=False)
    d.update(k)
    return d


def txt(key, kind, x, y, t, fs, **k):
    w, h = meas(t, fs)
    d = dict(text=t, rawText=t, originalText=t, fontSize=fs, fontFamily=2, textAlign="center",
             verticalAlign="middle", containerId=None, autoResize=True, lineHeight=1.25)
    d.update(k)
    return el(key, kind, "text", x, y, w, h, **d)


def colors(s):
    global INK, BG, STICKY
    dark, pal = bool(s.get("dark")), s.get("palette") or {}
    ink, bg = s.get("ink"), s.get("background") or ("#121212" if dark else BG)
    for c in [ink or INK, bg] + [c for v in pal.values() for c in (v if isinstance(v, list) and len(v) == 2 else [v])]:
        if not isinstance(c, str) or not re.fullmatch("#[0-9a-fA-F]{6}", c):
            raise ValueError("color is #rrggbb, a palette entry one color or [fill, stroke]: %r" % (c,))
    f = light if dark else str
    INK, BG = f(ink) if ink else INK, f(bg)
    PAL.update((k, tuple(map(f, v if isinstance(v, list) else (mix(v, bg, .75), v)))) for k, v in pal.items())
    STICKY = PAL["note"][0] if "note" in pal else STICKY


def parse(s):
    if not isinstance(s, dict):
        raise ValueError("spec must be an object")
    dr = s.get("direction") or "LR"
    if dr not in ("LR", "TB"):
        raise ValueError("direction must be LR or TB")
    frames, nodes, edges = s.get("frames") or [], s.get("nodes"), s.get("edges") or []
    if not nodes:
        raise ValueError("nodes required")
    colors(s)
    fids = [f["id"] for f in frames]
    ids = [n["id"] for n in nodes]
    if len(set(fids)) != len(fids) or len(set(ids)) != len(ids):
        raise ValueError("duplicate id")
    for f in frames:
        f.setdefault("label", f["id"])
    for n in nodes:
        n["label"] = n["label"]
        if not isinstance(n["label"], str) or not n["label"]:
            raise ValueError("label must be a non-empty string: %s" % n["id"])
        n["shape"] = n.get("shape") or "rectangle"
        if n["shape"] not in SHAPES:
            raise ValueError("unknown shape: %s" % n["shape"])
        if n.get("color") and n["color"] not in PAL:
            raise ValueError("unknown color: %s" % n["color"])
        if n.get("roughness", 0) not in (0, 1, 2) or n.get("strokeStyle", "solid") not in ("solid", "dashed", "dotted"):
            raise ValueError("roughness is 0, 1 or 2; strokeStyle is solid, dashed or dotted: %s" % n["id"])
        if n.get("frame") and n["frame"] not in fids:
            raise ValueError("unknown frame: %s" % n["frame"])
    for e in edges:
        if e["from"] not in ids or e["to"] not in ids:
            raise ValueError("edge to unknown node: %s -> %s" % (e["from"], e["to"]))
        if e["from"] == e["to"]:
            raise ValueError("self-loop: %s" % e["from"])
        if e.get("head", "arrow") not in HEADS:
            raise ValueError("head is one of %s" % ", ".join(HEADS))
    return dr, frames, nodes, edges


def unknown(spec):
    w = ["unknown key %r at top level ignored" % k for k in spec if k not in KEYS["top"]]
    for part in ("frames", "nodes", "edges"):
        for i, x in enumerate(spec.get(part) or []):
            w += ["unknown key %r on %s %s ignored" % (k, part[:-1], x.get("id", i)) for k in x if k not in KEYS[part]]
    return w


def nsize(n):
    w, h = meas(n["label"])
    ic = bool(n.get("icon")) and n["shape"] != "text"
    sh = n["shape"]
    if sh == "text":
        pass
    elif sh in ("rectangle", "note"):
        w, h = max(160, w + 48), max(72, h + 32)
    elif sh == "ellipse":
        w, h = max(160, 1.5 * (w + 16)), max(80, 1.5 * (h + 16))
    else:
        w, h = max(180, 2 * (w + 16)), max(100, 2 * (h + 16))
    if ic:
        w += 56
    if sh != "text":
        w, h = up20(w), up20(h)
    return w, h


def layout_frames(dr, frames, nodes, edges):
    """Frames are columns (LR) or rows (TB) in declared order; nodes stack inside their frame."""
    LR = dr == "LR"
    cols = {f["id"]: i for i, f in enumerate(frames)}
    ncol = len(frames) + (1 if any(not n.get("frame") for n in nodes) else 0)
    col = {n["id"]: cols[n["frame"]] if n.get("frame") else len(frames) for n in nodes}
    V, members = {}, [[] for _ in range(ncol)]
    for n in nodes:
        w, h = nsize(n)
        V[n["id"]] = dict(l=col[n["id"]], b=col[n["id"]], ms=w if LR else h, cs=h if LR else w, node=n)
        members[col[n["id"]]].append(n["id"])
    pos = {k: i for m in members for i, k in enumerate(m)}
    colw = [up20(max([V[k]["ms"] for k in m], default=0)) for m in members]
    tall = [sum(V[k]["cs"] for k in m) + GAPC * max(len(m) - 1, 0) for m in members]
    top = max(tall, default=0)
    c = {}
    for m, t in zip(members, tall):
        y = round((top - t) / 2 / 20) * 20
        for k in m:
            c[k] = y + V[k]["cs"] / 2
            y += V[k]["cs"] + GAPC
    # classify edges and allocate lanes per gap (gap g lies right of column g)
    lanes, lab, ori = {}, {}, {}
    for i, e in enumerate(edges):
        a, b = col[e["from"]], col[e["to"]]
        lw = (meas(e["label"], 16)[0] + 20 if LR else 30) if e.get("label") else 0
        if a == b:
            if abs(pos[e["from"]] - pos[e["to"]]) > 1:
                lanes.setdefault(a, []).append(("e", i))
            continue
        s, d = (e["from"], e["to"]) if a < b else (e["to"], e["from"])
        ori[i] = (s, d)
        if e.get("label"):
            for g in range(col[s], col[d]):
                lab[g] = max(lab.get(g, 0), lw)
    # each end of an edge gets its own port on the node side and each edge its own lane,
    # so fan-outs and fan-ins never share a trunk
    outp, inp = {}, {}
    for side, tab in ((0, outp), (1, inp)):
        by = {}
        for i, (s, d) in ori.items():
            by.setdefault(s if side == 0 else d, []).append(i)
        for node, ix in by.items():
            far = lambda i: c[ori[i][1] if side == 0 else ori[i][0]]
            ix.sort(key=lambda i: (far(i), i))
            step = min(32, (V[node]["cs"] - 24) / max(len(ix) - 1, 1))
            for j, i in enumerate(ix):
                tab[i] = (j - (len(ix) - 1) / 2) * step
            ups = [i for i in ix if far(i) < c[node]]
            dns = [i for i in ix if far(i) >= c[node]][::-1]
            for i in ups + dns:
                if side == 0:
                    lanes.setdefault(col[ori[i][0]], []).append(("o", i))
                elif col[ori[i][1]] - col[ori[i][0]] > 1:
                    lanes.setdefault(col[ori[i][1]] - 1, []).append(("i", i))
    slots = {g: list(dict.fromkeys(v)) for g, v in lanes.items()}
    gap = [up20(2 * PAD + 60 + 2 * lab.get(g, 0) + 20 * len(slots.get(g, []))) for g in range(max(ncol - 1, 0) + 1)]
    m0 = [0]
    for g in range(ncol - 1):
        m0.append(m0[-1] + colw[g] + gap[g])
    mp = {k: m0[V[k]["l"]] + (colw[V[k]["l"]] - V[k]["ms"]) / 2 for k in V}
    cmin = min([c[k] - V[k]["cs"] / 2 for k in V], default=0)
    cmax = max([c[k] + V[k]["cs"] / 2 for k in V], default=0)

    def lx(g, key):
        return m0[g] + colw[g] + PAD + 20 + lab.get(g, 0) + 20 * slots[g].index(key)
    ntop = nbot = 0
    paths = []
    for i, e in enumerate(edges):
        u, v = e["from"], e["to"]
        a, b = col[u], col[v]
        rev = a > b
        s, d = (v, u) if rev else (u, v)
        if a == b:
            if abs(pos[u] - pos[v]) == 1:
                mc = mp[u] + V[u]["ms"] / 2
                up_ = c[u] < c[v]
                y0 = c[u] + (V[u]["cs"] / 2 + GAP) * (1 if up_ else -1)
                y1 = c[v] - (V[v]["cs"] / 2 + GAP) * (1 if up_ else -1)
                pts = [(mc, y0), (mc, y1)]
            else:
                x = lx(a, ("e", i))
                pts = [(mp[u] + V[u]["ms"] + GAP, c[u]), (x, c[u]), (x, c[v]), (mp[v] + V[v]["ms"] + GAP, c[v])]
            paths.append(pts)
            continue
        ys, yd = c[s] + outp[i], c[d] + inp[i]
        pts = [(mp[s] + V[s]["ms"] + GAP, ys), (lx(col[s], ("o", i)), ys)]
        if col[d] - col[s] > 1:
            if (ys + yd) / 2 < (cmin + cmax) / 2:
                y = cmin - PAD - 70 - 20 * ntop
                ntop += 1
            else:
                y = cmax + PAD + 40 + 20 * nbot
                nbot += 1
            pts += [(pts[-1][0], y), (lx(col[d] - 1, ("i", i)), y)]
            pts.append((pts[-1][0], yd))
        else:
            pts.append((pts[-1][0], yd))
        pts.append((mp[d] - GAP, yd))
        if rev:
            pts.reverse()
        q = [pts[0]]
        for p in pts[1:]:
            if p != q[-1]:
                q.append(p)
        paths.append(q)
    box = {}
    for k, v in V.items():
        x, y = (mp[k], c[k] - v["cs"] / 2) if LR else (c[k] - v["cs"] / 2, mp[k])
        box[k] = (x, y, v["ms"] if LR else v["cs"], v["cs"] if LR else v["ms"])
    if not LR:
        paths = [[(p[1], p[0]) for p in r] for r in paths]
    return V, box, paths, None, None


def layout(dr, frames, nodes, edges):
    if frames:
        return layout_frames(dr, frames, nodes, edges)
    LR = dr == "LR"
    fi = {f["id"]: i for i, f in enumerate(frames)}
    ids = [n["id"] for n in nodes]
    adj = {i: [] for i in ids}
    for e in edges:
        adj[e["from"]].append(e["to"])
    state, back = {}, set()

    def dfs(u):
        state[u] = 1
        for v in adj[u]:
            if state.get(v) == 1:
                back.add((u, v))
            elif v not in state:
                dfs(v)
        state[u] = 2
    for i in ids:
        if i not in state:
            dfs(i)
    revs = [(e["from"], e["to"]) in back for e in edges]
    ends = [(e["to"], e["from"]) if r else (e["from"], e["to"]) for e, r in zip(edges, revs)]
    preds = {i: [] for i in ids}
    for a, b in ends:
        preds[b].append(a)
    lay = {}

    def L(v):
        if v not in lay:
            lay[v] = max([L(p) + 1 for p in preds[v]], default=0)
        return lay[v]
    for i in ids:
        L(i)
    V = {}
    for n in nodes:
        w, h = nsize(n)
        V[n["id"]] = dict(l=lay[n["id"]], b=fi[n["frame"]] if n.get("frame") else len(frames),
                          ms=w if LR else h, cs=h if LR else w, node=n)
    chains = []
    for i, (a, b) in enumerate(ends):
        ch = [a]
        for l in range(lay[a] + 1, lay[b]):
            k = ("d", i, l)
            V[k] = dict(l=l, b=V[edges[i]["from"]]["b"], ms=20, cs=20, node=None)
            ch.append(k)
        chains.append(ch + [b])
    up = {k: [] for k in V}
    dn = {k: [] for k in V}
    for ch in chains:
        for a, b in zip(ch, ch[1:]):
            dn[a].append(b)
            up[b].append(a)
    nl = max(lay.values()) + 1
    lays = [sorted([k for k in V if V[k]["l"] == l], key=lambda k: V[k]["b"]) for l in range(nl)]
    for it in range(8):
        down = it % 2 == 0
        for l in (range(1, nl) if down else range(nl - 2, -1, -1)):
            pos = {k: i for i, k in enumerate(lays[l - 1] if down else lays[l + 1])}
            cur = {k: i for i, k in enumerate(lays[l])}
            nb = up if down else dn

            def key(k):
                ns = [pos[x] for x in nb[k]]
                return (V[k]["b"], sum(ns) / len(ns) if ns else cur[k])
            lays[l].sort(key=key)
    c = {}
    for l in lays:
        cur = {}
        for k in l:
            b = V[k]["b"]
            c[k] = cur.get(b, 0) + V[k]["cs"] / 2
            cur[b] = c[k] + V[k]["cs"] / 2 + GAPC
    bands = sorted({v["b"] for v in V.values()})

    def restack():
        end = None
        for b in bands:
            ks = [k for k in V if V[k]["b"] == b]
            lo = min(c[k] - V[k]["cs"] / 2 for k in ks)
            hi = max(c[k] + V[k]["cs"] / 2 for k in ks)
            s = -lo if end is None else end + BANDGAP - lo
            for k in ks:
                c[k] += s
            end = hi + s
    restack()
    for it in range(8):
        for l in (lays if it % 2 == 0 else lays[::-1]):
            for b in bands:
                ks = [k for k in l if V[k]["b"] == b]
                if not ks:
                    continue
                t = [sum(c[x] for x in up[k] + dn[k]) / len(up[k] + dn[k]) if up[k] + dn[k] else c[k] for k in ks]
                sep = [(V[x]["cs"] + V[y]["cs"]) / 2 + GAPC for x, y in zip(ks, ks[1:])]
                f, g = t[:], t[:]
                for i in range(1, len(f)):
                    f[i] = max(t[i], f[i - 1] + sep[i - 1])
                for i in range(len(g) - 2, -1, -1):
                    g[i] = min(t[i], g[i + 1] - sep[i])
                for i, k in enumerate(ks):
                    c[k] = (f[i] + g[i]) / 2
        restack()
    for k in c:
        c[k] = round((c[k] - V[k]["cs"] / 2) / 20) * 20 + V[k]["cs"] / 2
    oo, io = {}, {}
    for side, tab in ((0, oo), (1, io)):
        by = {}
        for i, ch in enumerate(chains):
            by.setdefault(ch[0] if side == 0 else ch[-1], []).append(i)
        for node, ix in by.items():
            ix.sort(key=lambda i: (c[chains[i][1] if side == 0 else chains[i][-2]], i))
            step = min(32, (V[node]["cs"] - 24) / max(len(ix) - 1, 1))
            for j, i in enumerate(ix):
                tab[i] = (j - (len(ix) - 1) / 2) * step
    off = {(i, j): (oo if j == 0 else io)[i] for i, ch in enumerate(chains) for j in (0, len(ch) - 1)}
    rows = [[c[k] + off.get((i, j), 0) for j, k in enumerate(ch)] for i, ch in enumerate(chains)]
    hops = {}
    for i, ch in enumerate(chains):
        for j in range(len(ch) - 1):
            r1, r2 = rows[i][j], rows[i][j + 1]
            if r1 != r2:
                hops.setdefault(V[ch[j]]["l"], []).append((min(r1, r2), max(r1, r2), i, j))
    trk, nt = {}, {}
    for g, hs in hops.items():
        fin = []
        for h in sorted(hs):
            for t in range(len(fin)):
                if fin[t] < h[0] - 12:
                    fin[t] = h[1]
                    break
            else:
                fin.append(h[1])
                t = len(fin) - 1
            trk[h[2], h[3]] = t
        nt[g] = len(fin)
    lab = {}
    for i, e in enumerate(edges):
        if e.get("label"):
            lw = meas(e["label"], 16)[0] + 20 if LR else 30
            for j in range(len(chains[i]) - 1):
                g = V[chains[i][j]]["l"]
                lab[g] = max(lab.get(g, 0), lw)
    colw = [up20(max(V[k]["ms"] for k in l)) for l in lays]
    gap = [up20(max(100, 80 + 20 * nt.get(g, 0)) + 2 * lab.get(g, 0)) for g in range(nl - 1)]
    m0 = [0]
    for g in range(nl - 1):
        m0.append(m0[-1] + colw[g] + gap[g])
    mp = {k: m0[V[k]["l"]] + round((colw[V[k]["l"]] - V[k]["ms"]) / 2 / 20) * 20 for k in V}
    box = {}
    for k, v in V.items():
        x, y = (mp[k], c[k] - v["cs"] / 2) if LR else (c[k] - v["cs"] / 2, mp[k])
        box[k] = (x, y, v["ms"] if LR else v["cs"], v["cs"] if LR else v["ms"])
    paths = []
    for i, ch in enumerate(chains):
        pts = [(mp[ch[0]] + V[ch[0]]["ms"] + GAP, rows[i][0])]
        for j in range(len(ch) - 1):
            g = V[ch[j]]["l"]
            gs = m0[g] + colw[g]
            n = nt.get(g, 0)
            xg = gs + gap[g] / 2 + (trk[i, j] - (n - 1) / 2) * 20 if (i, j) in trk else gs + gap[g] / 2
            pts += [(xg, rows[i][j]), (xg, rows[i][j + 1])]
        pts.append((mp[ch[-1]] - GAP, rows[i][-1]))
        if revs[i]:
            pts.reverse()
        q = [pts[0]]
        for p in pts[1:]:
            if p != q[-1]:
                q.append(p)
        r = [q[0]]
        for j in range(1, len(q) - 1):
            if not ((r[-1][0] == q[j][0] == q[j + 1][0]) or (r[-1][1] == q[j][1] == q[j + 1][1])):
                r.append(q[j])
        r.append(q[-1])
        paths.append([(p if LR else (p[1], p[0])) for p in r])
    return V, box, paths, chains, revs


def hit(a, b):
    return int(a[0] < b[0] + b[2] and b[0] < a[0] + a[2] and a[1] < b[1] + b[3] and b[1] < a[1] + a[3])


def seghit(r, p, q):
    return int(min(p[0], q[0]) < r[0] + r[2] and max(p[0], q[0]) > r[0] and min(p[1], q[1]) < r[1] + r[3] and max(p[1], q[1]) > r[1])


def anchor(p, j):
    a, b = p[j], p[j + 1]
    at = lambda f: (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f)
    d = (j + 1) - (len(p) - 1 - j)
    nb, na = max(-d, 0), max(d, 0)
    return p[:j + 1] + [at(.5 * i / (nb + 1)) for i in range(1, nb + 1)] + [at(.5)] + \
        [at(.5 + .5 * i / (na + 1)) for i in range(1, na + 1)] + p[j + 1:]


def build(spec):
    dr, frames, nodes, edges = parse(spec)
    V, box, paths, chains, revs = layout(dr, frames, nodes, edges)
    fel, els, texts, files, nb = {}, [], [], {}, {}
    fmem = {f["id"]: [] for f in frames}
    for k, v in V.items():
        n = v["node"]
        if n is not None and n.get("frame"):
            fmem[n["frame"]].append(box[k])
    for f in frames:
        if fmem[f["id"]]:
            x0, y0 = min(b[0] for b in fmem[f["id"]]) - PAD, min(b[1] for b in fmem[f["id"]]) - PAD - 30
            x1, y1 = max(b[0] + b[2] for b in fmem[f["id"]]) + PAD, max(b[1] + b[3] for b in fmem[f["id"]]) + PAD
            fel[f["id"]] = el(f["id"], "frame", "frame", x0, y0, x1 - x0, y1 - y0, name=f["label"], strokeColor="#bbbbbb")
    els += list(fel.values())
    nodeel, nfr = {}, {}
    for n in nodes:
        k, (x, y, w, h) = n["id"], box[n["id"]]
        fr = fel[n["frame"]]["id"] if n.get("frame") in fel else None
        nfr[k] = fr
        bg, st = PAL[n["color"]] if n.get("color") else ((STICKY if n["shape"] == "note" else "transparent"), INK)
        rs = dict(roughness=n.get("roughness", 0), strokeStyle=n.get("strokeStyle", "solid"))
        gids = [eid(k, "icongroup")] if n.get("icon") and n["shape"] != "text" else []
        if n.get("group"):
            gids.append(eid(n["group"], "group"))
        tw, th = meas(n["label"])
        if n["shape"] == "text":
            b = txt(k, "box", x, y, n["label"], 20, verticalAlign="top", strokeColor=st, groupIds=gids, frameId=fr, link=n.get("link"), **rs)
            nodeel[k] = b
            els.append(b)
            texts.append(b)
            continue
        ic = bool(n.get("icon"))
        start = x + (w - (54 + tw)) / 2 if ic else x
        t = txt(k, "text", start + 54 if ic else x + (w - tw) / 2, y + (h - th) / 2, n["label"], 20,
                textAlign="left" if ic else "center", groupIds=gids, frameId=fr, containerId=eid(k, "box"))
        b = el(k, "box", "stickynote" if n["shape"] == "note" else n["shape"], x, y, w, h, strokeColor=st, backgroundColor=bg,
               groupIds=gids, frameId=fr, link=n.get("link"), roundness={"type": 3} if n["shape"] == "rectangle" else None,
               boundElements=[{"type": "text", "id": t["id"]}], **rs)
        nodeel[k] = b
        els += [b, t]
        texts.append(t)
        if ic:
            fid = sha(n["icon"])
            files[fid] = n["icon"]
            els.append(el(k, "image", "image", start, y + (h - 40) / 2, 40, 40, groupIds=gids,
                          frameId=fr, fileId=fid, scale=[1, 1], crop=None, status="saved"))
    arrows, taken, box0 = [], [], [box[n["id"]] for n in nodes]
    for i, e in enumerate(edges):
        p, key = paths[i], "%s>%s#%d" % (e["from"], e["to"], i)
        if e.get("label"):
            lw, lh = meas(e["label"], 16)
            best = None
            hs = [j for j in range(len(p) - 1) if p[j][1] == p[j + 1][1]]
            for j in hs or range(len(p) - 1):
                cx, cy = (p[j][0] + p[j + 1][0]) / 2, (p[j][1] + p[j + 1][1]) / 2
                rc = (cx - lw / 2, cy - lh / 2, lw, lh)
                sc = sum(hit(rc, b) for b in box0) + \
                    sum(seghit(rc, a, b) for m, pm in enumerate(paths) if m != i for a, b in zip(pm, pm[1:])) + \
                    sum(hit(rc, t) for t in taken)
                ln = abs(p[j + 1][0] - p[j][0]) + abs(p[j + 1][1] - p[j][1])
                if best is None or (sc, -ln) < best[0]:
                    best = ((sc, -ln), j, rc)
            _, j, rc = best
            taken.append(rc)
            p = anchor(p, j)
        xs, ys = [q[0] for q in p], [q[1] for q in p]
        a, bb = nodeel[e["from"]], nodeel[e["to"]]
        fr = nfr[e["from"]] if nfr[e["from"]] == nfr[e["to"]] else None
        ar = el(key, "arrow", "arrow", p[0][0], p[0][1], max(xs) - min(xs), max(ys) - min(ys), frameId=fr,
                strokeStyle="dashed" if e.get("dashed") else "solid", points=[[num(q[0] - p[0][0]), num(q[1] - p[0][1])] for q in p],
                startArrowhead=None, endArrowhead=HEADS[e.get("head", "arrow")],
                startBinding=dict(elementId=a["id"], focus=0, gap=GAP), endBinding=dict(elementId=bb["id"], focus=0, gap=GAP))
        a["boundElements"].append({"type": "arrow", "id": ar["id"]})
        bb["boundElements"].append({"type": "arrow", "id": ar["id"]})
        arrows.append(ar)
        if e.get("label"):
            t = txt(key, "label", rc[0], rc[1], e["label"], 16, containerId=ar["id"], frameId=fr)
            ar["boundElements"].append({"type": "text", "id": t["id"]})
            arrows.append(t)
            texts.append(t)
    els += arrows
    if spec.get("title"):
        x0, y0 = min(e["x"] for e in els), min(e["y"] for e in els)
        t = txt("title", "text", x0, y0 - 70, spec["title"], 28, textAlign="left", verticalAlign="top")
        els.append(t)
        texts.insert(0, t)
    return els, texts, files, {n["id"]: box[n["id"]] for n in nodes}, nodeel


def check(els, nbox, nodeel, edges):
    warns, ids = [], [e["id"] for e in els]
    if any(not re.fullmatch(r"[A-Za-z0-9]{8}", i) for i in ids) or len(set(ids)) != len(ids):
        raise ValueError("check 3: ids must be unique 8-char alphanumerics")
    by = {e["id"]: e for e in els}
    for e in els:
        for r in e["boundElements"]:
            o = by.get(r["id"])
            if o is None or (r["type"] == "text" and o.get("containerId") != e["id"]) or \
               (r["type"] == "arrow" and e["id"] not in (o["startBinding"]["elementId"], o["endBinding"]["elementId"])):
                raise ValueError("check 3: unmirrored binding on %s" % e["id"])
        if e["type"] == "arrow":
            for s in ("startBinding", "endBinding"):
                if {"type": "arrow", "id": e["id"]} not in by[e[s]["elementId"]]["boundElements"]:
                    raise ValueError("check 3: arrow not mirrored on endpoint")
        if e["type"] == "text" and e["containerId"] and {"type": "text", "id": e["id"]} not in by[e["containerId"]]["boundElements"]:
            raise ValueError("check 3: text not mirrored on container")
    ks = list(nbox)
    for i, a in enumerate(ks):
        for b in ks[i + 1:]:
            A, B = nbox[a], nbox[b]
            if A[0] < B[0] + B[2] and B[0] < A[0] + A[2] and A[1] < B[1] + B[3] and B[1] < A[1] + A[3]:
                raise ValueError("check 1: boxes overlap: %s, %s" % (a, b))
    segs, owner = [], []
    for e in els:
        if e["type"] != "arrow":
            continue
        pts = [(e["x"] + q[0], e["y"] + q[1]) for q in e["points"]]
        sg = list(zip(pts, pts[1:]))
        ends = {e["startBinding"]["elementId"], e["endBinding"]["elementId"]}
        for k, b in nbox.items():
            if nodeel[k]["id"] in ends:
                continue
            for (p, q) in sg:
                if min(p[0], q[0]) < b[0] + b[2] and max(p[0], q[0]) > b[0] and min(p[1], q[1]) < b[1] + b[3] and max(p[1], q[1]) > b[1]:
                    raise ValueError("check 2: arrow %s crosses box %s" % (e["id"], k))
        segs.append(sg)
        owner.append(e["id"])
    for f in els:
        if f["type"] == "frame":
            tr = (f["x"], f["y"] - 26, meas(f["name"], 16)[0] + 8, 26)
            for sg, o in zip(segs, owner):
                if any(seghit(tr, p, q) for p, q in sg):
                    warns.append("arrow %s crosses the title of frame %r" % (o, f["name"]))
    cr = 0
    for i, A in enumerate(segs):
        for B in segs[i + 1:]:
            for p, q in A:
                for r, s in B:
                    for (h0, h1), (v0, v1) in (((p, q), (r, s)), ((r, s), (p, q))):
                        if h0[1] == h1[1] and v0[0] == v1[0] and min(h0[0], h1[0]) < v0[0] < max(h0[0], h1[0]) and min(v0[1], v1[1]) < h0[1] < max(v0[1], v1[1]):
                            cr += 1
    if cr:
        warns.append("%d arrow crossings: the layout needs looking at" % cr)
    lb = [e for e in els if e["type"] == "text" and e["containerId"] and by[e["containerId"]]["type"] == "arrow"]
    for i, a in enumerate(lb):
        r = (a["x"], a["y"], a["width"], a["height"])
        for k, b in list(nbox.items()) + [(o["id"], (o["x"], o["y"], o["width"], o["height"])) for o in lb[i + 1:]]:
            if hit(r, b):
                warns.append("label %r overlaps %s" % (a["text"], k))
        for sg, o in zip(segs, owner):
            if o != a["containerId"] and any(seghit(r, p, q) for p, q in sg):
                warns.append("label %r overlaps arrow %s" % (a["text"], o))
    return cr, warns


def ours(raw):
    """True for this script's own plain output, or for that file after the plugin re-saved it, while its content is unedited."""
    m = re.match(r"---\n(?:.*\n)*?draw-py: ([0-9a-f]{16})\n(?:.*\n)*?---\n", raw)
    if not m:
        return False
    try:
        plain = re.fullmatch(re.escape(head(m.group(1))) + r".*?%%\n## Drawing\n```json\n(.*)\n```\n%%\n", raw, re.S)
        if plain:
            d = json.loads(plain.group(1))
            return json.dumps(d, ensure_ascii=False, separators=(",", ":")) == plain.group(1) and signature(d["elements"]) == m.group(1)
        c = re.search(r"```compressed-json\n(.*?)\n```", raw, re.S)
        return bool(c) and signature(json.loads(lz_decode(c.group(1)))["elements"]) == m.group(1)
    except (ValueError, KeyError, TypeError, IndexError):
        return False


def main(argv):
    rep = "--replace" in argv
    force = "--force" in argv
    argv = [a for a in argv if a not in ("--replace", "--force")]
    if len(argv) not in (2, 3):
        print("usage: draw.py <spec.json|-> [<out.excalidraw.md> [--replace [--force]]]", file=sys.stderr)
        return 1
    try:
        spec = json.loads(sys.stdin.read() if argv[1] == "-" else open(argv[1], encoding="utf-8").read())
        if len(argv) == 2:
            colors(spec)
            print(json.dumps(dict(ink=INK, background=BG, palette=PAL)))
            return 0
        if os.path.islink(argv[2]):
            raise ValueError("refusing symlink: %s" % argv[2])
        if os.path.exists(argv[2]):
            if not rep:
                raise ValueError("output exists: %s (--replace redoes a file this script wrote)" % argv[2])
            if not force and not ours(open(argv[2], encoding="utf-8").read()):
                raise ValueError("not replacing %s: it is not this script's unedited output (a foreign drawing, or edited in Obsidian). Change it with the plugin's :apply instead of regenerating; --replace --force overwrites it" % argv[2])
        els, texts, files, nbox, nodeel = build(spec)
        cr, warns = check(els, nbox, nodeel, spec.get("edges") or [])
        warns += unknown(spec)
        sc = dict(type="excalidraw", version=2, source="https://github.com/zsviczian/obsidian-excalidraw-plugin", elements=els,
                  appState=dict(gridSize=None, viewBackgroundColor=BG, **({"theme": "dark"} if spec.get("dark") else {})), files={})
        out = head(signature(els)) + "\n\n".join("%s ^%s" % (t["text"], t["id"]) for t in texts) + "\n\n"
        if files:
            out += "## Embedded Files\n" + "\n".join("%s: %s" % kv for kv in files.items()) + "\n\n"
        out += "%%\n## Drawing\n```json\n" + json.dumps(sc, ensure_ascii=False, separators=(",", ":")) + "\n```\n%%\n"
        d = os.path.dirname(os.path.abspath(argv[2]))
        os.makedirs(d, exist_ok=True)
        st = os.stat(argv[2]) if rep and os.path.exists(argv[2]) else None
        tmp = os.path.join(d, ".draw-%s.tmp" % uuid.uuid4().hex)
        fd = os.open(tmp, os.O_CREAT | os.O_EXCL | os.O_WRONLY, st.st_mode & 0o777 if st else 0o666)
        try:
            if st:
                os.fchmod(fd, st.st_mode & 0o777)
                try:
                    os.fchown(fd, -1, st.st_gid)
                except PermissionError:
                    pass
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(out)
            raw = open(tmp, "rb").read()
            back = json.loads(raw.decode().split("```json\n")[1].split("\n```")[0])["elements"]
            if len(back) != len(els):
                raise ValueError("readback element count mismatch")
            if st:
                os.replace(tmp, argv[2])
            else:
                os.link(tmp, argv[2])
        except FileExistsError:
            raise ValueError("output exists: %s" % argv[2])
        finally:
            if os.path.exists(tmp):
                os.remove(tmp)
        print(json.dumps(dict(path=argv[2], sha256=hashlib.sha256(raw).hexdigest(), elements=len(els),
                              by_type=dict(Counter(e["type"] for e in els)), crossings=cr, warnings=warns), ensure_ascii=False))
        return 0
    except (ValueError, KeyError, TypeError, OSError) as e:
        print("error: %s: %s" % (type(e).__name__, e), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
