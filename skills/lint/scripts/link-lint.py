#!/usr/bin/env python3
import argparse
import os
import re
import sys
import unicodedata

BARE = re.compile(r"(?<![\w/(\[<\"'=@])https?://[^\s<>\[\]()\"']+")
AUTOLINK = re.compile(r"<https?://[^\s<>]+>")
EMAIL = re.compile(r"(?<![\w/@.:+-])[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}(?![\w@-])")
FILE_EXT = set("png jpg jpeg gif webp svg bmp heic avif pdf md css js json txt csv mp3 mp4 mov zip".split())
FLIPPED = re.compile(r"\(([^()\n\[\]]+)\)\[(https?://[^\]\s]+)\]")
MDLINK = re.compile(r"(!?)\[([^\]\n]*)\]\(([^)\n]*)\)")
WIKILINK = re.compile(r"(!?)\[\[([^\]\n]+)\]\]")
DEEP = re.compile(r"obsidian://[^\s)>\]\"']+")
REFDEF = re.compile(r"^[ \t]{0,3}\[[^\]\n]+\]:[ \t]*\S", re.M)
FENCE = re.compile(r"^[ \t]{0,3}(`{3,}|~{3,})[^\n]*\n.*?(?:^[ \t]{0,3}\1[`~]*[ \t]*$|\Z)", re.M | re.S)
INLINE = re.compile(r"(`+)[^`\n]+?\1")
COMMENT = re.compile(r"<!--.*?-->", re.S)
FRONT = re.compile(r"\A---\n.*?\n---[ \t]*(?:\n|\Z)", re.S)
TRAIL = ".,;:!?'\"*"
SKIP_DIRS = {".git", ".obsidian", ".trash", "node_modules"}


def nfc(s):
    return unicodedata.normalize("NFC", s)


def protected(text):
    spans = []
    m = FRONT.match(text)
    if m:
        spans.append((0, m.end()))
    for rx in (FENCE, COMMENT, INLINE):
        spans += [(x.start(), x.end()) for x in rx.finditer(text)]
    return sorted(spans)


def inside(spans, s, e):
    return any(a < e and b > s for a, b in spans)


def strip_trailing(u):
    tail = ""
    while u:
        c = u[-1]
        if c in TRAIL or (c == ")" and u.count(")") > u.count("(")):
            tail = c + tail
            u = u[:-1]
        else:
            break
    return u


def walk(root):
    for d, dirs, files in os.walk(root):
        dirs[:] = sorted(x for x in dirs if x not in SKIP_DIRS)
        for f in sorted(files):
            yield os.path.relpath(os.path.join(d, f), root)


def index_vault(root):
    names = {}
    paths = set()
    for rel in walk(root):
        rel = nfc(rel)
        paths.add(rel)
        base = os.path.basename(rel)
        key = base[:-3] if base.endswith(".md") else base
        names.setdefault(key, []).append(rel)
    return names, paths


def resolves(target, names, paths):
    t = nfc(target.strip().strip("/"))
    if not t:
        return True
    if t in paths or t + ".md" in paths:
        return True
    base = os.path.basename(t)
    if base not in names:
        return False
    if t == base:
        return True
    return any(p == t or p == t + ".md" or p.endswith("/" + t) or p.endswith("/" + t + ".md") for p in names[base])


def planned_term_link(text, spans):
    front = FRONT.match(text)
    if not front or not re.search(r"""^layer:[ \t]*(?:terms|'terms'|"terms")[ \t]*(?:#.*)?$""", front[0], re.M):
        return None
    headings = [m for m in re.finditer(r"^#{1,6}[ \t]+.*$", text, re.M)
                if not inside(spans, m.start(), m.end())]
    sections = [i for i, h in enumerate(headings) if h[0].rstrip() == "## Related Terms"]
    if len(sections) != 1:
        return None
    i = sections[0]
    start = headings[i].end()
    end = headings[i + 1].start() if i + 1 < len(headings) else len(text)
    bullets = [m for m in re.finditer(r"^[-*+][ \t]+", text[start:end], re.M)
               if not inside(spans, start + m.start(), start + m.end())]
    if not bullets:
        return None
    pos = start + bullets[-1].end()
    item = re.match(r"\[\[([^\[\]|#/\n]+)\]\][ \t]*\n[ \t]+[-*+][ \t]+\S", text[pos:end])
    if item and item[1].strip():
        return pos
    return None


def find(text, names, paths):
    out = []
    sp = protected(text)
    planned = planned_term_link(text, sp)
    mdspans = [(m.start(), m.end()) for m in MDLINK.finditer(text)]
    wlspans = [(m.start(), m.end()) for m in WIKILINK.finditer(text)]
    ex = mdspans + wlspans + [(m.start(), m.end()) for m in AUTOLINK.finditer(text)] + [(m.start(), m.end()) for m in REFDEF.finditer(text)]

    for m in BARE.finditer(text):
        if inside(sp, m.start(), m.end()) or inside(ex, m.start(), m.end()):
            continue
        out.append(("BARE-URL", m.start(), strip_trailing(m.group(0))))
    for m in AUTOLINK.finditer(text):
        if not inside(sp, m.start(), m.end()):
            out.append(("AUTOLINK", m.start(), m.group(0)))
    bare = [(m.start(), m.end()) for m in BARE.finditer(text)]
    for m in EMAIL.finditer(text):
        if inside(sp, m.start(), m.end()) or inside(ex, m.start(), m.end()) or inside(bare, m.start(), m.end()):
            continue
        if m.group(0).rsplit(".", 1)[-1].lower() in FILE_EXT:
            continue
        out.append(("EMAIL", m.start(), m.group(0)))
    for m in FLIPPED.finditer(text):
        if not inside(sp, m.start(), m.end()):
            out.append(("FLIPPED", m.start(), m.group(0)))
    for m in DEEP.finditer(text):
        if not inside(sp, m.start(), m.end()):
            out.append(("DEEPLINK", m.start(), m.group(0)))

    for m in MDLINK.finditer(text):
        if inside(sp, m.start(), m.end()) or m.group(1) == "!":
            continue
        label, dest = m.group(2), m.group(3).strip()
        if not label.strip() or not dest or dest == "#":
            out.append(("EMPTY-LINK", m.start(), m.group(0)))
            continue
        if label != label.strip():
            out.append(("LABEL-SPACE", m.start(), m.group(0)))
        if re.match(r"(https?://|mailto:|tel:|obsidian://|#|data:)", dest, re.I):
            continue
        out.append(("MD-INTERNAL", m.start(), m.group(0)))

    for m in WIKILINK.finditer(text):
        if inside(sp, m.start(), m.end()):
            continue
        target = m.group(2).split("|", 1)[0].split("#", 1)[0]
        if not target.strip():
            continue
        if "/" in target.strip("/"):
            base = os.path.basename(target.strip("/"))
            key = base[:-3] if base.endswith(".md") else base
            if len(names.get(key, [])) == 1 and resolves(target, names, paths):
                out.append(("PATH-WIKILINK", m.start(), m.group(0)))
        if m.start() != planned and not resolves(target, names, paths):
            out.append(("BROKEN", m.start(), m.group(0)))
    return sorted(out, key=lambda r: (r[1], r[0]))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--vault", required=True)
    ap.add_argument("--scope", nargs="*", default=["."])
    ap.add_argument("--baseline")
    a = ap.parse_args(argv)
    root = os.path.abspath(a.vault)
    names, paths = index_vault(root)
    known = set()
    if a.baseline:
        with open(a.baseline, encoding="utf-8") as f:
            for line in f:
                p = line.rstrip("\n").split("\t")
                if len(p) == 4:
                    known.add((p[0], p[1], p[3]))
    scoped = set()
    for s in a.scope:
        full = os.path.normpath(os.path.join(root, s))
        if os.path.isfile(full):
            scoped.add(os.path.relpath(full, root))
        else:
            scoped.update(os.path.relpath(os.path.join(full, r), root) for r in walk(full))
    n = 0
    for rel in sorted(scoped):
        if not rel.endswith(".md") or rel.endswith(".excalidraw.md"):
            continue
        with open(os.path.join(root, rel), encoding="utf-8", errors="replace") as f:
            text = f.read()
        for rule, pos, snip in find(text, names, paths):
            snip = snip[:120].replace("\t", " ").replace("\n", " ")
            if (rule, nfc(rel), snip) in known:
                continue
            sys.stdout.write("%s\t%s\t%d\t%s\n" % (rule, nfc(rel), text.count("\n", 0, pos) + 1, snip))
            n += 1
    sys.stdout.write("# violations=%d\n" % n)
    return 1 if n else 0


if __name__ == "__main__":
    sys.exit(main())
