#!/usr/bin/env python3
"""Mechanical checks for the secondbrain-skills plugin. Standard library only.

Run from anywhere: `python3 scripts/validate.py`. Exits non-zero on any failure.
It answers one question each and judges nothing a skill should judge:

  manifests   every manifest parses, names agree, every version agrees
  skills      every skills/<name>/SKILL.md has valid frontmatter whose name is the folder
  links       every relative link in the READMEs resolves, and both READMEs list every package
  assets      every image file is recorded in assets/asset-ledger.json and vice versa
  icon        the plugin icon is a square PNG of 512-2048 px under 2 MB
  scripts     every bundled Python script compiles

Set SB_EVAL_FIXTURES to the external fixture root to also check that
skills/lint/scripts/link-lint.py reproduces <root>/lint-links/expected.tsv.
"""
import json
import os
import py_compile
import re
import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFESTS = [".claude-plugin/plugin.json", ".claude-plugin/marketplace.json", ".codex-plugin/plugin.json", "plugin.json", ".agents/plugins/marketplace.json"]
VERSIONED = MANIFESTS[:4]
NAME = "secondbrain-skills"
NAME_RX = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
IMAGE_EXT = {".svg", ".png", ".jpg", ".jpeg", ".gif", ".webp"}
READMES = ["README.md", "README.ko.md", "CODE_OF_CONDUCT.md", "CONTRIBUTING.md", "SECURITY.md", "ACKNOWLEDGEMENTS.md"]
ICON = "assets/icon.png"

errors: list[str] = []


def fail(check, msg):
    errors.append(f"[{check}] {msg}")


def check_manifests():
    data = {}
    for rel in MANIFESTS:
        try:
            data[rel] = json.loads((ROOT / rel).read_text())
        except FileNotFoundError:
            fail("manifests", f"{rel}: missing")
        except json.JSONDecodeError as e:
            fail("manifests", f"{rel}: invalid JSON ({e})")
    for rel, m in data.items():
        if m.get("name") != NAME:
            fail("manifests", f"{rel}: name is {m.get('name')!r}, expected {NAME!r}")
        for p in m.get("plugins", []):
            if p.get("name") != NAME:
                fail("manifests", f"{rel}: plugin entry name is {p.get('name')!r}")
    versions = {}
    for rel in VERSIONED:
        m = data.get(rel)
        if not m:
            continue
        versions[rel] = m.get("version")
        if rel.endswith("marketplace.json"):
            for p in m.get("plugins", []):
                versions[f"{rel} plugins[{p.get('name')}]"] = p.get("version")
    if len(set(versions.values())) > 1:
        fail("manifests", "versions disagree: " + ", ".join(f"{k}={v}" for k, v in versions.items()))
    if None in versions.values():
        fail("manifests", "a manifest has no version")
    codex = data.get(".codex-plugin/plugin.json", {})
    if codex and not (ROOT / codex.get("skills", "./skills/")).is_dir():
        fail("manifests", ".codex-plugin/plugin.json: skills path does not exist")
    return next(iter(versions.values()), None)


def frontmatter(text):
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end < 0:
        return None
    out = {}
    for line in text[4:end].splitlines():
        m = re.match(r"^([A-Za-z_-]+):\s*(.*)$", line)
        if m:
            v = m.group(2).strip()
            if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
                v = v[1:-1]
            out[m.group(1)] = v
    return out


def check_skills():
    root = ROOT / "skills"
    names = []
    for entry in sorted(root.iterdir()):
        if entry.name.startswith("."):
            continue
        if not entry.is_dir():
            fail("skills", f"skills/{entry.name}: only package folders belong in skills/")
            continue
        skill = entry / "SKILL.md"
        if not skill.is_file():
            fail("skills", f"skills/{entry.name}: no SKILL.md")
            continue
        fm = frontmatter(skill.read_text())
        if fm is None:
            fail("skills", f"skills/{entry.name}/SKILL.md: no YAML frontmatter")
            continue
        name, desc = fm.get("name", ""), fm.get("description", "")
        if name != entry.name:
            fail("skills", f"skills/{entry.name}/SKILL.md: name {name!r} does not match its folder")
        if not NAME_RX.match(name) or len(name) > 64:
            fail("skills", f"skills/{entry.name}/SKILL.md: name must be lowercase-hyphenated, at most 64 characters")
        if not desc:
            fail("skills", f"skills/{entry.name}/SKILL.md: empty description")
        elif len(desc) > 1024:
            fail("skills", f"skills/{entry.name}/SKILL.md: description is {len(desc)} characters (max 1024)")
        if "<" in desc and ">" in desc and re.search(r"<[a-zA-Z/][^>]*>", desc):
            fail("skills", f"skills/{entry.name}/SKILL.md: description contains an XML/HTML tag")
        names.append(name)
    if not names:
        fail("skills", "no packages found under skills/")
    return names


def tracked_files():
    try:
        out = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
        return {line for line in out.splitlines() if line}
    except (OSError, subprocess.CalledProcessError):
        return {str(p.relative_to(ROOT)) for p in ROOT.rglob("*") if p.is_file() and ".git" not in p.parts}


LINK_RX = re.compile(r"""(?:\]\(|src=["']|href=["'])([^)"'\s#]+)""")


def check_links(files):
    for rel in READMES:
        path = ROOT / rel
        if not path.is_file():
            fail("links", f"{rel}: missing")
            continue
        text = re.sub(r"```.*?```", "", path.read_text(), flags=re.S)
        for target in LINK_RX.findall(text):
            if re.match(r"^[a-z]+:", target) or target.startswith("//"):
                continue
            resolved = (path.parent / target).resolve()
            try:
                key = str(resolved.relative_to(ROOT))
            except ValueError:
                fail("links", f"{rel}: {target} points outside the repository")
                continue
            if key not in files and not resolved.is_dir():
                fail("links", f"{rel}: {target} does not resolve to a tracked file")


def check_readme_packages(names):
    for rel in READMES[:2]:
        text = (ROOT / rel).read_text() if (ROOT / rel).is_file() else ""
        for name in names:
            if f"(skills/{name}/SKILL.md)" not in text:
                fail("links", f"{rel}: package {name} is not listed (expected a link to skills/{name}/SKILL.md)")
        for listed in sorted(set(re.findall(r"\(skills/([a-z0-9-]+)/SKILL\.md\)", text)) - set(names)):
            fail("links", f"{rel}: lists {listed}, which is not a package")


def check_assets(files):
    ledger_path = ROOT / "assets/asset-ledger.json"
    try:
        ledger = json.loads(ledger_path.read_text())
    except (FileNotFoundError, json.JSONDecodeError) as e:
        fail("assets", f"assets/asset-ledger.json: {e}")
        return
    listed = {a["path"] for a in ledger.get("assets", [])}
    images = {f for f in files if Path(f).suffix.lower() in IMAGE_EXT and not f.startswith(("skills/", "evals/"))}
    for f in sorted(images - listed):
        fail("assets", f"{f}: image is not recorded in assets/asset-ledger.json")
    for f in sorted(listed - files):
        fail("assets", f"{f}: listed in the ledger but not in the repository")
    for f in sorted(listed & files):
        if f.endswith(".svg"):
            svg = (ROOT / f).read_text()
            if re.search(r"<script|<image|xlink:href=|href=\"http|@import|<foreignObject", svg):
                fail("assets", f"{f}: SVG must not embed scripts, raster images or external references")


def check_icon():
    path = ROOT / ICON
    if not path.is_file():
        fail("icon", f"{ICON}: missing")
        return
    raw = path.read_bytes()
    if raw[:8] != b"\x89PNG\r\n\x1a\n":
        fail("icon", f"{ICON}: not a PNG")
        return
    w, h = struct.unpack(">II", raw[16:24])
    if w != h or not 512 <= w <= 2048:
        fail("icon", f"{ICON}: {w}x{h}, needs a square of 512-2048 px")
    if len(raw) >= 2 * 1024 * 1024:
        fail("icon", f"{ICON}: {len(raw)} bytes, needs under 2 MB")


def check_scripts():
    for py in sorted((ROOT / "skills").glob("*/scripts/*.py")) + sorted((ROOT / "scripts").rglob("*.py")):
        try:
            py_compile.compile(str(py), doraise=True, cfile=None)
        except py_compile.PyCompileError as e:
            fail("scripts", f"{py.relative_to(ROOT)}: {e.msg}")


def check_lint_eval(fixture_root):
    script = ROOT / "skills/lint/scripts/link-lint.py"
    case = Path(fixture_root).expanduser().resolve() / "lint-links"
    expected = case / "expected.tsv"
    if not (case / "vault").is_dir() or not expected.is_file():
        fail("lint-eval", f"SB_EVAL_FIXTURES must provide {case / 'vault'} and {expected}")
        return
    run = subprocess.run([sys.executable, str(script), "--vault", str(case / "vault")], capture_output=True, text=True)
    if run.returncode not in (0, 1) or run.stdout != expected.read_text():
        fail("lint-eval", f"link-lint.py did not reproduce {expected}")


def main():
    files = tracked_files()
    version = check_manifests()
    names = check_skills()
    check_links(files)
    check_readme_packages(names)
    check_assets(files)
    check_icon()
    check_scripts()
    fixture_root = os.environ.get("SB_EVAL_FIXTURES")
    if fixture_root:
        check_lint_eval(fixture_root)
    if errors:
        print(f"FAIL: {len(errors)} problem(s)")
        for e in errors:
            print("  " + e)
        return 1
    checks = "manifests, links, assets, icon, scripts"
    if fixture_root:
        checks += ", lint-eval"
    print(f"OK: {NAME} {version}, {len(names)} packages, {checks} all pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
