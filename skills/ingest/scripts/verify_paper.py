#!/usr/bin/env python3
"""Mechanical review of one twelve-axis paper analysis folder (ingest Paper Mode, P-7).

Usage: python3 verify_paper.py PAPER_FOLDER [--vault VAULT] [--raw RAW]

Exit 0: every mechanical check passed. This is not semantic verification.
Exit 1: one or more validation failures.
Exit 2: a prerequisite is missing or an input cannot be resolved.
Needs Python 3.9+ and PyYAML. Reads only the vault; writes nothing.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

PAPER_TYPES = (
    "quantitative", "qualitative", "theory-concept",
    "mixed-methods", "scale-development", "meta-analysis",
)
_SHARED = {10: "CONCLUSIONS", 12: "DISCUSSION / WRITING VALUE"}
_EMPIRICAL = {
    2: "PURPOSE AND GENERAL RATIONALE", 3: "FIT AND SPECIFIC RATIONALE",
    4: "PARTICIPANTS", 5: "CONTEXT", 6: "STEPS IN SEQUENCE", 7: "DATA",
    8: "ANALYSIS", 9: "RESULTS", 11: "CAUTIONS", **_SHARED,
}
STEP_NAMES = {
    "quantitative": _EMPIRICAL,
    "qualitative": _EMPIRICAL,
    "theory-concept": {
        2: "PURPOSE AND GENERAL RATIONALE", 3: "FIT AND SPECIFIC RATIONALE",
        4: "CORE CONSTRUCTS / KEY CONCEPTS", 5: "SCOPE CONDITIONS / INTELLECTUAL CONTEXT",
        6: "ARGUMENT IN SEQUENCE", 7: "BUILDING BLOCKS / EVIDENTIARY BASE",
        8: "CONCEPTUAL WORK DONE", 9: "MAIN OUTPUTS",
        11: "CAUTIONS / BOUNDARY CONDITIONS", **_SHARED,
    },
    "mixed-methods": {
        2: "PURPOSE AND GENERAL RATIONALE", 3: "FIT AND SPECIFIC RATIONALE",
        4: "PARTICIPANTS / DATA SOURCES FOR BOTH STRANDS", 5: "CONTEXT",
        6: "DESIGN IN SEQUENCE", 7: "DATA", 8: "ANALYSIS AND INTEGRATION",
        9: "RESULTS / META-INFERENCES", 11: "CAUTIONS", **_SHARED,
    },
    "scale-development": {
        2: "PURPOSE", 3: "FIT AND RATIONALE", 4: "SAMPLES / PARTICIPANTS ACROSS STUDIES",
        5: "CONTEXT OF USE", 6: "DEVELOPMENT PROCESS IN SEQUENCE", 7: "DATA / ITEMS",
        8: "ANALYSIS", 9: "RESULTS", 11: "CAUTIONS", **_SHARED,
    },
    "meta-analysis": {
        2: "PURPOSE AND REVIEW QUESTION", 3: "FIT AND RATIONALE", 4: "CORPUS / STUDY SET",
        5: "CONTEXT OF THE REVIEWED FIELD", 6: "REVIEW PROCESS IN SEQUENCE",
        7: "DATA EXTRACTED FROM STUDIES", 8: "ANALYSIS / SYNTHESIS", 9: "RESULTS",
        11: "CAUTIONS", **_SHARED,
    },
}
BODY_SECTIONS = ("쉬운 도입", "정밀 해설", "예시", "원문 근거", "개념 관계")
RELATIONS = "개념 관계"
NON_CONTENT_HEADINGS = {"metadata", "ingest notes", "original content"}

WIKILINK_RE = re.compile(r"!?\[\[([^\[\]\n]+?)\]\]")
HEADING_RE = re.compile(r"^(#{1,6})[ \t]+(.+?)(?:[ \t]+#+)?[ \t]*$")
CALLOUT_RE = re.compile(r"^[ \t]*>[ \t]*\[!([^\]\s]+)\][+-]?[ \t]*(.*?)[ \t]*$")
FENCE_RE = re.compile(r"^[ \t]{0,3}(`{3,}|~{3,})")
PLACEHOLDER_RE = re.compile(r"\{\{[^{}\n]*\}\}")
LOCATOR_RE = re.compile(r"\bpp?\.[ \t]*\d|\bpages?[ \t]+\d|§[ \t]*[^\s{}(),]")
FILE_STEP_RE = re.compile(r" - S(\d{2}) ")
NUM_PREFIX_RE = re.compile(r"^(\d+(?:\.\d+)*\.?\)?|[ivxlcdm]+[.)]|[a-z][.)])\s+")
SEPARATOR_CELL_RE = re.compile(r":?-{3,}:?")
THEMATIC_BREAK_RE = re.compile(r"^[ \t]{0,3}([-*_])([ \t]*\1){2,}[ \t]*$")

_TYPOGRAPHIC = str.maketrans({
    "\u2018": "'", "\u2019": "'", "\u201a": "'", "\u201b": "'", "\u2032": "'",
    "\u201c": '"', "\u201d": '"', "\u201e": '"', "\u201f": '"', "\u2033": '"',
    "\u00ab": '"', "\u00bb": '"',
    "\u2010": "-", "\u2011": "-", "\u2012": "-", "\u2013": "-", "\u2014": "-",
    "\u2015": "-", "\ufe58": "-", "\ufe63": "-", "\uff0d": "-",
    "\u2026": "...",
    "\u200b": None, "\u2060": None, "\ufeff": None, "\u00ad": None,
})
SIGN_CHARS = "-+\u2212\u00b1"


def norm_text(text: str) -> str:
    """NFC, typographic folding and whitespace collapse; signs and digits are kept."""
    folded = unicodedata.normalize("NFC", text).translate(_TYPOGRAPHIC)
    return " ".join(folded.split())


def fold_name(text: str) -> str:
    """Case and whitespace folding only (analysisStepName, section titles)."""
    return " ".join(unicodedata.normalize("NFC", text).split()).casefold()


def structural_lines(text: str) -> list[str]:
    """Lines with HTML comments and fenced code blanked, line count preserved."""
    text = re.sub(r"<!--.*?-->", lambda m: "\n" * m.group(0).count("\n"), text, flags=re.S)
    out: list[str] = []
    fence = None
    for line in text.splitlines():
        m = FENCE_RE.match(line)
        if fence:
            if m and m.group(1)[0] == fence[0] and len(m.group(1)) >= len(fence) \
                    and line.strip() == m.group(1):
                fence = None
            out.append("")
        elif m:
            fence = m.group(1)
            out.append("")
        else:
            out.append(line)
    return out


def headings(lines: list[str], max_level: int = 6) -> list[tuple[int, int, str]]:
    found = []
    for i, line in enumerate(lines):
        m = HEADING_RE.match(line)
        if m and len(m.group(1)) <= max_level:
            found.append((i, len(m.group(1)), m.group(2).strip()))
    return found


def h2_sections(lines: list[str]) -> list[tuple[str, list[str]]]:
    """(folded title, body lines) for every H2; a section ends at the next H1/H2."""
    hs = [(i, lvl, t) for i, lvl, t in headings(lines) if lvl <= 2]
    sections = []
    for k, (i, lvl, title) in enumerate(hs):
        if lvl != 2:
            continue
        end = hs[k + 1][0] if k + 1 < len(hs) else len(lines)
        sections.append((fold_name(title), lines[i + 1:end]))
    return sections


def callouts(lines: list[str]) -> list[tuple[int, str, str]]:
    found = []
    for i, line in enumerate(lines):
        m = CALLOUT_RE.match(line)
        if m:
            found.append((i, m.group(1).casefold(), m.group(2)))
    return found


def callout_body(lines: list[str], header: int) -> str:
    out = []
    for line in lines[header + 1:]:
        m = re.match(r"^[ \t]*>[ \t]?(.*)$", line)
        if not m or CALLOUT_RE.match(line):
            break
        out.append(m.group(1))
    return "\n".join(out)


def link_targets(text: str) -> list[str]:
    return [m.group(1) for m in WIKILINK_RE.finditer(text)]


def split_table_row(line: str) -> list[str] | None:
    s = line.strip()
    if not s.startswith("|"):
        return None
    s = s[1:]
    if s.endswith("|") and not s.endswith("\\|"):
        s = s[:-1]
    cells, buf, depth, i = [], [], 0, 0
    while i < len(s):
        if s.startswith("[[", i):
            depth += 1
            buf.append("[[")
            i += 2
        elif s.startswith("]]", i) and depth:
            depth -= 1
            buf.append("]]")
            i += 2
        elif s.startswith("\\|", i):
            buf.append("|")
            i += 2
        elif s[i] == "|" and depth == 0:
            cells.append("".join(buf).strip())
            buf = []
            i += 1
        else:
            buf.append(s[i])
            i += 1
    cells.append("".join(buf).strip())
    return cells


def table_rows(lines: list[str]) -> list[list[str]]:
    """Data rows of the Markdown tables in lines; each header row is dropped."""
    rows: list[list[str]] = []
    for line in lines:
        cells = split_table_row(line)
        if cells is None:
            continue
        if any(cells) and all(SEPARATOR_CELL_RE.fullmatch(c) for c in cells if c):
            if rows:
                rows.pop()
            continue
        rows.append(cells)
    return rows


def as_date(value) -> date | None:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        m = re.fullmatch(r"(\d{4}-\d{2}-\d{2})(?:[T ]\S.*)?", value.strip())
        if m:
            try:
                return date.fromisoformat(m.group(1))
            except ValueError:
                return None
    return None


def is_text_scalar(value) -> bool:
    return isinstance(value, (str, int, float)) and not isinstance(value, bool) \
        and bool(str(value).strip())


def file_step(path: Path) -> int | None:
    marks = FILE_STEP_RE.findall(path.stem)
    return int(marks[0]) if len(marks) == 1 else None


def excerpt(text: str, width: int = 90) -> str:
    return text if len(text) <= width else text[:width - 1] + "…"


class Report:
    def __init__(self) -> None:
        self.root: Path | None = None
        self.failures: list[str] = []
        self.blockers: list[str] = []
        self.unverified: list[str] = []
        self.omissions: list[str] = []

    def where(self, path: Path | None) -> str:
        if path is None:
            return "-"
        if self.root is not None:
            try:
                return path.relative_to(self.root).as_posix()
            except ValueError:
                pass
        return str(path)

    def fail(self, path: Path | None, msg: str) -> None:
        self.failures.append(f"{self.where(path)}: {msg}")

    def block(self, path: Path | None, msg: str) -> None:
        self.blockers.append(f"{self.where(path)}: {msg}")

    def not_verified(self, path: Path | None, msg: str) -> None:
        self.unverified.append(f"{self.where(path)}: {msg}")


@dataclass
class Note:
    path: Path
    fm: dict
    body: str
    text: str
    lines: list[str] = field(default_factory=list)


def unique_key_loader():
    class Loader(yaml.SafeLoader):
        pass

    def construct_mapping(loader, node, deep=False):
        seen = set()
        for key_node, _ in node.value:
            if key_node.tag == "tag:yaml.org,2002:merge":
                continue
            key = loader.construct_object(key_node, deep=True)
            try:
                duplicate = key in seen
            except TypeError:
                continue
            if duplicate:
                raise yaml.constructor.ConstructorError(
                    "while constructing a mapping", node.start_mark,
                    f"duplicate key {key!r}", key_node.start_mark)
            seen.add(key)
        return yaml.SafeLoader.construct_mapping(loader, node, deep=deep)

    Loader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, construct_mapping)
    return Loader


def load_note(path: Path, rep: Report, loader) -> Note | None:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        rep.fail(path, "file is not valid UTF-8")
        return None
    except OSError as exc:
        rep.block(path, f"cannot read file: {exc.strerror or exc}")
        return None
    text = text.removeprefix("\ufeff")
    lines = text.splitlines()
    if not lines or lines[0].rstrip() != "---":
        rep.fail(path, "no YAML frontmatter (first line must be ---)")
        return None
    end = next((i for i in range(1, len(lines)) if lines[i].rstrip() in ("---", "...")), None)
    if end is None:
        rep.fail(path, "unterminated YAML frontmatter")
        return None
    try:
        data = yaml.load("\n".join(lines[1:end]), Loader=loader)
    except yaml.YAMLError as exc:
        rep.fail(path, "frontmatter YAML error: " + " ".join(str(exc).split()))
        return None
    if not isinstance(data, dict):
        rep.fail(path, f"frontmatter is not a mapping (got {type(data).__name__})")
        return None
    body = "\n".join(lines[end + 1:])
    return Note(path, data, body, text, structural_lines(body))


@dataclass
class Resolved:
    path: Path | None
    error: str | None = None
    candidates: tuple[Path, ...] = ()


class Vault:
    """Wikilink resolution confined to one vault root; hidden folders are not indexed."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.by_rel: dict[str, list[Path]] = {}
        self.by_name: dict[str, list[Path]] = {}
        self.by_rel_fold: dict[str, list[Path]] = {}
        self.by_name_fold: dict[str, list[Path]] = {}
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if not d.startswith(".")]
            for name in filenames:
                if name.startswith("."):
                    continue
                path = Path(dirpath) / name
                rel = unicodedata.normalize("NFC", path.relative_to(root).as_posix())
                nfc_name = unicodedata.normalize("NFC", name)
                self.by_rel.setdefault(rel, []).append(path)
                self.by_name.setdefault(nfc_name, []).append(path)
                self.by_rel_fold.setdefault(rel.casefold(), []).append(path)
                self.by_name_fold.setdefault(nfc_name.casefold(), []).append(path)

    def resolve(self, link: str) -> Resolved:
        target = link.replace("\\|", "|").split("|", 1)[0].split("#", 1)[0]
        target = unicodedata.normalize("NFC", target).strip()
        if not target:
            return Resolved(None, "link has no note target")
        if target.startswith("/") or "\\" in target or re.match(r"^[A-Za-z]:", target):
            return Resolved(None, f"[[{target}]] is an absolute or non-portable path")
        parts = target.split("/")
        if any(p in ("", ".", "..") for p in parts):
            return Resolved(None, f"[[{target}]] escapes or is not a normalized vault path")
        exact, folded = (self.by_rel, self.by_rel_fold) if len(parts) > 1 \
            else (self.by_name, self.by_name_fold)
        keys = (target, target + ".md")
        hits = {p for k in keys for p in exact.get(k, [])}
        if not hits:
            hits = {p for k in keys for p in folded.get(k.casefold(), [])}
        if not hits:
            return Resolved(None, f"[[{target}]] does not resolve inside the vault")
        if len(hits) > 1:
            names = ", ".join(sorted(p.relative_to(self.root).as_posix() for p in hits))
            return Resolved(None, f"[[{target}]] is ambiguous ({names})", tuple(sorted(hits)))
        path = hits.pop()
        if not path.resolve().is_relative_to(self.root):
            return Resolved(None, f"[[{target}]] is a symlink pointing outside the vault")
        return Resolved(path)


def frontmatter_links(value) -> tuple[list[str], str | None]:
    items = value if isinstance(value, list) else [value]
    targets: list[str] = []
    for item in items:
        found = link_targets(item) if isinstance(item, str) else []
        if not found:
            return [], f"expected wikilink(s), got {item!r}"
        targets.extend(found)
    if not targets:
        return [], "is empty"
    return targets, None


@dataclass
class Raw:
    path: Path
    evidence: str
    leaves: list[str]


@dataclass
class Paper:
    vault: Vault
    rep: Report
    folder: Path
    hub: Note | None
    atoms: list[Note]
    paper_type: str | None = None
    citekey: str | None = None
    raw_paths: set[Path] = field(default_factory=set)
    raws: list[Raw] = field(default_factory=list)

    @property
    def atom_paths(self) -> set[Path]:
        return {a.path for a in self.atoms}

    @property
    def step_names(self) -> dict[int, str] | None:
        return STEP_NAMES.get(self.paper_type) if self.paper_type else None


def check_placeholders(note: Note, rep: Report) -> None:
    text = re.sub(r"<!--.*?-->", "", note.text, flags=re.S)
    slots = sorted(set(PLACEHOLDER_RE.findall(text)))
    if slots:
        rep.fail(note.path, "unfilled template slots: " + ", ".join(slots[:5])
                 + (" …" if len(slots) > 5 else ""))


def check_provenance(note: Note, rep: Report) -> None:
    created, modified = as_date(note.fm.get("date_created")), as_date(note.fm.get("date_modified"))
    if created is None:
        rep.fail(note.path, "date_created missing or not an ISO date")
    if modified is None:
        rep.fail(note.path, "date_modified missing or not an ISO date")
    if created and modified and modified < created:
        rep.fail(note.path, "date_modified is earlier than date_created")
    model = note.fm.get("model")
    if not (is_text_scalar(model) or (isinstance(model, list) and model
                                      and all(is_text_scalar(m) for m in model))):
        rep.fail(note.path, "model missing or empty (a model id, or a list when several contributed)")
    if not is_text_scalar(note.fm.get("effort")):
        rep.fail(note.path, "effort missing or empty")


def resolve_links(paper: Paper, note: Note, targets: list[str], what: str) -> list[Path]:
    found = []
    for target in targets:
        res = paper.vault.resolve(target)
        if res.path is None:
            paper.rep.fail(note.path, f"{what}: {res.error}")
        else:
            found.append(res.path)
    return found


def check_hub(paper: Paper, explicit_raw: Path | None, loader) -> None:
    hub, rep = paper.hub, paper.rep
    fm = hub.fm
    if fm.get("status") != "active":
        rep.fail(hub.path, f"hub status must be 'active' (got {fm.get('status')!r})")
    citekey = fm.get("citekey")
    if isinstance(citekey, str) and citekey.strip():
        paper.citekey = citekey
    else:
        rep.fail(hub.path, "citekey missing or empty")
    target = fm.get("targetManuscript")
    if not isinstance(target, str) or not target.strip():
        rep.fail(hub.path, "targetManuscript missing or empty")
    elif link_targets(target):
        resolve_links(paper, hub, link_targets(target), "targetManuscript")
    elif target.strip().casefold() != "none":
        rep.fail(hub.path, "targetManuscript must be 'none' or an RQ wikilink")
    paper_type = fm.get("paperType")
    if paper_type in STEP_NAMES:
        paper.paper_type = paper_type
    else:
        rep.block(hub.path, f"paperType {paper_type!r} is not one of: {', '.join(PAPER_TYPES)}")
    check_provenance(hub, rep)
    check_placeholders(hub, rep)
    for _, kind, title in callouts(hub.lines):
        if kind == "note" and fold_name(title) == "compile plan":
            rep.fail(hub.path, "temporary [!note] Compile Plan callout is still present")
    resolve_raws(paper, explicit_raw, loader)


def resolve_raws(paper: Paper, explicit_raw: Path | None, loader) -> None:
    hub, rep = paper.hub, paper.rep
    targets, err = frontmatter_links(hub.fm.get("source"))
    if err:
        rep.block(hub.path, f"source {err}; the Raw cannot be resolved")
    for target in targets:
        res = paper.vault.resolve(target)
        if res.path is None:
            rep.block(hub.path, f"source: {res.error}")
        else:
            paper.raw_paths.add(res.path)
    if explicit_raw is not None:
        if paper.raw_paths and explicit_raw not in paper.raw_paths:
            rep.fail(hub.path, f"hub source does not name --raw {rep.where(explicit_raw)}")
        paper.raw_paths.add(explicit_raw)
        evidence_paths = [explicit_raw]
    else:
        evidence_paths = sorted(paper.raw_paths)
    for path in evidence_paths:
        raw = load_raw(path, paper, loader)
        if raw is not None:
            paper.raws.append(raw)


def load_raw(path: Path, paper: Paper, loader) -> Raw | None:
    rep = paper.rep
    if path.suffix.casefold() != ".md":
        rep.block(path, "Raw source is not a Markdown note")
        return None
    note = load_note(path, rep, loader)
    if note is None:
        rep.block(path, "Raw note cannot be parsed; quotations and coverage cannot be checked")
        return None
    raw_cite = note.fm.get("citekey")
    if paper.citekey and raw_cite is not None and raw_cite != paper.citekey:
        rep.fail(path, f"Raw citekey {raw_cite!r} differs from hub citekey {paper.citekey!r}")
    body_lines = note.body.splitlines()
    starts = [i for i, l in enumerate(note.lines) if re.fullmatch(r"##[ \t]+Original Content[ \t]*", l)]
    if not starts:
        rep.block(path, "Raw has no '## Original Content' section")
        return None
    start = starts[0] + 1
    ends = []
    for name in ("Metadata", "Ingest Notes"):
        found = [i for i, l in enumerate(note.lines)
                 if i >= start and re.fullmatch(rf"##[ \t]+{name}[ \t]*", l)]
        if found:
            ends.append(found[-1])
    end = min(ends) if ends else len(body_lines)
    evidence = norm_text("\n".join(body_lines[start:end]))
    if not evidence:
        rep.block(path, "Raw '## Original Content' is empty")
        return None
    titles = {heading_key(t)[0] for _, lvl, t in headings(note.lines[:start]) if lvl == 1}
    for key in ("title", "aliases"):
        value = note.fm.get(key)
        for item in value if isinstance(value, list) else [value]:
            if isinstance(item, str):
                titles.add(heading_key(item)[0])
    titles.add(heading_key(path.stem)[0])
    return Raw(path, evidence, leaf_headings(note.lines[start:end], titles))


def heading_key(text: str) -> tuple[str, str, str]:
    """(full key, section number, title without number) for heading matching."""
    t = re.sub(r"\[\[(?:[^\]|]*\|)?([^\]]*)\]\]", r"\1", text)
    t = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", t)
    t = re.sub(r"[*`]|(?<!\w)_|_(?!\w)", "", t)
    t = norm_text(t).casefold().strip().rstrip(":.").strip()
    t = t.lstrip("§").strip()
    if re.fullmatch(r"\d+(?:\.\d+)*\.?", t):
        return t, t.rstrip("."), ""
    m = NUM_PREFIX_RE.match(t)
    if not m:
        return t, "", t
    return t, m.group(1).rstrip(".)"), t[m.end():].strip()


def leaf_headings(lines: list[str], title_keys: set[str]) -> list[str]:
    hs = [(lvl, text) for _, lvl, text in headings(lines)]
    leaves = []
    for k, (lvl, text) in enumerate(hs):
        if k + 1 < len(hs) and hs[k + 1][0] > lvl:
            continue
        key = heading_key(text)
        if key[0] in NON_CONTENT_HEADINGS or key[2] in NON_CONTENT_HEADINGS:
            continue
        if lvl == 1 and key[0] in title_keys:
            continue
        leaves.append(text)
    return leaves


def part_matches(part: tuple[str, str, str], leaf: tuple[str, str, str]) -> bool:
    pf, pn, pr = part
    lf, ln, lr = leaf
    numbers_agree = not pn or not ln or pn == ln
    if pf == lf:
        return True
    if pr and pr == lr and numbers_agree:
        return True
    return not pr and bool(pn) and pn == ln


def prefix_matches(part: tuple[str, str, str], leaf: tuple[str, str, str]) -> bool:
    _, pn, pr = part
    _, ln, lr = leaf
    if not pr or len(pr) < 8 or len(pr.split()) < 2 or (pn and ln and pn != ln):
        return False
    return lr.startswith(pr) and (len(lr) == len(pr) or lr[len(pr)] == " ")


def hub_section(paper: Paper, title: str) -> list[str] | None:
    found = [body for t, body in h2_sections(paper.hub.lines) if t == fold_name(title)]
    if not found:
        paper.rep.fail(paper.hub.path, f"missing '## {title}' section")
        return None
    if len(found) > 1:
        paper.rep.fail(paper.hub.path, f"'## {title}' section appears {len(found)} times")
    return found[0]


def check_catalog(paper: Paper) -> set[Path]:
    rep, hub = paper.rep, paper.hub
    catalog: set[Path] = set()
    lines = hub_section(paper, "Atom Catalog")
    if lines is None:
        return catalog
    groups: list[tuple[int, int | None, list[Path]]] = []
    for line in lines:
        m = re.match(r"^###[ \t]+S(\d{1,2})\b(.*)$", line)
        if m:
            count = re.search(r"\((\d+)\s*atoms?\)", m.group(2))
            groups.append((int(m.group(1)), int(count.group(1)) if count else None, []))
            continue
        for path in resolve_links(paper, hub, link_targets(line), "Atom Catalog"):
            if path not in paper.atom_paths:
                rep.fail(hub.path, f"Atom Catalog links {rep.where(path)}, which is not an atom in this folder")
                continue
            catalog.add(path)
            if groups:
                groups[-1][2].append(path)
    for step, count, paths in groups:
        for path in paths:
            if file_step(path) != step:
                rep.fail(hub.path, f"Atom Catalog lists {rep.where(path)} under S{step:02d}")
        if count is not None and count != len(set(paths)):
            rep.fail(hub.path, f"Atom Catalog S{step:02d} header says {count} atoms, lists {len(set(paths))}")
    for path in sorted(paper.atom_paths - catalog):
        rep.fail(hub.path, f"atom file {rep.where(path)} is missing from the Atom Catalog")
    return catalog


def check_step_map(paper: Paper) -> None:
    rep, hub = paper.rep, paper.hub
    lines = hub_section(paper, "Step Map")
    if lines is None:
        return
    seen: set[int] = set()
    for cells in table_rows(lines):
        if len(cells) < 4:
            rep.fail(hub.path, f"Step Map row has fewer than 4 cells: {' | '.join(cells)}")
            continue
        m = re.fullmatch(r"S?0*(\d{1,2})", cells[0])
        if not m:
            rep.fail(hub.path, f"Step Map row has no step number: {' | '.join(cells)}")
            continue
        step, name, atoms, status = int(m.group(1)), cells[1], cells[2], cells[3]
        if step in seen:
            rep.fail(hub.path, f"Step Map lists S{step:02d} more than once")
            continue
        seen.add(step)
        if re.search(r"\bplanned\b", status, re.I):
            rep.fail(hub.path, f"Step Map S{step:02d} is still planned")
        if step == 1:
            if fold_name(name) != "citation" or atoms != "(hub)" or fold_name(status) != "compiled":
                rep.fail(hub.path, f"Step Map S01 must be 'CITATION | (hub) | compiled', got "
                                   f"{' | '.join(cells[1:4])!r}")
            continue
        if not 2 <= step <= 12:
            rep.fail(hub.path, f"Step Map row S{step:02d} is outside 1-12")
            continue
        names = paper.step_names
        if names and fold_name(name) != fold_name(names[step]):
            rep.fail(hub.path, f"Step Map S{step:02d} name {name!r} is not {names[step]!r}")
        in_step = [a for a in paper.atoms if file_step(a.path) == step]
        stubs = sum(1 for a in in_step if a.fm.get("status") == "stub")
        if not re.fullmatch(r"\d+", atoms):
            rep.fail(hub.path, f"Step Map S{step:02d} Atoms cell {atoms!r} is not an integer")
        elif int(atoms) != len(in_step):
            rep.fail(hub.path, f"Step Map S{step:02d} says {atoms} atoms; folder has {len(in_step)}")
        if not status:
            rep.fail(hub.path, f"Step Map S{step:02d} has no status")
        elif status.casefold().startswith("skipped"):
            if in_step:
                rep.fail(hub.path, f"Step Map S{step:02d} is skipped but {len(in_step)} atom file(s) exist")
            if not re.search(r"\(\s*\S.*\)", status):
                rep.fail(hub.path, f"Step Map S{step:02d} skipped without a stated reason")
        elif not in_step:
            rep.fail(hub.path, f"Step Map S{step:02d} has no atoms but is not 'skipped (reason)'")
        stated = re.search(r"stub\s*(\d+)\s*건", status)
        if stated and int(stated.group(1)) != stubs:
            rep.fail(hub.path, f"Step Map S{step:02d} states stub {stated.group(1)}건; folder has {stubs}")
        elif stubs and not stated:
            rep.fail(hub.path, f"Step Map S{step:02d} has {stubs} stub atom(s) not stated as 'stub {stubs}건'")
    for step in sorted(set(range(1, 13)) - seen):
        rep.fail(hub.path, f"Step Map has no row for S{step:02d}")


def check_coverage(paper: Paper, catalog: set[Path]) -> None:
    rep, hub = paper.rep, paper.hub
    lines = hub_section(paper, "Coverage Map")
    if lines is None:
        return
    parts: list[tuple[str, tuple[str, str, str], str | None]] = []
    for cells in table_rows(lines):
        if len(cells) < 2 or not cells[0]:
            rep.fail(hub.path, f"Coverage Map row is malformed: {' | '.join(cells)}")
            continue
        section, mapped = cells[0], " | ".join(cells[1:]).strip()
        targets = link_targets(mapped)
        omission = None
        if targets:
            for path in resolve_links(paper, hub, targets, "Coverage Map"):
                if path == hub.path:
                    continue
                if path not in paper.atom_paths:
                    rep.fail(hub.path, f"Coverage Map links {rep.where(path)}, which is not an atom in this folder")
                elif path not in catalog:
                    rep.fail(hub.path, f"Coverage Map links {rep.where(path)}, which the Atom Catalog omits")
        elif mapped.strip(" -—–") and not re.fullmatch(r"\(?\s*\)?", mapped):
            omission = mapped
            rep.omissions.append(f"{section}: {mapped}")
        else:
            rep.fail(hub.path, f"Coverage Map row '{section}' names neither an atom nor a stated omission")
            continue
        for piece in re.split(r"\s+·\s+|;\s+|<br\s*/?>", section):
            if piece.strip():
                parts.append((piece.strip(), heading_key(piece), omission))
    for raw in paper.raws:
        leaves = [(text, heading_key(text)) for text in raw.leaves]
        covered: dict[int, list[str | None]] = {}
        for text, key, omission in parts:
            exact = [k for k, (_, leaf) in enumerate(leaves) if part_matches(key, leaf)]
            if len(exact) > 1:
                rep.fail(hub.path, f"Coverage Map row '{text}' matches {len(exact)} identical Raw "
                                   f"headings; coverage is ambiguous")
                continue
            if not exact:
                prefixed = [k for k, (_, leaf) in enumerate(leaves) if prefix_matches(key, leaf)]
                if len(prefixed) > 1:
                    rep.fail(hub.path, f"Coverage Map row '{text}' is an ambiguous prefix of "
                                       f"{len(prefixed)} Raw headings")
                exact = prefixed if len(prefixed) == 1 else []
            for k in exact:
                covered.setdefault(k, []).append(omission)
        for k, (text, _) in enumerate(leaves):
            if k not in covered:
                rep.fail(hub.path, f"Raw heading '{text}' ({rep.where(raw.path)}) has no Coverage Map row")
            elif all(o is not None for o in covered[k]):
                rep.not_verified(hub.path, f"Raw heading '{text}' is covered only by a stated omission")


def check_index(paper: Paper, index_path: Path) -> None:
    rep, hub = paper.rep, paper.hub
    try:
        text = index_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        rep.block(index_path, f"cannot read index.md: {exc}")
        return
    listed = False
    atoms = paper.atom_paths
    for target in link_targets("\n".join(structural_lines(text))):
        res = paper.vault.resolve(target)
        if res.path == hub.path:
            listed = True
        elif res.path in atoms:
            rep.fail(index_path, f"index.md lists atom {rep.where(res.path)} (atoms never go in the index)")
        elif res.path is None and ({hub.path} | atoms) & set(res.candidates):
            rep.fail(index_path, f"index.md link {res.error}")
    if not listed:
        rep.fail(index_path, f"index.md does not link the hub {rep.where(hub.path)}")


def locate_quote(quote: str, evidence: str) -> bool:
    """Contiguous match whose edges do not cut a word, a number or a sign off a number."""
    start = 0
    while True:
        i = evidence.find(quote, start)
        if i < 0:
            return False
        if edges_ok(evidence, i, i + len(quote), quote):
            return True
        start = i + 1


def _wordish(ch: str) -> bool:
    if not ch or not ch.isalnum():
        return False
    cp = ord(ch)
    scriptio_continua = (0x1100 <= cp <= 0x11FF or 0x3040 <= cp <= 0x30FF or 0x3130 <= cp <= 0x318F
                         or 0x3400 <= cp <= 0x4DBF or 0x4E00 <= cp <= 0x9FFF or 0xAC00 <= cp <= 0xD7A3)
    return not scriptio_continua


def edges_ok(text: str, i: int, j: int, quote: str) -> bool:
    before = text[i - 1] if i > 0 else ""
    after = text[j] if j < len(text) else ""
    if _wordish(quote[0]) and _wordish(before):
        return False
    if _wordish(quote[-1]) and _wordish(after):
        return False
    starts_number = quote[0].isdigit() or (quote[0] == "." and len(quote) > 1 and quote[1].isdigit())
    if starts_number and before and before in SIGN_CHARS:
        if not _wordish(text[i - 2] if i > 1 else ""):
            return False
    if quote[-1].isdigit() and after in ".," and j + 1 < len(text) and text[j + 1].isdigit():
        return False
    return True


def quote_candidates(body: str) -> list[str]:
    text = norm_text(body)
    out = [text] if text else []
    if len(text) >= 2 and text[0] == '"' and text[-1] == '"' and text[1:-1].strip():
        out.append(text[1:-1].strip())
    return out


def check_atom(paper: Paper, atom: Note) -> None:
    rep, fm, path = paper.rep, atom.fm, atom.path
    if paper.paper_type and fm.get("paperType") != paper.paper_type:
        rep.fail(path, f"paperType {fm.get('paperType')!r} differs from hub {paper.paper_type!r}")
    if paper.citekey and fm.get("citekey") != paper.citekey:
        rep.fail(path, f"citekey {fm.get('citekey')!r} differs from hub {paper.citekey!r}")
    step = fm.get("analysisStep")
    step_ok = type(step) is int and 2 <= step <= 12
    if not step_ok:
        rep.fail(path, f"analysisStep must be an integer 2-12 (got {step!r})")
    marks = FILE_STEP_RE.findall(path.stem)
    if len(marks) != 1:
        rep.fail(path, "filename must contain exactly one ' - SNN ' marker")
    elif step_ok and int(marks[0]) != step:
        rep.fail(path, f"filename marker S{marks[0]} does not match analysisStep {step}")
    names = paper.step_names
    if step_ok and names:
        name = fm.get("analysisStepName")
        if not isinstance(name, str) or fold_name(name) != fold_name(names[step]):
            rep.fail(path, f"analysisStepName {name!r} is not {names[step]!r}")
    targets, err = frontmatter_links(fm.get("paperHub"))
    if err:
        rep.fail(path, f"paperHub {err}")
    elif paper.hub is not None:
        hubs = resolve_links(paper, atom, targets, "paperHub")
        if hubs and any(h != paper.hub.path for h in hubs):
            rep.fail(path, f"paperHub does not link the hub {rep.where(paper.hub.path)}")
    targets, err = frontmatter_links(fm.get("source"))
    if err:
        rep.fail(path, f"source {err}")
    else:
        for raw in resolve_links(paper, atom, targets, "source"):
            if paper.raw_paths and raw not in paper.raw_paths:
                rep.fail(path, f"source {rep.where(raw)} is not the paper's Raw")
    status = fm.get("status")
    if status not in ("completed", "stub"):
        rep.fail(path, f"status must be 'completed' or 'stub' (got {status!r})")
    check_provenance(atom, rep)
    check_placeholders(atom, rep)
    check_atom_body(paper, atom, status, step if step_ok else None)


def check_atom_body(paper: Paper, atom: Note, status, step: int | None) -> None:
    rep, path, lines = paper.rep, atom.path, atom.lines
    found = callouts(lines)
    if not any(kind == "info" and fold_name(title) == "analysis context" for _, kind, title in found):
        rep.fail(path, "missing '> [!info] Analysis Context' callout")
    located = checked = 0
    for i, kind, title in found:
        if kind != "quote":
            continue
        checked += 1
        if not LOCATOR_RE.search(title):
            rep.fail(path, f"quote header {title!r} has no page (p.N) or § locator")
        candidates = quote_candidates(callout_body(lines, i))
        if not candidates:
            rep.fail(path, f"quote at line {i + 1} of the body is empty")
            continue
        if not paper.raws:
            continue
        if any(locate_quote(c, raw.evidence) for c in candidates for raw in paper.raws):
            located += 1
        else:
            rep.fail(path, "quote not found contiguously in the Raw's Original Content: "
                           f"\"{excerpt(candidates[-1])}\"")
    if checked and not paper.raws:
        rep.not_verified(path, f"{checked} quote(s) unchecked: no usable Raw Original Content")
    if status == "stub":
        rep.not_verified(path, "stub atom: body, quotations and relations not required or verified")
        return
    if status != "completed":
        return
    titles = [t for t, _ in h2_sections(lines)]
    bodies = dict(h2_sections(lines))
    required = (RELATIONS,) if step == 12 else BODY_SECTIONS
    positions = []
    for name in required:
        hits = [k for k, t in enumerate(titles) if t == fold_name(name)]
        if not hits:
            rep.fail(path, f"completed atom is missing '## {name}'")
        elif len(hits) > 1:
            rep.fail(path, f"'## {name}' appears {len(hits)} times")
        else:
            positions.append(hits[0])
            if not any(l.strip() and not THEMATIC_BREAK_RE.match(l) for l in bodies[fold_name(name)]):
                rep.fail(path, f"'## {name}' is empty")
    if len(positions) == len(required) and positions != sorted(positions):
        rep.fail(path, "sections are out of order; expected " + " → ".join(required))
    relation_lines = bodies.get(fold_name(RELATIONS))
    if relation_lines is not None:
        linked = resolve_links(paper, atom, link_targets("\n".join(relation_lines)), RELATIONS)
        if not set(linked) & (paper.atom_paths - {path}):
            rep.fail(path, f"'## {RELATIONS}' links no sibling atom (hub and self do not count)")
    if step == 12:
        if checked == 0:
            rep.not_verified(path, "S12 atom without quotation: source evidence not verified")
    elif located == 0 and paper.raws:
        rep.fail(path, "completed atom has no quotation located in the Raw")


class InputError(Exception):
    pass


def find_vault(explicit: str | None, folder: Path) -> Path:
    if explicit is not None:
        root = Path(explicit).expanduser()
        if not root.is_dir():
            raise InputError(f"--vault {explicit!r} is not a directory")
        return root.resolve()
    for ancestor in folder.parents:
        if (ancestor / "index.md").is_file():
            return ancestor
    raise InputError("no ancestor of PAPER_FOLDER contains index.md; pass --vault VAULT")


def find_raw(explicit: str | None, root: Path) -> Path | None:
    if explicit is None:
        return None
    given = Path(explicit).expanduser()
    if not given.is_file():
        raise InputError(f"--raw {explicit!r} is not a file")
    resolved = given.resolve()
    if not resolved.is_relative_to(root):
        raise InputError(f"--raw {explicit!r} is outside the vault")
    absolute = Path(os.path.abspath(given))
    return absolute if absolute.is_relative_to(root) else resolved


def load_folder(folder: Path, root: Path, rep: Report, loader) -> tuple[list[Note], list[Note]]:
    hubs, atoms = [], []
    for path in sorted(folder.iterdir()):
        if path.name.startswith("."):
            continue
        if path.is_dir():
            nested = [p for p in path.rglob("*.md") if not any(s.startswith(".") for s in p.relative_to(folder).parts)]
            if nested:
                rep.fail(path, f"subfolder holds {len(nested)} Markdown note(s); nested atoms are "
                               f"not supported, keep every atom directly in the paper folder")
            continue
        if path.suffix.casefold() != ".md":
            continue
        if not path.resolve().is_relative_to(root):
            rep.fail(path, "symlink points outside the vault")
            continue
        note = load_note(path, rep, loader)
        if note is None:
            continue
        kind = note.fm.get("type")
        if kind == "paper-hub":
            hubs.append(note)
        elif kind == "paper-analysis":
            atoms.append(note)
        else:
            rep.fail(path, f"type {kind!r} is neither paper-hub nor paper-analysis")
    return hubs, atoms


def print_report(rep: Report, folder: Path) -> int:
    print(f"verify_paper: {rep.where(folder)}")
    for title, items in (("FAIL", rep.failures), ("BLOCKED", rep.blockers),
                         ("NOT FULLY VERIFIED", rep.unverified),
                         ("STATED OMISSIONS (not covered by atoms)", rep.omissions)):
        if items:
            print(f"\n{title} ({len(items)})")
            for item in items:
                print(f"  - {item}")
    print("\nLIMITS")
    print("  - Mechanical only: semantic fidelity, decomposition and exposition are not checked.")
    print("  - Quotations are matched contiguously after normalization; whether they support the claim is not checked.")
    print("  - Page and § locators are checked for presence only, not against the source pages.")
    print("  - Raw fidelity to the original document is outside this check.")
    if rep.blockers:
        print(f"\nBLOCKED: {len(rep.blockers)} unresolved prerequisite(s), "
              f"{len(rep.failures)} validation failure(s)")
        return 2
    if rep.failures:
        print(f"\nFAIL: {len(rep.failures)} validation failure(s)")
        return 1
    print("\nALL PASS (mechanical) — not a semantic or qualitative PASS")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Mechanical P-7 review of one paper analysis folder.")
    parser.add_argument("paper_folder", help="folder holding one paper-hub and its paper-analysis atoms")
    parser.add_argument("--vault", help="vault root (default: nearest ancestor containing index.md)")
    parser.add_argument("--raw", help="Raw note to use as evidence (default: the hub's source)")
    args = parser.parse_args(argv)
    if yaml is None:
        print("BLOCKED: PyYAML is required (python3 -m pip install pyyaml)", file=sys.stderr)
        return 2
    folder = Path(args.paper_folder).expanduser()
    try:
        if not folder.is_dir():
            raise InputError(f"PAPER_FOLDER {args.paper_folder!r} is not a directory")
        folder = folder.resolve()
        root = find_vault(args.vault, folder)
        if folder == root or not folder.is_relative_to(root):
            raise InputError("PAPER_FOLDER must be inside the vault")
        index_path = root / "index.md"
        if not index_path.is_file():
            raise InputError("the vault has no index.md")
        explicit_raw = find_raw(args.raw, root)
    except InputError as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        return 2
    rep = Report()
    rep.root = root
    loader = unique_key_loader()
    hubs, atoms = load_folder(folder, root, rep, loader)
    paper = Paper(Vault(root), rep, folder, hubs[0] if len(hubs) == 1 else None, atoms)
    if len(hubs) != 1:
        rep.block(folder, f"expected exactly one parseable paper-hub note, found {len(hubs)}")
    if not atoms:
        rep.fail(folder, "no paper-analysis atoms in the folder")
    if paper.hub is not None:
        check_hub(paper, explicit_raw, loader)
    for atom in atoms:
        check_atom(paper, atom)
    if paper.hub is not None:
        catalog = check_catalog(paper)
        check_step_map(paper)
        check_coverage(paper, catalog)
        check_index(paper, index_path)
    return print_report(rep, folder)


if __name__ == "__main__":
    sys.exit(main())
