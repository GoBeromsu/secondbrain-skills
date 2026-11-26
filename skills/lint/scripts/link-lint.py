#!/usr/bin/env python3
import argparse
import os
import re
import sys
import unicodedata

from daily_notes import daily_notes_folder, planned_daily_note

BARE = re.compile(r"(?<![\w/\[<\"'=@])https?://[^\s<>\[\]()\"']+")
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


def walk(root, vault=None):
    """Files under `root`, relative to it; a symlink that leads outside `vault` (default `root`)
    is skipped."""
    top = os.path.realpath(vault or root)
    for d, dirs, files in os.walk(root):
        dirs[:] = sorted(x for x in dirs if x not in SKIP_DIRS)
        for f in sorted(files):
            full = os.path.join(d, f)
            real = os.path.realpath(full)
            if real == top or real.startswith(top + os.sep):
                yield os.path.relpath(full, root)


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


def raw_original_span(text):
    fm = {key: values for key, _, values in frontmatter(text) or []}
    if fm.get("type") != ["raw-source"] and not (fm.get("source") and "raw" in fm.get("tags", [])):
        return []
    headings = [b for b in blocks(text, block_spans(text)) if b[0] == "heading"]
    start = next((b[4] for b in headings if b[3] == "## Original Content"), None)
    if start is None:
        return []
    # Verbatim Markdown can contain any heading. Legacy Raws without the marker
    # have no unambiguous authored boundary.
    stop = len(text)
    for marker in re.finditer(r"^<!-- end-original-content -->[ \t]*$", text[start:], re.M):
        stop = start + marker.start()
    return [(start, stop)]


def find(text, names, paths, daily_folder=None):
    out = []
    sp = protected(text) + raw_original_span(text)
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
        daily = not m.group(1) and planned_daily_note(m.group(2), daily_folder)
        if m.start() != planned and not daily and not resolves(target, names, paths):
            out.append(("BROKEN", m.start(), m.group(0)))
    return sorted(out, key=lambda r: (r[1], r[0]))


# Policy checks (`--checks policy`): the fallback for scripts/obsidian-lint.py when Obsidian is not
# running. Same rules, same report lines; keep the two in step (evals/lint/run.py checks both).
KEY = re.compile(r"^([^\s#:\-][^:]*?):(?:[ \t]+(.*?))?[ \t]*$")
ITEM = re.compile(r"^[ \t]*-(?:[ \t]+(.*?))?[ \t]*$")
QUOTED = re.compile(r"""^('(?:[^']|'')*'|"(?:[^"\\]|\\.)*")(?:[ \t]+#.*)?$""")
FLOW = re.compile(r"^\[(.*)\](?:[ \t]+#.*)?$")
PLAIN_URL = re.compile(r"^https?://[^\s<>\[\]()]+$", re.I)
URL_HOST = re.compile(r"^https?://(?:[^/?#\s@]+@)?([^/?#\s@:]+)(?::[0-9]+)?(?:[/?#]|$)", re.I)
ANY_URL = re.compile(r"https?://", re.I)
LEGACY_KEYS = {"youtube", "x"}
AUTO_ZONES = {"Wiki", "From Sources"}
NAME_SKIP_KEYS = {"aliases", "tags"}
# A name must stand alone: no letter, digit or Hangul around it, except Korean particles after it
# (`Anthropic은`, `서울역에서는` match; `오디` inside `오디오` and `Lumen에게2` do not).
WORD = "A-Za-z0-9_가-힣"
PARTICLES = ("에서는|에게는|으로는|에서도|에게도|으로도|까지는|부터는|에서|에게|으로|이랑|이나|처럼|보다|까지|부터|"
             "에는|에도|와는|과는|로는|은|는|이|가|을|를|의|에|와|과|로|도|만|랑|나|께")
LIST_ITEM = re.compile(r"^ {0,3}(?:[-*+]|\d+[.)])(?:[ \t]|$)")
ATX = re.compile(r"^ {0,3}(#{1,6})(?:[ \t]+(.*?))?(?:[ \t]+#+)?[ \t]*$")
SETEXT = re.compile(r"^ {0,3}(=+|-+)[ \t]*$")
RULE_LINE = re.compile(r"^ {0,3}([-*_])(?:[ \t]*\1){2,}[ \t]*$")
OBS_COMMENT = re.compile(r"%%.*?%%", re.S)
BLOCK_START = re.compile(r"^ {0,3}(?:#{1,6}(?:[ \t]|$)|>|[-*+][ \t]|\d+[.)][ \t]|\||```|~~~)")
YAML_ESCAPE = re.compile(r"\\(?:x[0-9A-Fa-f]{2}|u[0-9A-Fa-f]{4}|U[0-9A-Fa-f]{8}|.)")
YAML_KEY_ESCAPES = {"n": "\n", "t": "\t", '"': '"', "\\": "\\", "/": "/", "0": "\0", " ": " "}
YAML_SIMPLE_ESCAPES = {
    **YAML_KEY_ESCAPES,
    "a": "\a", "b": "\b", "\t": "\t", "v": "\v", "f": "\f", "r": "\r", "e": "\x1b",
    "N": "\x85", "_": "\xa0", "L": "\u2028", "P": "\u2029",
}


def decode_yaml_escape(match):
    token = match[0][1:]
    if len(token) > 1:
        codepoint = int(token[1:], 16)
        if codepoint <= 0x10FFFF and not 0xD800 <= codepoint <= 0xDFFF:
            return chr(codepoint)
    return YAML_SIMPLE_ESCAPES.get(token, match[0])


def unquote(v, *, key=False):
    """A YAML scalar as a string: quotes removed, trailing comment dropped."""
    v = v.strip()
    q = QUOTED.match(v)
    if q:
        s = q.group(1)
        if s[0] == '"':
            if key:
                return re.sub(r"\\(.)", lambda e: YAML_KEY_ESCAPES.get(e[1], e[0]), s[1:-1])
            return YAML_ESCAPE.sub(decode_yaml_escape, s[1:-1])
        return s[1:-1].replace("''", "'")
    return re.sub(r"(?:^|[ \t]+)#.*$", "", v)


def bad_scalar(v):
    """A scalar YAML rejects: an opened quote that does not close cleanly, or an unclosed `[`."""
    v = v.strip()
    if v[:1] in ("'", '"'):
        return not QUOTED.match(v)
    if v[:1] in ("[", "{"):
        return not balanced(strip_comment(v))
    return False


def balanced(v):
    """True when a flow collection closes every bracket it opens, outside quotes, and ends there."""
    stack, q, skip = [], None, False
    for i, c in enumerate(v):
        if skip:
            skip = False
        elif q:
            if q == '"' and c == "\\":
                skip = True
            elif c == q:
                q = None
        elif c in "\"'":
            q = c
        elif c in "[{":
            stack.append("]" if c == "[" else "}")
        elif c in "]}":
            if not stack or stack.pop() != c:
                return False
            if not stack:
                return not v[i + 1:].strip()
    return False


def split_flow(v):
    out, cur, q = [], "", None
    for c in v:
        if q:
            cur += c
            if c == q:
                q = None
        elif c in "\"'":
            q = c
            cur += c
        elif c == ",":
            out.append(cur)
            cur = ""
        else:
            cur += c
    out.append(cur)
    return [unquote(x) for x in out if x.strip()]


def strip_comment(line):
    """`line` without a YAML comment: `#` at the start or after whitespace, outside quotes."""
    q, skip = None, False
    for i, c in enumerate(line):
        if skip:
            skip = False
        elif q:
            if q == '"' and c == "\\":
                skip = True
            elif c == q:
                q = None
        elif c in "\"'" and (i == 0 or line[i - 1] in " \t[,:-"):
            q = c
        elif c == "#" and (i == 0 or line[i - 1] in " \t"):
            return line[:i].rstrip()
    return line


def scalar_values(rest):
    f = FLOW.match(rest)
    if f:
        return split_flow(f.group(1))
    if rest[:1] == "{":
        return []
    return [unquote(rest)]


def frontmatter(text):
    """Top-level keys in file order: [(key, line, [string values])]. Nested maps are not read.
    None when the block is YAML that Obsidian rejects and reads as no properties at all: a repeated
    key, a broken quoted scalar or an unclosed flow sequence."""
    m = FRONT.match(text)
    if not m:
        return []
    raw = text[:m.end()].split("\n")[1:-1]
    lines, j = [], 0
    while j < len(raw):
        # Join a quoted scalar or flow collection that YAML folds over several lines. A `#` is a
        # comment only outside quotes, so a quoted continuation line keeps it.
        start, line = j, strip_comment(raw[j])
        k, it = KEY.match(line), ITEM.match(line)
        val = ((k.group(2) if k else it.group(1) if it else "") or "").strip()
        while val[:1] in ("'", '"', "[", "{") and bad_scalar(val) and j + 1 < len(raw) and raw[j + 1][:1] in (" ", "\t"):
            j += 1
            more = raw[j].strip() if val[:1] in ("'", '"') else strip_comment(raw[j]).strip()
            line += " " + more
            val += " " + more
        lines.append((start + 2, line))
        j += 1
    keys, block = [], False
    for i, line in lines:
        if line.rstrip() == "---":
            break
        k = KEY.match(line)
        if k:
            rest = (k.group(2) or "").strip()
            block = rest[:1] in ("|", ">")
            if bad_scalar(rest) or bad_scalar(k.group(1)):
                return None
            keys.append((unquote(k.group(1), key=True), i, [] if not rest or block else scalar_values(rest)))
            continue
        if not keys:
            continue
        if block:
            if line.strip():
                vals = keys[-1][2]
                vals[:] = [((vals[0] + " ") if vals else "") + line.strip()]
            continue
        it = ITEM.match(line)
        if it and it.group(1):
            if bad_scalar(it.group(1)):
                return None
            keys[-1][2].extend(scalar_values(it.group(1).strip()))
    if len({k for k, _, _ in keys}) < len(keys):
        return None
    if not keys and any(x.strip() and x.rstrip() != "---" for _, x in lines):
        return None  # not a map, e.g. a bare list
    return keys


def contained(root, path):
    """True when `path`, symlinks resolved, is inside the vault `root`."""
    real, top = os.path.realpath(path), os.path.realpath(root)
    return real == top or real.startswith(top + os.sep)


def in_dirs(rel, dirs):
    return any(d == "." or rel == d or rel.startswith(d.rstrip("/") + "/") for d in dirs)


def is_entity(in_entity_folder, layers):
    return in_entity_folder or layers[:1] == ["entities"]


def index_entities(root, folders):
    """Index Entity titles and aliases using registered folders and a layer fallback."""
    out = {}
    for rel in sorted(nfc(r) for r in walk(root) if r.endswith(".md") and not r.endswith(".excalidraw.md")
                      and not any(part.startswith(".") for part in r.split(os.sep))):
        # Obsidian does not index dot folders, so neither does this.
        if not contained(root, os.path.join(root, rel)):
            continue
        with open(os.path.join(root, rel), encoding="utf-8", errors="replace") as f:
            head = f.read(65536)
        fm = {k: v for k, _, v in frontmatter(head) or []}
        if not is_entity(in_dirs(rel, folders), fm.get("layer", [])):
            continue
        for name in [os.path.basename(rel)[:-3]] + fm.get("aliases", []):
            name = nfc(name.strip())
            if name and not name.startswith("[[") and rel not in out.get(name, []):
                out.setdefault(name, []).append(rel)
    return out


def entity_pattern(entities):
    if not entities:
        return None
    alt = "|".join(re.escape(n) for n in sorted(entities, key=lambda n: (-len(n), n)))
    return re.compile(r"(?<![{w}])(?:{a})(?:(?![{w}])|(?=(?:{p})(?![{w}])))".format(w=WORD, a=alt, p=PARTICLES))


def entity_text(name, targets):
    links = " ".join("[[%s]]" % (t if len(targets) > 1 else os.path.basename(t))[:-3] for t in targets)
    return "%s -> %s%s" % (name, "ambiguous " if len(targets) > 1 else "", links)


def resolve_path(target, names):
    """Vault paths a wikilink target names, as Obsidian resolves it: by file name, or by path suffix
    when the target has a folder. A stale folder path resolves to nothing."""
    t = nfc(target.strip().strip("/"))
    base = os.path.basename(t)
    cands = names.get(base[:-3] if base.endswith(".md") else base, [])
    if "/" not in t:
        return cands
    return [p for p in cands if p in (t, t + ".md") or p.endswith("/" + t) or p.endswith("/" + t + ".md")]


def block_spans(text):
    """Frontmatter, fenced code and comments: where no Markdown block starts."""
    spans = []
    m = FRONT.match(text)
    if m:
        spans.append((0, m.end()))
    for rx in (FENCE, COMMENT, OBS_COMMENT):
        spans += [(x.start(), x.end()) for x in rx.finditer(text)]
    return spans


def indent_of(line):
    """Columns of leading whitespace, a tab counting as four."""
    n = 0
    for c in line:
        if c == " ":
            n += 1
        elif c == "\t":
            n += 4
        else:
            break
    return n


def blocks(text, spans):
    """Block structure outside block spans, CommonMark-style:
    [("heading", offset, title, first line text, end offset)], [("break", offset, line text)],
    [("quote", start, end)] for block quotes with their lazy continuation lines, and
    [("code", start, end)] for indented code (indented four past the enclosing list item)."""
    out, pos = [], 0
    para, quote = None, None  # para: [start offset, [line texts]]; quote: start offset
    blank, in_code, list_col, quote_para = True, False, None, False
    for line in text.split("\n"):
        end = pos + len(line)
        if inside(spans, pos, pos + max(len(line), 1)) or not line.strip():
            if quote is not None:
                out.append(("quote", quote, pos))
            para, quote, blank = None, None, True
            pos = end + 1
            continue
        lead = indent_of(line)
        if list_col is not None and blank and lead < list_col and not LIST_ITEM.match(line):
            list_col = None
        base = list_col or 0
        in_code = lead >= base + 4 and (blank or in_code) and quote is None and para is None
        item = LIST_ITEM.match(line.lstrip(" \t")) if not in_code else None
        is_quote = re.match(r"^ {0,3}>", line.lstrip(" \t") if list_col is not None else line)
        if in_code:
            out.append(("code", pos, end))
        elif is_quote or (quote is not None and quote_para and not BLOCK_START.match(line) and not RULE_LINE.match(line)):
            # A plain line after quoted paragraph text is its lazy continuation; nothing else is.
            if quote is None:
                quote = pos
            if is_quote:
                inner = re.sub(r"^[ \t]*>[ ]?", "", line)
                quote_para = bool(inner.strip()) and not BLOCK_START.match(inner) and not RULE_LINE.match(inner) \
                    and not SETEXT.match(inner)
            para = None
        else:
            if quote is not None:
                out.append(("quote", quote, pos))
                quote = None
            atx, setext, rule = ATX.match(line), SETEXT.match(line), RULE_LINE.match(line)
            if item and not rule:
                # Content starts after the marker and 1-4 spaces; with 5 or more, after one space.
                body = line.lstrip(" \t")
                marker = len(item.group(0).rstrip(" \t"))
                gap = len(body) - marker - len(body[marker:].lstrip(" "))
                list_col = lead + marker + (gap if 1 <= gap <= 4 else 1)
            if setext and para:
                out.append(("heading", para[0], " ".join(para[1]), para[1][0], end))
                para = None
            elif rule:
                out.append(("break", pos, line.strip()))
                para = None
            elif atx:
                out.append(("heading", pos, (atx.group(2) or "").strip(), line.strip(), end))
                para = None
            elif BLOCK_START.match(line):
                para = None
            elif para is None:
                para = [pos, [line.strip()]]
            else:
                para[1].append(line.strip())
        blank = False
        pos = end + 1
    if quote is not None:
        out.append(("quote", quote, len(text)))
    return out


def find_policy(rel, text, names, entities, pattern, wiki, lifecycle, entity_folders, book_types, product_types):
    out = []
    is_wiki = in_dirs(rel, wiki)
    keys = frontmatter(text)
    starts = [0] + [m.end() for m in re.finditer("\n", text)]

    def at(line):
        return starts[line - 1]

    if keys is None:
        out.append(("FM-INVALID", 0, "frontmatter does not parse"))
        keys = []
    for (k1, _, _), (k2, line, _) in zip(keys, keys[1:]):
        if k1.lower() > k2.lower():
            out.append(("FM-KEY-ORDER", at(line), "%s > %s" % (k1, k2)))
    fm = {k: (line, v) for k, line, v in keys}
    kind = (fm.get("type", (0, []))[1] or [""])[0]
    in_entity_folder = in_dirs(rel, entity_folders)
    is_product = kind in product_types and is_entity(in_entity_folder, fm.get("layer", (0, []))[1])
    for key, line, values in keys:
        if key in LEGACY_KEYS:
            out.append(("FM-LEGACY-KEY", at(line), key))
            continue
        if is_product and key == "url":
            for v in values or [""]:
                host = match[1] if (match := URL_HOST.match(v.strip())) else ""
                target = "github_url" if host.isascii() and host.lower() in ("github.com", "www.github.com") else "website_url"
                out.append(("FM-PRODUCT-URL", at(line), "%s <- url: %s" % (target, v)))
        for v in values:
            if key == "url" or key.endswith("_url"):
                if v.strip() and not PLAIN_URL.match(v.strip()):
                    out.append(("FM-URL-FORM", at(line), "%s: %s" % (key, v)))
            elif is_wiki and ANY_URL.search(v):
                out.append(("FM-URL-KEY", at(line), "%s: %s" % (key, v)))
    spans = block_spans(text) + raw_original_span(text)
    found = blocks(text, spans)
    headings = [b for b in found if b[0] == "heading"]
    if "status" in fm:
        reading_book = kind in book_types and in_entity_folder and any(
            title == "Reading Progress" and (match := ATX.match(line)) and match[1] == "##"
            for _, _, title, line, _ in headings)
        if kind not in lifecycle and not reading_book:
            line, values = fm["status"]
            out.append(("STATUS-NOT-LIFECYCLE", at(line), "status: %s" % ", ".join(values)))

    seen = set()
    for _, pos, title, line, _ in headings:
        if title in seen:
            out.append(("DUP-HEADING", pos, line))
        seen.add(title)
        if is_wiki and title in AUTO_ZONES:
            out.append(("AUTO-ZONE", pos, line))
    if not is_wiki:
        return out
    out += [("HR-IN-WIKI", b[1], b[2]) for b in found if b[0] == "break"]

    if pattern is None:
        return out
    own = nfc(rel)
    for key, line, values in keys:
        if key in NAME_SKIP_KEYS:
            continue
        for v in values:
            targets = [t for t in entities.get(nfc(v.strip()), []) if t != own]
            if targets:
                out.append(("ENTITY-UNLINKED", at(line), "%s: %s" % (key, entity_text(v, targets))))
    linked = set()
    front = FRONT.match(text)
    body_start = front.end() if front else 0
    code = spans + [(m.start(), m.end()) for m in INLINE.finditer(text)] + [(b[1], b[2]) for b in found if b[0] == "code"]
    for m in WIKILINK.finditer(text):
        if m.start() >= body_start and not inside(code, m.start(), m.end()):
            linked.update(resolve_path(m.group(2).split("|", 1)[0].split("#", 1)[0], names))
    masked = code + [(h[1], h[4]) for h in headings] + [(b[1], b[2]) for b in found if b[0] in ("quote", "code")]
    for rx in (WIKILINK, AUTOLINK, BARE):
        masked += [(m.start(), m.end()) for m in rx.finditer(text)]
    masked += [(m.end(2) if not m[1] and re.match(r"https?://", m[3].strip(), re.I) else m.start(), m.end())
               for m in MDLINK.finditer(text)]
    reported = set()
    for m in pattern.finditer(text):
        targets = [t for t in entities[nfc(m.group(0))] if t != own]
        key = tuple(targets)
        if m.start() < body_start or not targets or linked & set(targets) or key in reported or inside(masked, m.start(), m.end()):
            continue
        reported.add(key)
        out.append(("ENTITY-UNLINKED", m.start(), entity_text(m.group(0), targets)))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--vault", required=True)
    ap.add_argument("--scope", nargs="*", default=["."])
    ap.add_argument("--baseline")
    ap.add_argument("--checks", choices=("link", "policy", "all"), default="link")
    ap.add_argument("--wiki", action="append", default=[], help="wiki-role folder from the live policy (repeatable)")
    ap.add_argument("--entity-folder", action="append", default=[], help="entity-role folder from the live policy (repeatable)")
    ap.add_argument("--book-type", action="append", default=[], help="book Entity type from the live policy (repeatable)")
    ap.add_argument("--product-type", action="append", default=[], help="product Entity type from the live policy (repeatable)")
    ap.add_argument("--lifecycle", help="comma-separated `type` values the live policy names as lifecycle notes")
    a = ap.parse_args(argv)
    if a.checks != "link" and (not a.wiki or a.lifecycle is None):
        ap.error("--checks %s needs --wiki and --lifecycle from the vault's live policy" % a.checks)
    root = os.path.abspath(a.vault)
    names, paths = index_vault(root)
    daily_folder = daily_notes_folder(root) if a.checks != "policy" else None
    wiki = [nfc(w.strip("/")) for w in a.wiki]
    lifecycle = {t.strip() for t in (a.lifecycle or "").split(",") if t.strip()}
    folders = [nfc(d.strip("/")) for d in a.entity_folder]
    book_types = set(a.book_type)
    product_types = set(a.product_type)
    entities = index_entities(root, folders) if a.checks != "link" else {}
    pattern = entity_pattern(entities)
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
        if not contained(root, full):
            ap.error("scope %r is outside the vault" % s)
        if os.path.isfile(full):
            scoped.add(os.path.relpath(full, root))
        else:
            scoped.update(os.path.relpath(os.path.join(full, r), root) for r in walk(full, root))
    n = 0
    for rel in sorted(scoped, key=nfc):
        if not rel.endswith(".md") or rel.endswith(".excalidraw.md") or not contained(root, os.path.join(root, rel)):
            continue
        with open(os.path.join(root, rel), encoding="utf-8", errors="replace") as f:
            text = f.read()
        found = []
        if a.checks != "policy":
            found += find(text, names, paths, daily_folder)
        if a.checks != "link":
            found += find_policy(nfc(rel), text, names, entities, pattern, wiki, lifecycle, folders, book_types, product_types)
        rows = [(rule, text.count("\n", 0, pos) + 1, snip[:120].replace("\t", " ").replace("\n", " "), pos)
                for rule, pos, snip in found]
        # Link-only output keeps its historical order; policy output sorts like obsidian-lint.py.
        order = (lambda r: (r[3], r[0], r[2])) if a.checks == "link" else (lambda r: (r[1], r[0], r[2]))
        for rule, line, snip, _ in sorted(rows, key=order):
            if (rule, nfc(rel), snip) in known:
                continue
            sys.stdout.write("%s\t%s\t%d\t%s\n" % (rule, nfc(rel), line, snip))
            n += 1
    sys.stdout.write("# violations=%d\n" % n)
    return 1 if n else 0


if __name__ == "__main__":
    sys.exit(main())
