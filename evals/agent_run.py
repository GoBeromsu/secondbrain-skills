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
import shutil
import stat
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor

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


def ignore_evidence_files(directory, names):
    ignored = []
    for name in names:
        mode = os.lstat(os.path.join(directory, name)).st_mode
        if name == ".obsidian" or not (stat.S_ISREG(mode) or stat.S_ISDIR(mode) or stat.S_ISLNK(mode)):
            ignored.append(name)
    return ignored


def copy_evidence(src, dest):
    if not os.path.islink(src) and os.path.isdir(src):
        shutil.copytree(src, dest, symlinks=True, ignore=ignore_evidence_files)


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
    def __init__(self, case, run_dir, before, after, answer, events, subagents):
        self.case, self.run_dir, self.before, self.after = case, run_dir, before, after
        self.answer, self.events, self.subagents = answer, events, subagents
        self.ch = changes(before, after)
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
            wiki = self.case.get("wiki", "Knowledge/")
            return [p for p in self.ch["created"] + self.ch["modified"] if p.startswith(wiki) and p.endswith(".md")]
        out = []
        for s in spec:
            p = self.path(s)
            if p is None:
                continue
            out += sorted(x for x in set(self.before) | set(self.after) if fnmatch.fnmatch(x, p)) or [p]
        return out


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
    files = ctx.files(e.get("files", "@changed_wiki"))
    if not files:  # a run that wrote no wiki page has nothing to violate; a required page is its own row
        return True, "no wiki page written"
    vault = os.path.join(ctx.run_dir, "outputs", "vault-full")
    p = subprocess.run([sys.executable, LINK_LINT, "--vault", vault, "--checks", "all", "--wiki",
                        ctx.case.get("wiki", "Knowledge/").strip("/"), "--lifecycle", "project,task",
                        "--scope", *files], capture_output=True, text=True)
    ignore = set(e.get("ignore", []))
    rows = [l for l in p.stdout.splitlines() if l and not l.startswith("#") and l.split("\t")[0] not in ignore]
    if p.returncode not in (0, 1):
        return False, "link-lint exit %d: %s" % (p.returncode, p.stderr.strip()[-200:])
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
    bad = [p for p in ctx.files(e["files"]) if p in ctx.before and ctx.before.get(p) != ctx.after.get(p)]
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
    """{'created': [...], 'updated': [...], 'failed': [...]} from `Wiki: created [[X]], updated [[Y]], failed ...`."""
    out, verb = {"created": [], "updated": [], "failed": []}, None
    for m in re.finditer(r"\b(created|updated|failed)\b|\[\[([^\]|#]+)(?:[^\]]*)\]\]", line):
        if m.group(1):
            verb = m.group(1)
        elif verb:
            out[verb].append(m.group(2).strip())
    return out


def ck_answer_line(ctx, e):
    lines = answer_lines(ctx)
    pool = lines[-1:] if e.get("position") == "last" else lines
    hit = [l for l in pool if re.search(e["regex"], l)]
    return bool(hit), hit[0] if hit else "last line: %r" % (lines[-1] if lines else "")


def ck_footer_matches(ctx, e):
    """The final line is the only Wiki line, and its created/updated pages are exactly the wiki writes."""
    lines = answer_lines(ctx)
    f = footer(ctx)
    wiki = ctx.case.get("wiki", "Knowledge/")
    written = {"created": {os.path.basename(p)[:-3] for p in ctx.ch["created"] if p.endswith(".md")},
               "updated": {os.path.basename(p)[:-3] for p in ctx.ch["modified"] if p.endswith(".md")}}
    wiki_writes = {os.path.basename(p)[:-3] for p in ctx.ch["created"] + ctx.ch["modified"] if p.startswith(wiki)}
    if f is None:
        ok = not wiki_writes and e.get("optional")
        return bool(ok), "no final Wiki line; wiki writes %s" % sorted(wiki_writes)
    if sum(1 for l in lines if FOOTER.match(l)) != 1:
        return False, "more than one Wiki line"
    cl = footer_clauses(f)
    bad = []
    for verb in ("created", "updated"):
        for name in cl[verb]:
            if name not in written[verb]:
                bad.append("%s [[%s]] is not a %s file" % (verb, name, verb))
    named = set(cl["created"]) | set(cl["updated"])
    for name in sorted(wiki_writes - named):
        bad.append("wiki page [[%s]] written but not named" % name)
    for verb, names in e.get("require", {}).items():
        for rx in names:
            if not any(re.search(rx, n) for n in cl[verb]):
                bad.append("no %s page matching /%s/" % (verb, rx))
    return not bad, "; ".join(bad) or f[:200]


def ck_modified(ctx, e):
    p = ctx.path(e["file"])
    return p in ctx.ch["modified"], "%s %s" % (p, "modified" if p in ctx.ch["modified"] else "not modified")


def ck_answer_no_wiki_line(ctx, e):
    hit = [l for l in answer_lines(ctx) if FOOTER.match(l)]
    return not hit, ("has %r" % hit[0]) if hit else "no Wiki line"


PRINCIPLE_CITE = re.compile(r"^\W*(\*\*)?`?principle-[a-z-]+")


def ck_answer_no_wiki_prose(ctx, e):
    """Every line but the parsed footer is checked; a line that cites a principle leaf by name may say what it changed."""
    lines = answer_lines(ctx)
    if footer(ctx) is not None:
        lines = lines[:-1]
    pat = re.compile("|".join(e["forbid"]), re.I)
    hits = [l for l in lines if pat.search(l) and not PRINCIPLE_CITE.match(l)]
    return not hits, ("wiki prose: %r" % hits[0][:160]) if hits else "no wiki-work prose in the answer body"


def tool_uses(ctx, events=None):
    for ev in ctx.events if events is None else events:
        msg = ev.get("message") or {}
        if ev.get("type") != "assistant" or not isinstance(msg.get("content"), list):
            continue
        for c in msg["content"]:
            if c.get("type") == "tool_use":
                yield ev.get("parent_tool_use_id"), c


WRITE_TOOLS = ("Write", "Edit", "MultiEdit", "NotebookEdit")


def ck_routed(ctx, e):
    """A top-level background subagent got a kickoff naming <skill>/SKILL.md, opened that file, finished,
    and did the case's writes; the main thread wrote nothing into the wiki itself."""
    pat = re.compile(r"(^|[/\s\"'])%s/SKILL\.md" % re.escape(e["skill"]))
    kick = [c for parent, c in tool_uses(ctx) if parent is None and c.get("name") in ("Task", "Agent")
            and pat.search(json.dumps(c.get("input", {}), ensure_ascii=False))]
    if not kick:
        starts = [c.get("input", {}).get("description") for _, c in tool_uses(ctx) if c.get("name") in ("Task", "Agent")]
        return False, "no subagent kickoff names %s/SKILL.md; subagents: %s" % (e["skill"], starts)
    wiki = ctx.case.get("wiki", "Knowledge/")
    main_writes = [c["input"].get("file_path", "") for parent, c in tool_uses(ctx)
                   if parent is None and c.get("name") in WRITE_TOOLS and "/" + wiki in c["input"].get("file_path", "")]
    main_bash = [c["input"].get("command", "")[:60] for parent, c in tool_uses(ctx) if parent is None and c.get("name") == "Bash"
                 and "/" + wiki in c["input"].get("command", "") and re.search(r"(>|\bmv\b|\bcp\b|write|replace)", c["input"].get("command", ""))]
    if main_writes or main_bash:
        return False, "main thread wrote to the wiki itself: %s" % (main_writes + main_bash)[:3]
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
        uses = [u for _, u in tool_uses(ctx, events)]
        opened = any(pat.search(json.dumps(u.get("input", {}))) for u in uses
                     if u.get("name") in ("Read", "Bash", "Skill"))
        wrote = any(u.get("name") in WRITE_TOOLS for u in uses) or any(
            u.get("name") == "Bash" and "/" + wiki in u["input"].get("command", "") for u in uses)
        need_write = e.get("writes", False)
        if meta.get("finished") and opened and (wrote or not need_write):
            return True, "background subagent %r read %s/SKILL.md%s" % (
                c["input"].get("description", "")[:60], e["skill"], " and wrote" if wrote else "")
    return False, "kickoff found but no finished background subagent that opened %s/SKILL.md%s" % (
        e["skill"], " and wrote" if e.get("writes") else "")


CHECKS = {
    "exists": ck_exists, "frontmatter": ck_frontmatter, "headings": ck_headings, "lint_clean": ck_lint_clean,
    "no_new_under": ck_no_new_under, "changed_only_within": ck_changed_only_within, "unchanged": ck_unchanged,
    "no_changes_under": ck_no_changes_under, "records_updated": ck_records_updated,
    "first_mention_link": ck_first_mention_link, "section_line": ck_section_line,
    "moved_verbatim": ck_moved_verbatim, "contains": ck_contains, "count_created": ck_count_created,
    "links_new_page": ck_links_new_page, "answer_line": ck_answer_line, "answer_no_wiki_line": ck_answer_no_wiki_line,
    "answer_no_wiki_prose": ck_answer_no_wiki_prose, "routed": ck_routed, "modified": ck_modified,
    "footer_matches": ck_footer_matches,
}


def validate(spec):
    for case in spec["evals"]:
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
    """macOS sandbox: no writes under ~/Documents (the owner's vaults and this repo) except evals/results,
    and no way to launch Obsidian. Claude's own state (~/.claude) and the temp vault stay writable."""
    path = os.path.join(tmp, "eval.sb")
    with open(path, "w") as f:
        f.write('(version 1)\n(allow default)\n(deny file-write* (subpath "%s"))\n'
                '(allow file-write* (subpath "%s"))\n'
                '(deny process-exec (subpath "/Applications/Obsidian.app") (literal "/usr/bin/open"))\n'
                % (os.path.expanduser("~/Documents"), os.path.join(HERE, "results")))
    return path


def copy_subagents(transcript, vault, dest):
    """Background subagents log to ~/.claude/projects/<cwd slug>/<session>/subagents/; keep them with the run."""
    try:
        with open(transcript) as f:
            sid = json.loads(f.readline())["session_id"]
    except (OSError, ValueError, KeyError):
        return
    roots = [os.environ.get("CLAUDE_CONFIG_DIR"), os.path.expanduser("~/.claude")]
    for root in filter(None, roots):
        src = os.path.join(root, "projects", re.sub(r"[^A-Za-z0-9]", "-", vault), sid, "subagents")
        if not os.path.islink(src) and os.path.isdir(src):
            copy_evidence(src, dest)
            return


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
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
    env["PATH"] = stub + os.pathsep + env.get("PATH", "")
    t0 = time.time()
    with open(os.path.join(out, "transcript.jsonl"), "w") as tf:
        try:
            p = subprocess.run(cmd, cwd=vault, env=env, stdout=tf, stderr=subprocess.STDOUT, timeout=timeout)
            status = "exit %d" % p.returncode
        except subprocess.TimeoutExpired:
            status = "timeout after %ds" % timeout
    elapsed = time.time() - t0
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
    # A background subagent's completion wakes the main thread for another turn, so the user sees every
    # top-level result in order; the footer is in the last one.
    results = [e for e in events if e.get("type") == "result"]
    with open(os.path.join(out, "run.json")) as f:
        completed = json.load(f).get("status") == "exit 0" and any(
            r.get("subtype") == "success" and not r.get("is_error") for r in results
        )
    answer = "\n\n".join((r.get("result") or "").strip() for r in results if (r.get("result") or "").strip())
    with open(os.path.join(out, "answer.md"), "w") as f:
        f.write(answer)
    ctx = Ctx(case, run_dir, before, after, answer, events, load_subagents(os.path.join(out, "subagents")))
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
    ap.add_argument("skill")
    ap.add_argument("--config", choices=["new", "old", "both"], default="both")
    ap.add_argument("--iteration", type=int, default=1)
    ap.add_argument("--cases", help="comma-separated eval ids")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--model", default="opus")
    ap.add_argument("--timeout", type=int, default=1800)
    ap.add_argument("--grade-only", action="store_true")
    a = ap.parse_args(argv)
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
    if "old" in configs:
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
