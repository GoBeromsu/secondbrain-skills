#!/usr/bin/env python3
"""Agent-level eval for the knowledge skills (term, concept, entity, secondbrain-mode).

Runs each case of evals/<skill>/evals.json through `claude -p` on a fresh temp copy of the fixture
vault, saves the outputs in skill-creator's workspace layout, and grades every expectation with a
programmatic check. The committed fixture is never written.

  python3 evals/agent_run.py term                     # new skill and the 0.28.1 baseline, iteration 1
  python3 evals/agent_run.py term --config new --iteration 2 --cases 1,3
  python3 evals/agent_run.py term --grade-only --iteration 1

Layout (aggregate_benchmark.py reads it):
  evals/results/<skill>-workspace/iteration-<N>/eval-<id>-<name>/{with_skill,old_skill}/run-1/
    grading.json  timing.json  outputs/{answer.md,transcript.jsonl,changes.json,diff.patch,vault/}

Runs use only the plugin under test (`--plugin-dir`) with user settings, plugins and MCP servers off,
and an `obsidian` stub on PATH: the real CLI would open or switch the owner's vault.
"""
import argparse
import difflib
import fnmatch
import json
import os
import re
import shlex
import shutil
import stat
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from types import SimpleNamespace

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LINK_LINT = os.path.join(ROOT, "skills", "lint", "scripts", "link-lint.py")
BASELINE_REF = "1c73d0b"
CONFIGS = {"new": "with_skill", "old": "old_skill"}
WIKILINK = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|([^\]]*))?\]\]")

SKILL_WRAPPER = """Read {skill_md} and follow it for the user message below.
The vault root is {vault} (its live policy is {vault}/Guideline.md). Work only inside the vault root.
The `obsidian` CLI is not available here: search and read the vault files directly instead.
Today is 2026-11-26.

User message:
{prompt}"""

MODE_WRAPPER = """Secondbrain mode is on for this session: read {skill_md} and follow it for the user message below.
The vault root is {vault} (its live policy is {vault}/Guideline.md). Work only inside the vault root.
The `obsidian` CLI is not available here: search and read the vault files directly instead.
Today is 2026-11-26.

User message:
{prompt}"""

OLD_MODE_WRAPPER = """The skills of this plugin are at {skills_dir}/<name>/SKILL.md; use whichever the message needs.
The vault root is {vault} (its live policy is {vault}/Guideline.md). Work only inside the vault root.
The `obsidian` CLI is not available here: search and read the vault files directly instead.
Today is 2026-11-26.

User message:
{prompt}"""


# ---------------------------------------------------------------- vault helpers

def regular_file(path):
    try:
        return stat.S_ISREG(os.lstat(path).st_mode)
    except FileNotFoundError:
        return False


DIRECTORY_FLAGS = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW


def copy_evidence_dir(fd, dest):
    os.mkdir(dest)
    for name in os.listdir(fd):
        if name == ".obsidian":
            continue
        mode = os.lstat(name, dir_fd=fd).st_mode
        target = os.path.join(dest, name)
        if stat.S_ISDIR(mode):
            child = os.open(name, DIRECTORY_FLAGS, dir_fd=fd)
            try:
                copy_evidence_dir(child, target)
            finally:
                os.close(child)
        elif stat.S_ISREG(mode):
            source = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd)
            with os.fdopen(source, "rb") as f:
                info = os.fstat(f.fileno())
                if stat.S_ISREG(info.st_mode) and info.st_nlink == 1:
                    with open(target, "xb") as out:
                        shutil.copyfileobj(f, out)


def copy_evidence(src, dest):
    """Reject linked ancestors and anchor all source reads to no-follow directory descriptors."""
    fd = os.open(os.sep, DIRECTORY_FLAGS)
    try:
        for name in os.path.abspath(src).split(os.sep)[1:]:
            try:
                if not stat.S_ISDIR(os.lstat(name, dir_fd=fd).st_mode):
                    return False
                child = os.open(name, DIRECTORY_FLAGS, dir_fd=fd)
            except (FileNotFoundError, NotADirectoryError):
                return False
            os.close(fd)
            fd = child
        copy_evidence_dir(fd, dest)
        return True
    finally:
        os.close(fd)


def walk(root):
    out = {}
    if os.path.islink(root):
        return out
    for d, dirs, files in os.walk(root):
        dirs[:] = [x for x in dirs if x not in (".obsidian", ".git", ".claude", ".trash")]
        for f in files:
            full = os.path.join(d, f)
            if not regular_file(full):
                continue
            with open(full, "rb") as fh:
                out[os.path.relpath(full, root)] = fh.read()
    return out


def changes(before, after):
    created = sorted(set(after) - set(before))
    deleted = sorted(set(before) - set(after))
    modified = sorted(p for p in set(before) & set(after) if before[p] != after[p])
    return {"created": created, "modified": modified, "deleted": deleted}


def split_fm(text):
    """(frontmatter text or None, body, raw key order)."""
    if not text.startswith("---\n"):
        return None, text, []
    end = text.find("\n---", 4)
    if end < 0:
        return None, text, []
    fm = text[4:end]
    body = text[end + 4:].lstrip("\n")
    keys = [m.group(1) for m in re.finditer(r"^([A-Za-z_][\w-]*):", fm, re.M)]
    return fm, body, keys


def fm_value(fm, key):
    """Scalar or list value of a top-level key, as strings with quotes removed."""
    m = re.search(r"^%s:[ \t]*(.*)$" % re.escape(key), fm or "", re.M)
    if not m:
        return None
    rest = m.group(1).strip()
    if rest and rest not in ("|", ">"):
        if rest.startswith("[") and rest.endswith("]"):
            return [x.strip().strip("'\"") for x in rest[1:-1].split(",") if x.strip()]
        return rest.strip("'\"")
    items = []
    for line in fm[m.end():].split("\n")[1:]:
        if re.match(r"^\s+-\s*", line):
            items.append(re.sub(r"^\s+-\s*", "", line).split(" #")[0].strip().strip("'\""))
        elif line.strip() and not line.startswith(" "):
            break
    return items


def h2s(text):
    _, body, _ = split_fm(text)
    out, fence = [], False
    for line in body.split("\n"):
        if line.startswith("```"):
            fence = not fence
        if not fence and re.match(r"^## \S", line):
            out.append(line.strip())
    return out


def section(text, heading):
    lines = text.split("\n")
    out, on = [], False
    depth = len(heading.split()[0])
    for line in lines:
        if on and re.match(r"^#{1,%d} " % depth, line):
            break
        if line.strip() == heading:
            on = True
            continue
        if on:
            out.append(line)
    return out if on else None


def unlink(text):
    return WIKILINK.sub(lambda m: m.group(2) if m.group(2) is not None else m.group(1), text)


# ---------------------------------------------------------------- checks

class Ctx:
    def __init__(self, case, run_dir, before, after, answer, events, subagents, mode=False, vault=None):
        self.case, self.run_dir, self.before, self.after = case, run_dir, before, after
        self.answer, self.events, self.subagents = answer, events, subagents
        self.mode = mode
        self.vault = vault
        self.ch = changes(before, after)
        self.guideline = self.text("Guideline.md", "before") or ""
        self.roles = dict(re.findall(r"^\|\s*(wiki|source)\s*\|\s*`([^`]+)`\s*\|", self.guideline, re.M))
        self.targets = {}
        for name, t in case.get("targets", {}).items():
            pool = {"created": self.ch["created"], "modified": self.ch["modified"]}.get(
                t.get("state"), self.ch["created"] + self.ch["modified"])
            hits = [p for p in pool if fnmatch.fnmatch(p, t["glob"])
                    and re.search(t.get("name_regex", ""), os.path.basename(p)[:-3] if p.endswith(".md") else p)]
            self.targets[name] = sorted(hits)[0] if hits else None

    def path(self, ref):
        if ref.startswith("@"):
            return self.targets.get(ref[1:])
        return ref

    def text(self, ref, which="after"):
        p = self.path(ref)
        src = self.after if which == "after" else self.before
        if p is None or p not in src:
            return None
        return src[p].decode("utf-8", "replace")

    def files(self, spec):
        """Resolve a list of refs/globs or the keyword @changed_wiki to existing vault paths."""
        if spec == "@changed_wiki":
            return self.changed_notes("wiki")
        out = []
        for s in spec:
            p = self.path(s)
            if p is None:
                continue
            out += sorted(x for x in set(self.before) | set(self.after) if fnmatch.fnmatch(x, p)) or [p]
        return out

    def role_prefix(self, role):
        return self.roles[role].strip("/") + "/"

    def changed_notes(self, role, ops=("created", "modified")):
        prefix = self.role_prefix(role)
        return [p for op in ops for p in self.ch[op] if p.startswith(prefix) and p.endswith(".md")]


def missing(ctx, ref):
    return False, "no file resolved for %s" % ref


def ck_exists(ctx, e):
    p = ctx.path(e["file"])
    return (p is not None and p in ctx.after), "resolved to %s" % p


def ck_frontmatter(ctx, e):
    t = ctx.text(e["file"])
    if t is None:
        return missing(ctx, e["file"])
    fm, _, keys = split_fm(t)
    if fm is None:
        return False, "no frontmatter"
    bad = []
    if e.get("alphabetical") and keys != sorted(keys):
        bad.append("keys not alphabetical: %s" % keys)
    for k in e.get("absent", []):
        if k in keys:
            bad.append("has %s" % k)
    for k, v in e.get("equals", {}).items():
        got = fm_value(fm, k)
        if got != v:
            bad.append("%s=%r, want %r" % (k, got, v))
    for k, v in e.get("contains", {}).items():
        got = fm_value(fm, k) or []
        got = got if isinstance(got, list) else [got]
        if not any(re.search(v, g) for g in got):
            bad.append("%s=%r lacks /%s/" % (k, got, v))
    for k in e.get("present", []):
        if k not in keys:
            bad.append("missing %s" % k)
    return not bad, "; ".join(bad) or "ok: keys %s" % keys


def ck_headings(ctx, e):
    t = ctx.text(e["file"])
    if t is None:
        return missing(ctx, e["file"])
    with open(os.path.join(ROOT, e["template"]), encoding="utf-8") as f:
        tmpl = h2s(f.read())
    got = h2s(t)
    bad = []
    extra = [h for h in got if h not in tmpl]
    if extra:
        bad.append("headings not in template: %s" % extra)
    known = [h for h in got if h in tmpl]
    if known != sorted(known, key=tmpl.index):
        bad.append("out of template order: %s" % known)
    for r in e.get("required", []):
        if r not in got:
            bad.append("missing %s" % r)
    for c in e.get("callouts", []):
        if c not in t:
            bad.append("missing callout %s" % c)
    return not bad, "; ".join(bad) or "ok: %s" % got


def ck_lint_clean(ctx, e):
    scope = e.get("files", "@changed_wiki")
    files = ctx.files(scope)
    missing_wiki = scope == "@changed_wiki" and not files and not e.get("optional")
    if ctx.mode:
        files = list(dict.fromkeys(files + ctx.changed_notes("source")))
    if not files:
        return bool(e.get("optional")), "no wiki page written" if missing_wiki else "no pages to lint"
    missing_files = [f for f in files if f not in ctx.after]
    if missing_files:
        return False, "missing scoped pages: %s" % missing_files
    vault = os.path.join(ctx.run_dir, "outputs", "vault-full")
    wiki = ctx.role_prefix("wiki").rstrip("/")
    cmd = [sys.executable, LINK_LINT, "--vault", vault, "--checks", "all", "--wiki", wiki,
           "--lifecycle", "project,task"]
    entities = re.search(r"^Wiki subfolders:.*?(`[^`]+`(?:, `[^`]+`)*(?: and `[^`]+`)?) for Entities\b",
                         ctx.guideline, re.M)
    if entities:
        for folder in re.findall(r"`([^`]+)`", entities[1]):
            cmd.extend(("--entity-folder", wiki + "/" + folder.strip("/")))
    for kind in re.findall(r"Book Entities of `type: ([^`]+)`", ctx.guideline):
        cmd.extend(("--book-type", kind))
    p = subprocess.run(cmd + ["--scope", *files], capture_output=True, text=True)
    # link-lint itself excludes only the single planned link in the Term template.
    rows = [l for l in p.stdout.splitlines() if l and not l.startswith("#")]
    if p.returncode not in (0, 1):
        return False, "link-lint exit %d: %s" % (p.returncode, p.stderr.strip()[-200:])
    if missing_wiki:
        rows.insert(0, "no wiki page written")
    return not rows, ("findings: " + " | ".join(rows[:8])) if rows else "0 findings on %s" % files


def ck_no_new_under(ctx, e):
    hits = [p for p in ctx.ch["created"] if p.startswith(e["prefix"])]
    return not hits, ("created %s" % hits) if hits else "nothing created under %s" % e["prefix"]


def ck_changed_only_within(ctx, e):
    allow = [ctx.path(a) for a in e.get("allow", [])]
    out = [p for k in ("created", "modified", "deleted") for p in ctx.ch[k]
           if not any(p.startswith(x) for x in e["prefixes"]) and p not in allow]
    return not out, ("changed outside %s: %s" % (e["prefixes"], out)) if out else "ok: %s" % ctx.ch


def ck_no_changes_under(ctx, e):
    hits = [(op, p) for op, paths in ctx.ch.items() for p in paths if p.startswith(e["prefix"])]
    return not hits, ("changes: %s" % hits) if hits else "nothing changed under %s" % e["prefix"]


def ck_records_updated(ctx, e):
    missing = set(e["files"]) - set(ctx.ch["created"]) - set(ctx.ch["modified"])
    return not missing, ("records not updated: %s" % sorted(missing)) if missing else "both records updated"


def ck_unchanged(ctx, e):
    bad = [p for p in ctx.files(e["files"])
           if (e.get("include_created") or p in ctx.before) and ctx.before.get(p) != ctx.after.get(p)]
    return not bad, ("changed: %s" % bad) if bad else "byte-identical"


def ck_first_mention_link(ctx, e):
    """Exactly one span changes: the first prose mention becomes a link to the page the run created."""
    old, new = ctx.text(e["file"], "before"), ctx.text(e["file"])
    if old is None or new is None:
        return missing(ctx, e["file"])
    if old == new:
        return False, "work note unchanged: first mention not linked"
    page = ctx.path(e["target"])
    if page is None:
        return False, "no created page to link"
    target = os.path.basename(page)[:-3]
    _, body, _ = split_fm(old)
    first = re.search(e["term_regex"], body)
    if not first:
        return False, "fixture has no mention matching /%s/" % e["term_regex"]
    start = len(old) - len(body) + first.start()
    orig = first.group(0)
    allowed = ["[[%s|%s]]" % (target, orig)]
    if target.lower() == orig.lower():
        allowed.append("[[%s]]" % target)
    for link in allowed:
        if new == old[:start] + link + old[start + len(orig):]:
            return True, "only change: %r -> %s" % (orig, link)
    diff = list(difflib.unified_diff(old.splitlines(), new.splitlines(), lineterm="", n=0))
    return False, "want only %r -> %s; got %s" % (orig, " or ".join(allowed), " / ".join(diff[2:8]))


def ck_section_line(ctx, e):
    t = ctx.text(e["file"])
    if t is None:
        return missing(ctx, e["file"])
    lines = section(t, e["heading"])
    if lines is None:
        return False, "no %s section" % e["heading"]
    fence, prose = False, []
    for l in lines:
        if l.lstrip().startswith("```"):
            fence = not fence
        elif not fence:
            prose.append(l)
    if "patterns" in e:
        absent = [pat for pat in e["patterns"] if not any(re.search(pat, l) for l in prose)]
        return not absent, ("missing %s in %s" % (absent, e["heading"])) if absent else "steps found in %s" % e["heading"]
    hits = [l for l in prose if re.search(e["regex"], l)]
    return bool(hits), hits[0] if hits else "no line matches /%s/ in %s" % (e["regex"], lines)


def ck_moved_verbatim(ctx, e):
    """The sentences sit byte-exact in the destination's body and nowhere in the source's body."""
    src, dst = ctx.text(e["from"]), ctx.text(e["to"])
    if dst is None:
        return missing(ctx, e["to"])
    bad = []
    src_body = split_fm(src)[1] if src is not None else ""
    for sentence in re.split(r"(?<=[.!?])\s+", e["sentences"]):
        if sentence and sentence in src_body:
            bad.append("%r still on %s" % (sentence[:40], ctx.path(e["from"])))
    if e["sentences"] not in split_fm(dst)[1]:
        bad.append("not verbatim in the body of %s" % ctx.path(e["to"]))
    return not bad, "; ".join(bad) or "moved verbatim to %s" % ctx.path(e["to"])


def ck_contains(ctx, e):
    t = ctx.text(e["file"])
    if t is None:
        return missing(ctx, e["file"])
    hit = re.search(e["regex"], t, re.M)
    want = e.get("present", True)
    return bool(hit) == want, ("found %r" % hit.group(0)) if hit else "no match for /%s/" % e["regex"]


def ck_count_created(ctx, e):
    hits = [p for p in ctx.ch["created"] if fnmatch.fnmatch(p, e["glob"])
            and re.search(e.get("name_regex", ""), os.path.basename(p))]
    if "frontmatter_equals" in e:
        hits = [p for p in hits if all(fm_value(split_fm(ctx.after[p].decode("utf-8", "replace"))[0], k) == v
                                       for k, v in e["frontmatter_equals"].items())]
    ok = e.get("min", 0) <= len(hits) <= e.get("max", 10 ** 6)
    return ok, "%d created: %s" % (len(hits), hits)


def ck_raw_original(ctx, e):
    paths = [p for p in ctx.ch["created"] if p.endswith(".md") and (
        p.startswith(ctx.role_prefix("source")) or fm_value(split_fm(ctx.text(p))[0], "type") == "raw-source")]
    if len(paths) != 1:
        return False, "expected exactly one new Raw: %s" % paths
    for path in paths:
        if not path.startswith(ctx.role_prefix("source")):
            continue
        fm, body, _ = split_fm(ctx.text(path))
        if fm_value(fm, "type") != "raw-source":
            continue
        start = re.search(r"^## Original Content\n\n", body, re.M)
        if not start:
            continue
        original = body[start.end():]
        if original.startswith(e["content"]):
            tail = original[len(e["content"]):]
            markers = list(re.finditer(r"^<!-- end-original-content -->[ \t]*$", original, re.M))
            if not markers or markers[-1].start() != len(e["content"]) + 2 or not re.match(
                r"^\n\n<!-- end-original-content -->[ \t]*(?:\n?\Z|\n\n## Ingest Notes(?:\n|$))", tail):
                continue
            return True, "verbatim Original Content in %s" % path
    return False, "no new Raw contains the exact handed-over article followed by its closing marker: %s" % paths


def ck_links_new_page(ctx, e):
    """The MOC body gains a wikilink, outside code, to a wiki page this run created."""
    p = ctx.path(e["file"])
    if p not in ctx.ch["modified"]:
        return False, "%s not modified" % p
    def links(text):
        body = re.sub(r"```.*?```|`[^`\n]*`|<!--.*?-->", "", split_fm(text)[1], flags=re.S)
        return {m.group(1).strip() for m in WIKILINK.finditer(body)}
    new = links(ctx.text(p)) - links(ctx.text(p, "before"))
    wiki = e.get("wiki", ctx.case.get("wiki", "Knowledge/"))
    names = {os.path.basename(x)[:-3] for x in ctx.ch["created"] if x.endswith(".md") and x.startswith(wiki)}
    hit = new & names
    return bool(hit), ("adds links to %s" % sorted(hit)) if hit else "added %s, created wiki pages %s" % (sorted(new), sorted(names))


def answer_lines(ctx):
    return [l for l in ctx.answer.strip().split("\n") if l.strip()]


FOOTER = re.compile(r"^\W*Wiki:\s")


def footer(ctx):
    lines = answer_lines(ctx)
    return lines[-1] if lines and FOOTER.match(lines[-1]) else None


def footer_clauses(line):
    """Parse the whole footer, not just verbs and links found somewhere in it."""
    remaining = line.removeprefix("Wiki: ")
    if remaining == line:
        return None
    out = {"created": [], "updated": [], "failed": []}
    order = list(out)
    verb = None
    while remaining:
        clause = re.match(r"(created|updated|failed) ", remaining)
        if clause:
            if verb is not None and order.index(clause[1]) <= order.index(verb):
                return None
            verb = clause[1]
            remaining = remaining[clause.end():]
        if verb is None:
            return None
        link = re.match(r"\[\[([^\[\]|#\r\n]+)\]\]", remaining)
        if not link or not link[1].strip() or link[1] != link[1].strip():
            return None
        out[verb].append(link[1])
        remaining = remaining[link.end():]
        if verb == "failed":
            if not remaining.startswith(" ("):
                return None
            depth = 0
            for i, ch in enumerate(remaining[1:], 1):
                depth += (ch == "(") - (ch == ")")
                if depth == 0:
                    break
            if depth or not remaining[2:i].strip():
                return None
            remaining = remaining[i + 1:]
        if not remaining:
            return out
        separator = re.match(r", (?=\S)", remaining)
        if not separator:
            return None
        remaining = remaining[separator.end():]
    return None


def ck_answer_line(ctx, e):
    lines = answer_lines(ctx)
    for line in lines:
        if any(re.search(rx, line) for rx in e.get("forbid", [])):
            return False, "contradictory answer line: %s" % line[:200]
    pool = lines[-1:] if e.get("position") == "last" else lines
    if e.get("unquoted"):
        body = re.sub(r"^[ \t]*(`{3,}|~{3,})[^\n]*\n.*?^[ \t]*\1[ \t]*$", "", "\n".join(pool), flags=re.M | re.S)
        pool = [re.sub(r'"[^"\n]*"|“[^”\n]*”|‘[^’\n]*’|`[^`\n]*`|(?<!\w)\'[^\'\n]*\'(?!\w)', " … ",
                       unlink(line)).replace("**", "") for line in body.splitlines() if not line.lstrip().startswith(">")]
    if e.get("asserted"):
        pool = [s for line in pool for s in re.split(r"(?<=[.!?])\s+", line)
                if not s.endswith("?") and not re.search(
                    r"(?i)\b(?:if|whether|assuming|assume|suppose|hypothesis|hypothetically|speculation|might|perhaps|maybe|possibly|could be|not true that|rumou?r(?:s|ed)?|allegedly|reportedly|unconfirmed|not confirmed|according to)\b|라면|일지도|일까|소문|미확인|(?:다고|라고)\s*(?:보도|주장|전해|합니다)|됐다는|되었다는|라는\s*(?:말|주장|보도)|(?:직함|임명)[^.!?]{0,30}확인되지", s)
                and not any(re.search(rx, s) for rx in e.get("attribution", []))]
    hit = [l for l in pool if re.search(e["regex"], l)]
    return bool(hit), hit[0] if hit else "last line: %r" % (lines[-1] if lines else "")


def ck_footer_matches(ctx, e):
    """The final Wiki line reports only observed wiki outcomes, and reports all of them."""
    lines = answer_lines(ctx)
    f = footer(ctx)
    written = {verb: {p[:-3] for p in ctx.changed_notes("wiki", (op,))}
               for verb, op in (("created", "created"), ("updated", "modified"))}
    traces = [(u, r) for u, r in resolved_uses(ctx) if u.get("name") not in ("Agent", "Task")]
    for _, events in ctx.subagents.values():
        traces.extend(resolved_uses(ctx, events))
    written["failed"] = {p[:-3] for u, r in traces if r.get("is_error") for p in write_paths(ctx, u)
                         if p.startswith(ctx.role_prefix("wiki")) and p.endswith(".md")}
    written["failed"] -= written["created"] | written["updated"]
    wiki_outcomes = set().union(*written.values())
    wiki_lines = [l for l in lines if FOOTER.match(l)]
    if f is None:
        ok = not wiki_lines and not wiki_outcomes and e.get("optional")
        return bool(ok), "no final Wiki line; wiki outcomes %s" % sorted(wiki_outcomes)
    if len(wiki_lines) != 1:
        return False, "more than one Wiki line"
    cl = footer_clauses(f)
    if cl is None:
        return False, "malformed Wiki footer: %s" % f[:200]
    bad = []
    named = {verb: [] for verb in written}
    for verb in written:
        seen = set()
        for name in cl[verb]:
            matches = [p for p in written[verb] if p == name or p.endswith("/" + name)]
            if len(matches) != 1 or matches[0] in seen:
                bad.append("%s [[%s]] does not identify a distinct %s wiki page" % (verb, name, verb))
            else:
                seen.add(matches[0])
                named[verb].append(os.path.basename(matches[0]))
        for path in sorted(written[verb] - seen):
            bad.append("%s wiki page [[%s]] not named" % (verb, path))
    for verb, names in e.get("require", {}).items():
        for rx in names:
            if not any(re.search(rx, n) for n in named[verb]):
                bad.append("no %s page matching /%s/" % (verb, rx))
    return not bad, "; ".join(bad) or f[:200]


def ck_modified(ctx, e):
    p = ctx.path(e["file"])
    return p in ctx.ch["modified"], "%s %s" % (p, "modified" if p in ctx.ch["modified"] else "not modified")


def ck_answer_no_wiki_line(ctx, e):
    hit = [l for l in answer_lines(ctx) if FOOTER.match(l)]
    return not hit, ("has %r" % hit[0]) if hit else "no Wiki line"


# Exclude a feature addition attributed to a product version, not other matches on the line.
VERSION_FEATURE = re.compile(r"(?:^|[.!?])[^.!?]*\b버전[은이]\s+(?:(?!위키|볼트)[^.!?])*(?:기능|속성|태그|뷰)[을를]\s*$")
PRODUCT_MAKER = re.compile(r"\b지금은\s+[\w -]+(?:Inc|Corp|Ltd|LLC)\.?[이가]\s*$", re.I)
SOURCE_QUOTE = re.compile(
    r"(?:^|[.!?])\s*(?:(?:이|이번|해당|그)\s+)?(?:글|기사|논문|공지|보도자료|출처)(?:은|는|이|가|도)\s+"
    r"(?:\"[^\"\n]+\"|“[^”\n]+”|‘[^’\n]+’|'[^'\n]+')\s*(?:이?라고)\s*$")
ROLE_TRANSITION = re.compile(r"\d(?:부터|부로)\s+(?:CEO|CTO|CFO|COO|CIO|CMO)(?:으)?로\s*$")
SOURCE_AUTHOR = re.compile(r"(?:발표|공지|보도자료) 캡처에는 원문 URL이 없어서, (?!내가|제가|우리가|저희가)[\w -]+[이가]\s*$")
WIKI_ACTION_CONTEXT = re.compile(r"위키(?:에서|에|로)|볼트(?:에서|에|로)|\b(?:wiki|vault)\b", re.I)
FIRST_PERSON = re.compile(r"(?:^|[\s,])(?:제가|내가|저는|나는|우리가|저희가|우리는|저희는)(?=\s)|\b(?:I|we)\b", re.I)
CARD_PLACEMENT = re.compile(
    r"\b(?:a|the) (?:card|note)\b[^.!?]*\b(?:"
    r"is filed between\s+\d+(?:/\d+)+\s+and\s+\d+(?:/\d+)+\b|"
    r"was filed (?:right )?behind it with a branching (?:number|ID)\b)", re.I)
BACKLINK_MECHANISM = re.compile(
    r"\b(?:backlinks?|incoming links?)\b[^.!?\n]{0,50}\b(?:when|because)\s+"
    r"(?:a|the) link (?:is|was) (?:written|added|created) (?:on|in|from) another (?:page|note)\b"
    r"|\b(?:the|a) list updates itself when links are (?:written|added|created)\b", re.I)
CONTROL_TAG = re.compile(
    r"</?(?:system(?:[-_]reminder)?|tool(?:[-_](?:use|call|result))?|task[-_]notification|function[-_]calls)(?=[\s/>])[^>]*>", re.I)
MODE_BOOKKEEPING = re.compile(
    r"\bstill being (?:looked up|checked)\b|\b(?:the (?:ingest|wiki work)|I(?:'m| am)) (?:is )?still (?:running|working)\b"
    r"|\bI(?:'ll| will) (?:send|report)\b[^.!?\n]*\b(?:once|when)\b"
    r"|\b(?:I (?:can|could)|I(?:'ll| will)|(?:would you like|want) me to)\b[^.!?\n]*\b(?:edit|update|write|save|fill in|create|change)\b[^.!?\n]*\b(?:pages?|notes?|wiki|vault)\b"
    r"|\b(?:I|we) (?:did not|didn't|haven't|have not) (?:edit|update|write|save|change|create|modify)\b[^.!?\n]*\b(?:pages?|notes?|wiki|vault|anything)\b"
    r"|\b(?:no wiki (?:edits|writes|changes)|(?:wiki )?edits made: none)\b"
    r"|\bno (?:edits|writes|changes)\b[^.!?\n]*\b(?:to|in) (?:your|the) (?:vault|wiki|notes?)\b"
    r"|(?:페이지|위키|볼트)[^.!?\n]{0,80}(?:(?:수정하지|고치지|쓰지|편집하지)(?:는)? 않았|고칠게요|수정해 ?드릴|보강해 ?드릴|채워 ?넣을 수)"
    r"|(?:원하시면|원한다면)[^.!?\n]*(?:페이지|위키|볼트)[^.!?\n]*(?:고치|고칠|수정|작성|저장|추가|갱신)", re.I)


def ck_answer_no_wiki_prose(ctx, e):
    """Check every body line; principle decisions may be cited, but not reports of wiki writes."""
    lines = answer_lines(ctx)
    tags = CONTROL_TAG.findall(ctx.answer)
    if (f := footer(ctx)) is not None and footer_clauses(f) is not None:
        lines = lines[:-1]
    pat = re.compile("|".join(e["forbid"]), re.I)
    hits = [line for line in lines if MODE_BOOKKEEPING.search(line) or any(
        not ((m.group() == "추가했" and VERSION_FEATURE.search(line[:m.start()]))
             or (m.group() == "만들고" and PRODUCT_MAKER.search(line[:m.start()]))
             or (m.group() == "적었" and SOURCE_QUOTE.search(line[:m.start()]))
             or (m.group().lower() in {"is filed", "was filed"} and any(
                 card.start() <= m.start() < card.end() for card in CARD_PLACEMENT.finditer(line))
                 and not WIKI_ACTION_CONTEXT.search(line) and not FIRST_PERSON.search(line))
             or (m.group().lower().startswith(("is ", "was ", "are ")) and any(
                 mechanism.start() <= m.start() < mechanism.end() for mechanism in BACKLINK_MECHANISM.finditer(line))
                 and not WIKI_ACTION_CONTEXT.search(line) and not FIRST_PERSON.search(line))
             or (m.group() == "옮겼" and ROLE_TRANSITION.search(line[:m.start()])
                 and not WIKI_ACTION_CONTEXT.search(line) and not FIRST_PERSON.search(line))
             or (m.group() == "작성했" and SOURCE_AUTHOR.search(line[:m.start()])
                 and not WIKI_ACTION_CONTEXT.search(line) and not FIRST_PERSON.search(line)
                 and line[m.end():].startswith("다는 것")))
        for m in pat.finditer(line)
    )]
    evidence = ["echoed control tag: %s" % tags[0]] if tags else []
    if ctx.mode and ctx.events:
        ok, detail = ck_parent_answer(ctx.events)
        if not ok:
            evidence.append(detail)
    evidence.extend("wiki prose: %r" % line[:120] for line in hits[:4])
    return not evidence, "; ".join(evidence) or "no wiki-work prose in the answer body"


def parent_text(events):
    for i, ev in enumerate(events):
        if ev.get("type") != "assistant" or ev.get("parent_tool_use_id") is not None:
            continue
        msg = ev.get("message") or {}
        for block in msg.get("content") or []:
            if block.get("type") == "text" and (text := block.get("text", "").strip()):
                yield i, msg.get("id") or i, text


def ck_parent_answer(events):
    # Only runtime terminal notifications clear launched background tasks, never
    # matching tags printed by the assistant or the tool's launch acknowledgement.
    tasks = {}
    for i, event in enumerate(events):
        if event.get("type") != "system" or event.get("parent_tool_use_id") is not None:
            continue
        key = (event.get("task_id"), event.get("tool_use_id"))
        if not all(key):
            continue
        if event.get("subtype") == "task_started" and event.get("is_backgrounded", True):
            tasks.setdefault(key, len(events))
        if (event.get("subtype") == "task_notification" and key in tasks
                and event.get("status") in {"completed", "failed", "stopped", "cancelled"}):
            tasks[key] = min(i, tasks[key])
    text = list(parent_text(events))
    if text and text[0][0] < max(tasks.values(), default=-1):
        return False, "parent text before trusted completion: %r" % text[0][2][:120]
    turns = len({msg for _, msg, _ in text})
    return turns == 1, "%d visible parent answer messages (expected one)" % turns


def tool_uses(ctx, events=None):
    for ev in ctx.events if events is None else events:
        msg = ev.get("message") or {}
        if ev.get("type") != "assistant" or not isinstance(msg.get("content"), list):
            continue
        for c in msg["content"]:
            if c.get("type") == "tool_use":
                yield ev.get("parent_tool_use_id"), c


WRITE_TOOLS = ("Write", "Edit", "MultiEdit", "NotebookEdit")


def resolved_uses(ctx, events=None):
    events = ctx.events if events is None else events
    results = {}
    for event in events:
        content = (event.get("message") or {}).get("content")
        if event.get("type") == "user" and isinstance(content, list):
            results.update((c.get("tool_use_id"), c) for c in content
                           if isinstance(c, dict) and c.get("type") == "tool_result")
    return [(u, results[u["id"]]) for parent, u in tool_uses(ctx, events)
            if parent is None and u.get("id") in results]


def vault_path(ctx, path):
    if not path:
        return ""
    path = os.path.normpath(path)
    if os.path.isabs(path):
        # Older retained traces may lack the runner's recorded working directory.
        if ctx.vault:
            path = os.path.relpath(path, ctx.vault)
        else:
            path = path.partition("/vault/")[2]
    return path if path != ".." and not path.startswith("../") else ""


def write_paths(ctx, use):
    if use.get("name") in WRITE_TOOLS:
        args = use.get("input", {})
        path = vault_path(ctx, args.get("file_path") or args.get("notebook_path"))
        return {path} if path else set()
    if use.get("name") == "Bash":
        return {p for file in shell_files(use.get("input", {}).get("command", ""))[1] if (p := vault_path(ctx, file))}
    return set()


def shell_words(command):
    try:
        lexer = shlex.shlex(command, posix=True, punctuation_chars=True)
        lexer.whitespace_split = True
        return list(lexer)
    except ValueError:
        return []


def shell_files(command):
    """Exact operands of a single, statically identifiable shell file operation."""
    command = command.removesuffix("\n")
    header, newline, body = command.partition("\n")
    if newline:
        # Only a quoted here-doc has a body that cannot run more commands.
        doc = re.fullmatch(r"(cat +(?:>>?) +.+?) +<< *(['\"])([A-Za-z_][\w]*)\2", header)
        if doc and body.splitlines()[-1:] == [doc[3]] and doc[3] not in body.splitlines()[:-1]:
            return shell_files(doc[1])
        return set(), set()
    # Keep quote delimiters until after testing operators: `printf '>' note.md`
    # is not a redirect. Dynamic paths and compound commands are not evidence.
    if any(c in command for c in "\n\r$`\\"):
        return set(), set()
    try:
        lexer = shlex.shlex(command, posix=False, punctuation_chars=True)
        lexer.whitespace_split = True
        lexer.commenters = ""
        words = list(lexer)
    except ValueError:
        return set(), set()
    if not words or any(w.startswith("#") or re.fullmatch(r"[;&|()<]+", w) for w in words):
        return set(), set()

    def path(token):
        value = token[1:-1] if token.startswith(("'", '"')) and token.endswith(token[:1]) else token
        if not value or value.startswith(("-", "~")) or re.search(r"[*?\[\]{};&|<>'\"]", value):
            return None
        return value

    cmd, args = words[0], words[1:]
    if cmd in ("cat", "head", "tail") and len(args) == 1 and (file := path(args[0])):
        return {file}, set()
    if cmd in ("cat", "echo", "printf") and len(args) >= 2 and args[-2] in (">", ">>"):
        if not any(re.fullmatch(r"[;&|()<>]+", w) for w in args[:-2]) and (file := path(args[-1])):
            return set(), {file}
    if cmd == "touch" and len(args) == 1 and (file := path(args[0])):
        return set(), {file}
    return set(), set()


def parent_shell_write(ctx, command):
    wiki = ctx.role_prefix("wiki")
    for line in command.splitlines():
        words = shell_words(line)
        if any(op in (">", ">>", ">|", "&>", "&>>", "<>") and vault_path(ctx, path).startswith(wiki)
               for op, path in zip(words, words[1:])):
            return True
    # File mutation commands and inline script writes are not valid parent work.
    # Inspect one command at a time so a read followed by an unrelated redirect
    # (such as 2>&1) is not attributed as a wiki write.
    for segment in re.split(r"[;\n]|&&|\|\|", command):
        wiki_ref = r"(?:^|[/\s>'\"=])(?:\./)?" + re.escape(wiki)
        if re.search(wiki_ref, segment) and re.search(
            r"(?:^|\|)\s*(?:mv|cp|rm|mkdir|touch|tee|truncate|install|patch)\b|"
            r"\bsed\s+[^\n]*-i\b|\.(?:write(?:_text|_bytes)?|replace|unlink|rename)\s*\(|\bopen\s*\([^\n]+['\"][wax]",
            segment,
        ):
            return True
    return False


def ck_routed(ctx, e):
    """A top-level background subagent got a kickoff naming <skill>/SKILL.md, opened that file, finished,
    and did the case's writes; the main thread wrote nothing into the wiki itself."""
    skill = e["skill"]
    pat = re.compile(r"(^|[/\s\"'])%s/SKILL\.md(?=\.?(?:$|[^\w./-]))" % re.escape(skill))
    kick = [c for parent, c in tool_uses(ctx) if parent is None and c.get("name") in ("Task", "Agent")
            and pat.search(json.dumps(c.get("input", {}), ensure_ascii=False))]
    if not kick:
        starts = [c.get("input", {}).get("description") for _, c in tool_uses(ctx) if c.get("name") in ("Task", "Agent")]
        return False, "no subagent kickoff names %s/SKILL.md; subagents: %s" % (e["skill"], starts)
    wiki = ctx.role_prefix("wiki")
    main_writes = [p for parent, c in tool_uses(ctx) if parent is None
                   for p in write_paths(ctx, c) if p.startswith(wiki)]
    # Reject visible parent shell writes, including shell expressions outside the
    # narrower set accepted as positive file-level evidence for child work.
    main_bash = [c["input"].get("command", "")[:60] for parent, c in tool_uses(ctx) if parent is None and c.get("name") == "Bash"
                 and parent_shell_write(ctx, c["input"].get("command", ""))]
    if main_writes or main_bash:
        return False, "main thread wrote to the wiki itself: %s" % (main_writes + main_bash)[:3]
    writes = {p for paths in ctx.ch.values() for p in paths if p.startswith(wiki)}
    attributed = set()
    matched_reader = False
    required_reads = set(e.get("reads", []))
    for c in kick:
        child = ctx.subagents.get(c["id"]) or ctx.subagents.get(("prompt", (c["input"].get("prompt") or "").strip()))
        if child is None:
            continue
        meta, events = child
        if not (
            meta.get("requestShape") == "background" if "requestShape" in meta
            else c["input"].get("run_in_background")
        ):
            continue
        uses = [u for u, r in resolved_uses(ctx, events) if not r.get("is_error")]
        reads = {u.get("input", {}).get("file_path", "") for u in uses if u.get("name") == "Read"}
        reads.update(p for u in uses if u.get("name") == "Bash"
                     for p in shell_files(u.get("input", {}).get("command", ""))[0])
        opened = any(
            u.get("name") == "Skill" and u.get("input", {}).get("skill", "").rsplit(":", 1)[-1] == skill
            for u in uses
        ) or any(os.path.normpath(p).endswith("/" + skill + "/SKILL.md") or p == skill + "/SKILL.md" for p in reads)
        if not (meta.get("finished") and opened):
            continue
        attributed.update(p for u in uses for p in write_paths(ctx, u))
        read = {vault_path(ctx, p) for p in reads}
        if required_reads and required_reads <= read:
            matched_reader = True
    if writes - attributed:
        return False, "wiki changes lack successful %s worker writes: %s" % (skill, sorted(writes - attributed))
    if required_reads and not matched_reader:
        return False, "no finished %s worker read %s" % (skill, sorted(required_reads))
    if e.get("writes"):
        return bool(writes), "finished %s worker(s) attributed wiki changes: %s" % (skill, sorted(writes))
    return matched_reader, "finished %s reader opened the skill and read %s: %s" % (
        skill, sorted(required_reads), matched_reader)


CHECKS = {
    "exists": ck_exists, "frontmatter": ck_frontmatter, "headings": ck_headings, "lint_clean": ck_lint_clean,
    "no_new_under": ck_no_new_under, "changed_only_within": ck_changed_only_within, "unchanged": ck_unchanged,
    "no_changes_under": ck_no_changes_under, "records_updated": ck_records_updated,
    "first_mention_link": ck_first_mention_link, "section_line": ck_section_line,
    "moved_verbatim": ck_moved_verbatim, "contains": ck_contains, "count_created": ck_count_created,
    "links_new_page": ck_links_new_page, "answer_line": ck_answer_line, "answer_no_wiki_line": ck_answer_no_wiki_line,
    "answer_no_wiki_prose": ck_answer_no_wiki_prose, "routed": ck_routed, "modified": ck_modified,
    "footer_matches": ck_footer_matches, "raw_original": ck_raw_original,
}


def validate(spec):
    for case in spec["evals"]:
        for name in case.get("fixture_append", {}):
            path = Path(name)
            if path.is_absolute() or ".." in path.parts or path.suffix != ".md":
                sys.exit("eval %s: invalid fixture path %r" % (case["id"], name))
        for e in case["expectations"]:
            if e.get("check") not in CHECKS:
                sys.exit("eval %s: unknown check %r" % (case["id"], e.get("check")))
            for k in ("file", "from", "to", "target"):
                v = e.get(k)
                if v and v.startswith("@") and v[1:] not in case.get("targets", {}):
                    sys.exit("eval %s: unknown target %s" % (case["id"], v))


# ---------------------------------------------------------------- running

def eval_dir(ws, it, case):
    return os.path.join(ws, "iteration-%d" % it, "eval-%d-%s" % (case["id"], case["eval_name"]))


def old_plugin(spec, ws):
    """Plugin dir for the 0.28.1 baseline: its manifest plus the extracted skills tree."""
    plug = os.path.join(ws, "old-plugin")
    skills = os.path.join(HERE, "results", "%s-workspace" % spec["baseline_skill"], "old-skills", spec["baseline_skill"])
    if not os.path.isfile(os.path.join(skills, "SKILL.md")):  # extract once; parallel runners share it
        skills = subprocess.run([os.path.join(HERE, "baseline.sh"), spec["baseline_skill"], BASELINE_REF],
                                capture_output=True, text=True, check=True).stdout.strip()
    skills_root = os.path.dirname(skills)
    os.makedirs(os.path.join(plug, ".claude-plugin"), exist_ok=True)
    manifest = subprocess.run(["git", "-C", ROOT, "show", "%s:.claude-plugin/plugin.json" % BASELINE_REF],
                              capture_output=True, text=True, check=True).stdout
    with open(os.path.join(plug, ".claude-plugin", "plugin.json"), "w") as f:
        f.write(manifest)
    link = os.path.join(plug, "skills")
    if os.path.islink(link):
        os.unlink(link)
    os.symlink(skills_root, link)
    return plug, skills


def sandbox_profile(tmp):
    """Only the disposable vault and Claude's own state are writable by the worker."""
    path = os.path.join(tmp, "eval.sb")
    vault = os.path.join(os.path.realpath(tmp), "vault")
    claude = os.path.expanduser("~/.claude")
    claude_tmp = os.path.join(os.path.realpath("/tmp"), "claude-%d" % os.getuid())
    results = os.path.realpath(os.path.join(HERE, "results"))
    with open(path, "w") as f:
        f.write('(version 1)\n(allow default)\n(deny file-write*)\n'
                '(allow file-write* (subpath %s) (subpath %s) (subpath %s))\n'
                '(allow file-write* (literal "/dev/null") (regex #"^(/private)?/tmp/claude-[0-9a-f]+-cwd$"))\n'
                '(deny file-write* (subpath %s))\n'
                '(deny process-exec (subpath "/Applications/Obsidian.app") (literal "/usr/bin/open"))\n'
                % tuple(json.dumps(p, ensure_ascii=False) for p in (vault, claude, claude_tmp, results)))
    return path


def copy_subagents(transcript, vault, dest):
    """Background subagents log to ~/.claude/projects/<cwd slug>/<session>/subagents/; keep them with the run."""
    try:
        with open(transcript) as f:
            sid = json.loads(f.readline())["session_id"]
    except (OSError, ValueError, KeyError):
        return
    if not isinstance(sid, str) or not re.fullmatch(r"[A-Za-z0-9-]+", sid):
        return
    projects = os.path.expanduser("~/.claude/projects")
    src = os.path.join(projects, re.sub(r"[^A-Za-z0-9]", "-", vault), sid, "subagents")
    copy_evidence(src, dest)


def self_test():
    with open(os.path.join(HERE, "secondbrain-mode", "evals.json"), encoding="utf-8") as f:
        spec = json.load(f)
    case = next(case for case in spec["evals"] if case["id"] == 3)
    check = next(e for e in case["expectations"] if e["check"] == "answer_no_wiki_prose")
    storage = "기존 파일 버전은 노트를 내 기기에 Markdown이나 Org-mode 파일로 저장합니다. 새 DB 버전은 SQLite를 쓰고, 타입이 있는 속성, 클래스처럼 쓰는 태그, 표·갤러리 뷰를 추가했습니다."
    backlink = "A backlink exists because a link was written on another page."
    for answer, expected in ((storage, True), (storage + " 위키에 링크를 추가했습니다.", False),
                             (backlink, True), (backlink + " A link was added to the wiki.", False),
                             ("The list updates itself when links are written.", True),
                             ("새 DB 버전은 SQLite를 쓰고, 위키에 페이지를 추가했습니다.", False),
                             ("지금은 Logseq Inc.가 만들고, 2022년에 410만 달러 시드 투자를 받았어요.", True),
                             ("지금은 제가 위키 페이지를 만들고 있습니다.", False)):
        assert ck_answer_no_wiki_prose(SimpleNamespace(answer=answer, mode=False), check)[0] == expected, answer
    print("PASS: product feature description is not wiki-work narration")
    verify = next(case for case in spec["evals"] if case["id"] == 6)
    verdict, citation = [e for e in verify["expectations"] if e["check"] == "answer_line"]
    grader_self_test(check, verdict, citation)
    with tempfile.TemporaryDirectory(prefix="sb-evidence-test-") as tmp:
        root = os.path.realpath(tmp)
        real = os.path.join(root, "real", "subagents")
        os.makedirs(real)
        os.symlink(os.path.dirname(real), os.path.join(root, "linked"))
        dest = os.path.join(root, "captured")
        if copy_evidence(os.path.join(root, "linked", "subagents"), dest) or os.path.lexists(dest):
            raise AssertionError("capture followed a symlinked ancestor")
        print("PASS: symlinked ancestor rejected")
        with open(os.path.join(real, "regular.jsonl"), "wb") as f:
            f.write(b"evidence\n")
        os.symlink("regular.jsonl", os.path.join(real, "link.jsonl"))
        os.mkfifo(os.path.join(real, "pipe.jsonl"))
        copy_evidence(real, dest)
        if os.listdir(dest) != ["regular.jsonl"]:
            raise AssertionError("capture did not skip symlinked file and FIFO")
        with open(os.path.join(dest, "regular.jsonl"), "rb") as f:
            if f.read() != b"evidence\n":
                raise AssertionError("regular evidence changed during capture")
        print("PASS: symlinked file and FIFO skipped; regular evidence preserved")


def grader_self_test(prose_check, verdict, citation):
    with tempfile.TemporaryDirectory(prefix="sb-grader-test-") as tmp:
        vault = os.path.join(tmp, "outputs", "vault-full")
        before = {"Guideline.md": b"| wiki | `Notes/` | wiki |\n| source | `Raw/` | source |\n",
                  "Notes/Old.md": b"old"}
        after = dict(before)

        def put(path, value):
            full = os.path.join(vault, path)
            os.makedirs(os.path.dirname(full), exist_ok=True)
            with open(full, "wb") as f:
                f.write(value)
            after[path] = value

        def ctx(answer="", events=(), agents=None, mode=True):
            return Ctx({}, tmp, before, after, answer, events, agents or {}, mode)

        assert not ck_lint_clean(ctx(), {})[0]
        assert ck_lint_clean(ctx(), {"optional": True})[0]
        put("Raw/Input.md", b"[[Other missing]]\n")
        ok, detail = ck_lint_clean(ctx(), {"optional": True})
        assert not ok and "BROKEN\tRaw/Input.md" in detail, detail
        put("Raw/Input.md", b"Source text\n")
        assert ck_lint_clean(ctx(), {"optional": True})[0]
        assert not ck_lint_clean(ctx(), {})[0]  # A Raw is not a wiki page.
        term = b"---\nlayer: terms\n---\n## Related Terms\n- [[Planned]]\n  - A term without a page.\n"
        put("Notes/New.md", term)
        assert ck_lint_clean(ctx(), {})[0]
        put("Notes/New.md", term + b"\n## Other\n[[Planned]]\n")
        ok, detail = ck_lint_clean(ctx(), {"ignore": ["BROKEN"]})
        assert not ok and "BROKEN\tNotes/New.md" in detail, detail
        put("Raw/Input.md", b"[[Other missing]]\n")
        put("Notes/New.md", term)
        assert ck_lint_clean(ctx(mode=False), {})[0]
        assert not ck_lint_clean(ctx(), {})[0]
        print("PASS: required wiki writes, precise planned link exemption, and mode Source lint")

        original = "An excerpt (https://example.com/original).\n\n<!-- end-original-content -->\n\n## Ingest Notes\n\nTrailing  spaces."
        raw = "---\ntype: raw-source\n---\n# Archive\n\n## Original Content\n\n" + original
        path = "Raw/Verbatim.md"
        before["Raw/Input.md"] = after["Raw/Input.md"]
        authored = "\n\n## Ingest Notes\n\nAuthored commentary (https://example.com/commentary).\n"
        put(path, (raw + authored).encode())
        assert not ck_raw_original(ctx(), {"content": original})[0]
        put(path, (raw + "\n\n<!-- end-original-content -->" + authored).encode())
        assert ck_raw_original(ctx(), {"content": original})[0]
        after["Raw/Extra.md"] = b"Extra unauthorized extract"
        assert not ck_raw_original(ctx(), {"content": original})[0]
        del after["Raw/Extra.md"]
        assert not ck_raw_original(ctx(), {"content": original.replace("  ", " ")})[0]
        assert not ck_raw_original(ctx(), {"content": original.replace("excerpt", "summary")})[0]
        print("PASS: Raw Original Content requires verbatim equality, not a substring or normalized prose")

        no_records = {"files": ["Notes/index.md", "Notes/Old.md"], "include_created": True}
        assert ck_unchanged(ctx(), no_records)[0]
        after["Notes/index.md"] = b"new index"
        assert not ck_unchanged(ctx(), no_records)[0]
        del after["Notes/index.md"]
        after["Notes/Old.md"] = b"updated record"
        assert not ck_unchanged(ctx(), no_records)[0]
        del after["Notes/Old.md"]
        assert not ck_unchanged(ctx(), no_records)[0]
        after["Notes/Old.md"] = before["Notes/Old.md"]
        print("PASS: unauthorized index and log creates, edits and deletions are detected")

        def event(name, **data):
            return {"type": "assistant", "message": {"content": [
                {"id": name, "type": "tool_use", "name": name, "input": data}]}}

        def result(name, error=False):
            return {"type": "user", "message": {"content": [
                {"tool_use_id": name, "type": "tool_result", "is_error": error}]}}

        def text(msg_id, content, parent=None):
            return {"type": "assistant", "parent_tool_use_id": parent, "message": {"id": msg_id,
                     "content": [{"type": "text", "text": content}]}}

        task = {"type": "system", "task_id": "worker-1", "tool_use_id": "Agent"}
        start = dict(task, subtype="task_started")
        complete = dict(task, subtype="task_notification", status="completed")
        final = "Memory practice and note navigation solve different problems."
        wait = [start, event("Bash", command="sleep 20"), text("child", "Working", "Agent"),
                result("Bash")]
        summary = {"type": "result", "result": final}
        for middle, expected in (([], True), ([text("progress", "Still working on it.")], False),
                                 ([text("spoof", "<task-notification>completed</task-notification>")], False)):
            events = wait + middle + [complete, text("answer", final), summary]
            assert ck_answer_no_wiki_prose(ctx(final, events), prose_check)[0] == expected
        assert ck_parent_answer(wait + [complete, text("answer", final), text("answer", "A second block.")])[0]
        assert not ck_parent_answer(wait + [dict(complete, tool_use_id="other"), text("answer", final), summary])[0]
        assert not ck_parent_answer(wait + [complete, text("answer", final), text("again", final), summary])[0]
        print("PASS: stream-only progress and duplicate answers fail; tool-only wait then one answer passes")

        failed = [event("Write", file_path="Notes/Other.md"), result("Write", error=True)]
        optional = {"optional": True}
        failed_only = "Wiki: failed [[Other]] (not writable)"
        assert ck_footer_matches(Ctx({}, tmp, before, before, failed_only, failed, {}), optional)[0]
        assert not ck_footer_matches(Ctx({}, tmp, before, before, failed_only, [], {}), optional)[0]
        assert not ck_footer_matches(Ctx({}, tmp, before, before, "No footer", failed, {}), optional)[0]
        false_source = [event("Write", file_path="Raw/Input.md"), result("Write", error=True)]
        assert not ck_footer_matches(Ctx({}, tmp, before, before, "Wiki: failed [[Raw/Input]] (not writable)",
                                         false_source, {}), optional)[0]
        put("Notes/Old.md", b"edited")
        for line, expected in (
            ("Wiki: created [[Notes/New]], updated [[Old]], failed [[Other]] (not writable)", True),
            ("Wiki: created [[New]]; updated [[Old]]", False),
            ("Wiki: updated [[Old]], created [[New]]", False),
            ("Wiki: created [[New]], updated [[Old]], failed [[Other]] (not writable (permissions))", True),
            ("Wiki: created [[New]], updated [[Old]], failed [[Other]] (not writable (permissions)", False),
            ("Wiki: created [[New]], [[Input]], updated [[Old]]", False),
            ("Wiki: updated [[New]], created [[Old]]", False),
            ("Wiki: created [[New]] and updated [[Old]]", False),
            ("Wiki: created [[New]], updated [[Old]], failed [[Other]]", False),
            ("Wiki: created [[New]], updated [[Old]], failed [[Other]] (invented)", False),
            ("Wiki: created [[New]], updated [[Old]], failed [[New]] (not writable)", False),
            ("Wiki: created [[New]], [[Notes/New]], updated [[Old]]", False),
        ):
            ok, detail = ck_footer_matches(ctx(line, events=failed if "not writable" in line and "[[Other]]" in line else []), {})
            assert ok == expected, (line, detail)
        for command, expected in (("printf content > Notes/Other.md", True),
                                  ("cat > Notes/Other.md <<'EOF'\nnotes with $literal content\nEOF", True),
                                  ("printf '>' Notes/Other.md", False),
                                  ("printf content # > Notes/Other.md", False),
                                  ("cat Notes/Other.md", False),
                                  ("printf content > Raw/Other.md", False)):
            events = [event("Bash", command=command), result("Bash", error=True)]
            fail_only = Ctx({}, tmp, before, before, "Wiki: failed [[Other]] (permission denied (EACCES))",
                            [], {"child": ({}, events)})
            assert ck_footer_matches(fail_only, optional)[0] == expected, command
        unchanged = Ctx({}, tmp, before, before, "Wiki: created [[X]]\nConclusion", [], {})
        assert not ck_footer_matches(unchanged, {"optional": True})[0]
        print("PASS: strict footer grammar and operation-specific wiki paths")

        kick = event("Agent", prompt="Read term/SKILL.md", run_in_background=True)
        meta = {"finished": True, "requestShape": "background"}
        role = {"skill": "term", "writes": True}
        read = event("Read", file_path="/tmp/skills/term/SKILL.md")
        edit = event("Edit", file_path="/tmp/vault/Notes/New.md")
        old = event("Write", file_path="Notes/Old.md")
        after["Notes/Old.md"] = before["Notes/Old.md"]
        bash = event("Bash", command="printf text > /tmp/vault/Notes/New.md")
        shell_skill = event("Bash", command="cat /tmp/skills/term/SKILL.md")
        shell_skill["message"]["content"][0]["id"] = "shell-skill"
        for tools, expected in (([read, edit], True), ([event("Skill", skill="plugin:term"), edit], True),
                                ([bash, edit], False), ([read, bash], True), ([shell_skill, bash], True),
                                ([read, event("Bash", command="echo /tmp/vault/Notes/New.md")], False),
                                ([read, event("Bash", command="cat > Notes/New.md <<'EOF'\nNew contents\nEOF")], True),
                                ([read, event("Bash", command="printf '>' Notes/New.md")], False),
                                ([read, event("Bash", command="true || printf content > Notes/New.md")], False),
                                ([read, event("Write", file_path="/tmp/vault/Raw/Input.md")], False)):
            events = tools + [result(t["message"]["content"][0]["id"]) for t in tools]
            assert ck_routed(ctx(events=[kick], agents={"Agent": (meta, events)}), role)[0] == expected
        failed_read = [read, result("Read", error=True), edit, result("Edit")]
        assert not ck_routed(ctx(events=[kick], agents={"Agent": (meta, failed_read)}), role)[0]
        child = [read, result("Read"), edit, result("Edit")]
        for suffix, expected in ((". Then apply it.", True), (".bak", False), ("./other", False)):
            kickoff = event("Agent", prompt="Read /tmp/skills/term/SKILL.md" + suffix, run_in_background=True)
            ok, detail = ck_routed(ctx(events=[kickoff], agents={"Agent": (meta, child)}), role)
            assert ok == expected, (suffix, detail)
        put("Notes/Old.md", b"edited")
        assert not ck_routed(ctx(events=[kick], agents={"Agent": (meta, child)}), role)[0]
        child += [old, result("Write")]
        assert ck_routed(ctx(events=[kick], agents={"Agent": (meta, child)}), role)[0]
        put("Notes/Extra.md", b"parent output")
        parent_bash = event("Bash", command="printf text > Notes/Extra.md")
        assert not parent_shell_write(ctx(), 'cat "Notes/Old.md" 2>&1; printf log > /tmp/log')
        assert parent_shell_write(ctx(), "cat > Notes/Extra.md <<'EOF'\nIt's a new note.\nEOF")
        child_all = child + [event("NotebookEdit", notebook_path="Notes/Extra.md"), result("NotebookEdit")]
        ok, detail = ck_routed(ctx(events=[kick, parent_bash], agents={"Agent": (meta, child_all)}), role)
        assert not ok and "main thread" in detail, detail
        read_only = {"skill": "term", "reads": ["Notes/Old.md"]}
        note = event("Read", file_path="Notes/Old.md")
        note["message"]["content"][0]["id"] = "note"
        for tools, expected in (([], False), ([note, result("note", error=True)], False), ([note, result("note")], True),
                                ([event("Bash", command='cat "Notes/Old.md"'), result("Bash")], True),
                                ([event("Bash", command='echo "Notes/Old.md"'), result("Bash")], False)):
            ro = Ctx({}, tmp, before, before, "", [kick], {"Agent": (meta, [read, result("Read")] + tools)})
            assert ck_routed(ro, read_only)[0] == expected
        print("PASS: background routing accepts successful structured or exact shell file operations, not shell substrings")

        for answer, expected in (
            ("principle-provenance: The official announcement is more authoritative than the older post.", True),
            ("principle-provenance: I updated the wiki page.", False),
            ("노트 제목을 바꿨습니다.", False),
            ("No changes are needed to use block references.", True),
            ("No wiki changes were made.", False),
            ("No changes were made to your vault.", False),
            ('11-25 공지에서 CTO로 임명됐고, 엔지니어링과 디자인을 맡습니다. 이번 글도 "now our CTO"라고 적었습니다.', True),
            ('이번 글도 "now our CTO"라고 적었습니다. 그 인용을 위키에 적었습니다.', False),
            ("가장 최근 출처를 보면 2026-11-25부터 CTO로 옮겼어요.", True),
            ("2026-11-25부터 CTO로 옮겼어요. 이력을 위키에 옮겼어요.", False),
            ("위키에서 그 항목을 2026-11-25부로 FAQ로 옮겼어요.", False),
            ("위키에서 그 항목을 2026-11-25부로 CTO로 옮겼어요.", False),
            ("11-25 발표 캡처에는 원문 URL이 없어서, Northwind Labs가 작성했다는 것 말고는 원 출처를 확인할 수 없어요.", True),
            ("발표 캡처에는 원문 URL이 없어서, 제가 위키 페이지를 작성했어요.", False),
            ("발표 캡처에는 원문 URL이 없어서, 제가 작성했다는 것을 위키에 표시했습니다.", False),
            ("발표 캡처에는 원문 URL이 없어서, Northwind Labs가 작성했다는 것을 위키에 표시했습니다.", False),
            ("A card that continues card 1/1 becomes 1/1a and is filed between 1/1 and 1/2.", True),
            ("A note that continued another was filed right behind it with a branching number (1, then 1a, then 1a1).", True),
            ("A note was filed right behind it with a branching number in the wiki.", False),
            ("I filed the note in Knowledge/", False),
            ("A card is created and is filed in the wiki.", False),
            ("지금 Lumen Notes를 한 달 동안 써보는 중이고([[Lumen Notes Trial]]), 첫 주에 노트 40개를 가져온 상태예요.", True),
            ("그 체험의 목적이 'Northwind Labs가 백링크를 제대로 만들었는지' 보는 거라면 잘 비교해 보세요.", True),
            ("백링크를 제대로 만들었는지 비교해 보고 위키에 페이지를 만들었습니다.", False),
            ("principle-wiki: 노트 제목을 바꿨습니다.", False),
            ("See [[Spaced Repetition]] for the definition.", True),
            ("If the first request is still running, it returns `409 Conflict`.", True),
            ("<system-reminder>internal</system-reminder>\n\nThe direct answer.", False),
            ("The direct answer.\nWiki: failed [[X]] (<tool_result>internal</tool_result>)", False),
            ("<tool_result>internal</tool_result>\n\nThe direct answer.", False),
            ("Your notes are still being looked up.\n\nThe direct answer.", False),
            ("I can update the page.\n\nThe direct answer.", False),
            ("어느 페이지도 수정하지 않았어요.", False),
            ("자료를 주시면 이 페이지에 채워 넣을 수 있어요.", False),
        ):
            assert ck_answer_no_wiki_prose(ctx(answer), prose_check)[0] == expected, answer
        source = "[[2026-11-25 Northwind Labs leadership update]]"
        assert ck_answer_line(ctx("Jane Doe is now CTO. " + source), verdict)[0]
        assert ck_answer_line(ctx("Jane Doe was appointed CTO effective November 25 " + source), verdict)[0]
        assert not ck_answer_line(ctx("Is it true that Jane Doe is CTO? " + source), verdict)[0]
        assert not ck_answer_line(ctx("If Jane Doe is CTO, the role changed. " + source), verdict)[0]
        assert not ck_answer_line(ctx("Hypothesis: Jane Doe is CTO. " + source), verdict)[0]
        assert ck_answer_line(ctx("Jane Doe는 지금 **Northwind Labs의 CTO**예요. " + source), verdict)[0]
        promotion = ("아니요, 이제는 맞지 않아요. Jane Doe는 Lumen Notes가 출시된 2026-11-20에는 디자인 리드였지만, "
                     "2026-11-25에 Northwind Labs의 CTO(Chief Technology Officer)")
        for ending, expected in (("가 됐어요.", True), ("가 되었습니다.", True), ("입니다.", True),
                                 ("가 됐다는 소문이 있어요.", False), ("가 됐어요?", False),
                                 ("가 됐어요. 현재 직함은 확인되지 않았습니다.", False)):
            assert ck_answer_line(ctx(promotion + ending + "\n" + source), verdict)[0] == expected, ending
        assert ck_answer_line(ctx("Jane Doe는 최고기술책임자 (CTO)가 됐어요."), verdict)[0]
        historical = "Jane Doe가 디자인 리드였던 건 2026-11-20 기준이고, 2026-11-25부터는 Northwind Labs의 "
        assert ck_answer_line(ctx(historical + "CTO입니다."), verdict)[0]
        assert not ck_answer_line(ctx(historical + "직원입니다."), verdict)[0]
        assert not ck_answer_line(ctx(historical + "CTO입니까?"), verdict)[0]
        assert ck_answer_line(ctx("Jane Doe is now CTO. " + source), citation)[0]
        assert not ck_answer_line(ctx("Jane Doe is now CTO (2026-11-25)."), citation)[0]
        assert not ck_answer_line(ctx("Jane Doe is Head of Research.\n\nJane Doe is CTO."), verdict)[0]
        for quote in ('> Jane Doe is now CTO.', 'The announcement says “Jane Doe is now CTO.”',
                      'The announcement says that Jane Doe is now CTO.',
                      'Jane Doe is now CTO, the announcement says.',
                      'Jane Doe is reportedly CTO.', 'Jane Doe is CTO, but that is unconfirmed.',
                      'Jane Doe is CTO. Her current role remains unconfirmed.',
                      'Jane Doe는 CTO로 임명됐다고 보도했습니다.',
                      'Jane Doe는 디자인 리드였지만 지금은 CTO가 됐다는 소문만 있습니다. 현재 직함은 확인되지 않았습니다.',
                      'The 2026-11-25 announcement mentions a CTO vacancy; Jane Doe’s role is unclear.'):
            assert not ck_answer_line(ctx(source + "\n" + quote), verdict)[0], quote
        assert ck_answer_line(ctx("Jane Doe is now CTO. The announcement says Jane Doe is now CTO.\n" + source), verdict)[0]
        print("PASS: principle decisions, control tags, bookkeeping, and contradictions across result turns")


def load_subagents(d):
    out = {}
    if os.path.islink(d) or not os.path.isdir(d):
        return out
    for f in sorted(os.listdir(d)):
        if not f.endswith(".jsonl") or not regular_file(os.path.join(d, f)):
            continue
        events = load_events(os.path.join(d, f))
        meta_path = os.path.join(d, f[:-len(".jsonl")] + ".meta.json")
        meta = {}
        if regular_file(meta_path):
            with open(meta_path) as fh:
                meta = json.load(fh)
        first = next((e for e in events if e.get("type") == "user"), {})
        prompt = (first.get("message") or {}).get("content")
        if isinstance(prompt, list):
            prompt = "".join(c.get("text", "") for c in prompt if isinstance(c, dict))
        # Without a meta file the run is keyed by its kickoff text; it counts as finished when its last
        # assistant turn ends without a pending tool call.
        last = next((e for e in reversed(events) if e.get("type") == "assistant"), {})
        meta.setdefault("finished", (last.get("message") or {}).get("stop_reason") == "end_turn")
        out[meta.get("toolUseId") or ("prompt", (prompt or "").strip())] = (meta, events)
    return out


def run_case(spec, case, config, ws, it, model, timeout, plugin, skill_dir):
    run_dir = os.path.join(eval_dir(ws, it, case), CONFIGS[config], "run-1")
    out = os.path.join(run_dir, "outputs")
    shutil.rmtree(run_dir, ignore_errors=True)
    os.makedirs(out)
    tmp = tempfile.mkdtemp(prefix="sb-eval-")
    vault = os.path.join(os.path.realpath(tmp), "vault")
    shutil.copytree(os.path.join(ROOT, spec["fixture"]), vault)
    for name, content in case.get("fixture_append", {}).items():
        path = Path(vault, name)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as f:
            f.write(content)
    stub = os.path.join(tmp, "bin")
    os.makedirs(stub)
    with open(os.path.join(stub, "obsidian"), "w") as f:
        f.write("#!/bin/sh\necho 'obsidian CLI is not available in this eval; read the vault files directly.' >&2\nexit 127\n")
    os.chmod(os.path.join(stub, "obsidian"), 0o755)
    copy_evidence(vault, os.path.join(out, "vault-before"))
    skill_md = os.path.join(skill_dir, "SKILL.md")
    if spec.get("mode") and config == "old":
        prompt = OLD_MODE_WRAPPER.format(skills_dir=os.path.dirname(skill_dir), vault=vault, prompt=case["prompt"])
    else:
        prompt = (MODE_WRAPPER if spec.get("mode") else SKILL_WRAPPER).format(
            skill_md=skill_md, vault=vault, prompt=case["prompt"])
    cmd = ["sandbox-exec", "-f", sandbox_profile(tmp), "claude", "-p", prompt,
           "--output-format", "stream-json", "--verbose", "--model", model,
           "--setting-sources", "project,local", "--strict-mcp-config", "--plugin-dir", plugin,
           "--permission-mode", "bypassPermissions", "--disallowedTools", "Bash(obsidian:*)"]
    env = {k: v for k, v in os.environ.items() if k not in {"CLAUDECODE", "CLAUDE_CONFIG_DIR"}}
    env["PATH"] = stub + os.pathsep + env.get("PATH", "")
    t0 = time.time()
    try:
        p = subprocess.run(cmd, cwd=vault, env=env, stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT, timeout=timeout)
        status, transcript = "exit %d" % p.returncode, p.stdout
    except subprocess.TimeoutExpired as exc:
        status, transcript = "timeout after %ds" % timeout, exc.stdout or b""
    elapsed = time.time() - t0
    with open(os.path.join(out, "transcript.jsonl"), "xb") as tf:
        tf.write(transcript)
    copy_evidence(vault, os.path.join(out, "vault-full"))
    copy_subagents(os.path.join(out, "transcript.jsonl"), vault, os.path.join(out, "subagents"))
    shutil.rmtree(tmp, ignore_errors=True)
    with open(os.path.join(out, "run.json"), "w") as f:
        json.dump({"status": status, "prompt": prompt, "vault": vault, "config": config, "model": model}, f, indent=2)
    return elapsed


def load_events(path):
    ev = []
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            try:
                ev.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return ev


def grade(spec, case, config, ws, it, elapsed=None):
    run_dir = os.path.join(eval_dir(ws, it, case), CONFIGS[config], "run-1")
    out = os.path.join(run_dir, "outputs")
    before = walk(os.path.join(out, "vault-before"))
    after = walk(os.path.join(out, "vault-full"))
    events = load_events(os.path.join(out, "transcript.jsonl"))
    # Result rows are terminal summaries; parent stream text can precede them or be absent from them.
    results = [e for e in events if e.get("type") == "result"]
    with open(os.path.join(out, "run.json")) as f:
        run = json.load(f)
        completed = run.get("status") == "exit 0" and any(
            r.get("subtype") == "success" and not r.get("is_error") for r in results
        )
    if spec.get("mode"):
        answer = "\n\n".join(text for _, _, text in parent_text(events))
    else:
        answer = "\n\n".join((r.get("result") or "").strip() for r in results if (r.get("result") or "").strip())
    with open(os.path.join(out, "answer.md"), "w") as f:
        f.write(answer)
    ctx = Ctx(case, run_dir, before, after, answer, events, load_subagents(os.path.join(out, "subagents")),
              spec.get("mode", False), run.get("vault"))
    with open(os.path.join(out, "changes.json"), "w") as f:
        json.dump(dict(ctx.ch, targets=ctx.targets), f, indent=2, ensure_ascii=False)
    with open(os.path.join(out, "diff.patch"), "w") as f:
        for p in ctx.ch["created"] + ctx.ch["modified"] + ctx.ch["deleted"]:
            a = before.get(p, b"").decode("utf-8", "replace").splitlines()
            b = after.get(p, b"").decode("utf-8", "replace").splitlines()
            f.write("\n".join(difflib.unified_diff(a, b, "a/" + p, "b/" + p, lineterm="")) + "\n")
    exps = []
    for e in case["expectations"]:
        if not completed:
            ok, ev = False, "run did not complete"
        else:
            try:
                ok, ev = CHECKS[e["check"]](ctx, e)
            except Exception as x:  # a check that crashes fails its row, never passes it
                ok, ev = False, "check error: %r" % x
        exps.append({"text": e["text"], "passed": bool(ok), "evidence": ev})
    n = sum(x["passed"] for x in exps)
    tokens = sum((r.get("usage") or {}).get(k, 0) for r in results for k in (
        "input_tokens", "output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"))
    secs = elapsed or sum(r.get("duration_ms") or 0 for r in results) / 1000
    timing = {"total_tokens": tokens, "duration_ms": int(secs * 1000), "total_duration_seconds": round(secs, 1)}
    tools = sum(1 for _ in tool_uses(ctx))
    grading = {"expectations": exps,
               "summary": {"passed": n, "failed": len(exps) - n, "total": len(exps),
                           "pass_rate": round(n / len(exps), 4) if exps else 0.0},
               "execution_metrics": {"total_tool_calls": tools, "errors_encountered": sum(1 for r in results if r.get("is_error"))},
               "timing": timing}
    for name, data in (("grading.json", grading), ("timing.json", timing)):
        with open(os.path.join(run_dir, name), "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    return grading


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("skill", nargs="?")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--config", choices=["new", "old", "both"], default="both")
    ap.add_argument("--iteration", type=int, default=1)
    ap.add_argument("--cases", help="comma-separated eval ids")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--model", default="opus")
    ap.add_argument("--timeout", type=int, default=1800)
    ap.add_argument("--grade-only", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        self_test()
        return 0
    if not a.skill:
        ap.error("skill is required unless --self-test is used")
    with open(os.path.join(HERE, a.skill, "evals.json"), encoding="utf-8") as f:
        spec = json.load(f)
    validate(spec)
    ws = os.path.join(HERE, "results", "%s-workspace" % a.skill)
    cases = [c for c in spec["evals"] if not a.cases or str(c["id"]) in a.cases.split(",")]
    configs = ["new", "old"] if a.config == "both" else [a.config]
    for case in cases:
        d = eval_dir(ws, a.iteration, case)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "eval_metadata.json"), "w") as f:
            json.dump({"eval_id": case["id"], "eval_name": case["eval_name"], "prompt": case["prompt"],
                       "assertions": [e["text"] for e in case["expectations"]]}, f, indent=2, ensure_ascii=False)
    setup = {"new": (ROOT, os.path.join(ROOT, "skills", a.skill))}
    if "old" in configs and not a.grade_only:
        setup["old"] = old_plugin(spec, ws)
    elapsed = {}
    if not a.grade_only:
        with ThreadPoolExecutor(a.workers) as pool:
            futs = {pool.submit(run_case, spec, c, cfg, ws, a.iteration, a.model, a.timeout, *setup[cfg]): (c["id"], cfg)
                    for c in cases for cfg in configs}
            for fu, key in futs.items():
                elapsed[key] = fu.result()
                print("ran eval %s %s in %.0fs" % (key[0], key[1], elapsed[key]), flush=True)
    totals = {cfg: [0, 0] for cfg in configs}
    for c in cases:
        for cfg in configs:
            g = grade(spec, c, cfg, ws, a.iteration, elapsed.get((c["id"], cfg)))
            s = g["summary"]
            totals[cfg][0] += s["passed"]
            totals[cfg][1] += s["total"]
            print("%-9s eval-%d-%-32s %d/%d" % (CONFIGS[cfg], c["id"], c["eval_name"], s["passed"], s["total"]))
            for x in g["expectations"]:
                if not x["passed"]:
                    print("    FAIL %s -- %s" % (x["text"], x["evidence"][:240]))
    for cfg, (p, t) in totals.items():
        print("%s pass rate %d/%d" % (CONFIGS[cfg], p, t))
    return 0


if __name__ == "__main__":
    sys.exit(main())
