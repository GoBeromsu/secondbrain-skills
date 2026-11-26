#!/usr/bin/env python3
"""Mechanical eval for the lint skill's scripts against an external fixture vault.

Each case in evals.json lists the findings it expects and the script paths it applies to. For each
path that runs, a case passes when every expected finding is reported and none of its clean files
has a finding; a last check per path fails on any finding no case expects.
Set --fixtures DIR or SB_EVAL_FIXTURES to the fixture root.

  python3 evals/lint/run.py                       # current skill: python and marksman paths
  python3 evals/lint/run.py --cli                 # also obsidian-lint.py (fixture open in Obsidian)
  python3 evals/lint/run.py --skill-dir <old>     # baseline from evals/baseline.sh lint
"""
import argparse
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))


def run(script, args):
    """Findings as {(rule, path, line, text)}, or None and the reason the script did not run."""
    if not os.path.isfile(script):
        return None, "script missing", None
    try:
        p = subprocess.run([sys.executable, script, *args], capture_output=True, text=True, timeout=600)
    except subprocess.TimeoutExpired:
        return None, "timed out", None
    if p.returncode not in (0, 1):
        last = (p.stderr or p.stdout).strip().splitlines()
        return None, "exit %d: %s" % (p.returncode, last[-1] if last else ""), p.returncode
    # A crash or a malformed report must not read as "no findings".
    lines = p.stdout.splitlines()
    rows = [l.split("\t") for l in lines if l and not l.startswith("#")]
    total = [l for l in lines if l.startswith("# violations=")]
    if any(len(r) != 4 or not re.fullmatch(r"[1-9][0-9]*", r[2]) for r in rows):
        return None, "malformed report line", None
    if len(total) != 1 or total[0] != lines[-1] or total[0] != "# violations=%d" % len(rows):
        return None, "report does not end with a matching # violations line", None
    if p.returncode != (1 if rows else 0):
        return None, "exit %d with %d findings" % (p.returncode, len(rows)), None
    found = [(r[0], r[1], int(r[2]), r[3]) for r in rows]
    if len(set(found)) != len(found):
        return None, "duplicate report lines", None
    return set(found), "ok", 0


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--fixtures", metavar="DIR", help="fixture root (default: SB_EVAL_FIXTURES)")
    ap.add_argument("--skill-dir", default=os.path.join(ROOT, "skills", "lint"))
    ap.add_argument("--cli", action="store_true", help="also run obsidian-lint.py; Obsidian must already have the fixture open")
    ap.add_argument("--json", help="write per-case results to this file")
    a = ap.parse_args(argv)
    fixture_root = a.fixtures or os.environ.get("SB_EVAL_FIXTURES")
    if not fixture_root:
        ap.error("set --fixtures DIR or SB_EVAL_FIXTURES to the fixture root")
    fixture_root = os.path.abspath(os.path.expanduser(fixture_root))
    with open(os.path.join(HERE, "evals.json"), encoding="utf-8") as f:
        spec = json.load(f)
    vault = os.path.join(fixture_root, spec["fixture"])
    guideline_path = os.path.join(fixture_root, spec["policy"]["source"])
    if not os.path.isfile(guideline_path):
        ap.error(f"fixture guideline is missing: {guideline_path}")
    with open(guideline_path, encoding="utf-8") as f:
        guideline = f.read()
    # Read fixture-specific role and type declarations from its guideline.
    wiki = re.findall(r"^\| wiki \| `([^`]+?)/?` \|", guideline, re.M)
    section = re.search(r"^Wiki subfolders:.*?(?P<folders>`[^`]+`(?:, `[^`]+`)*(?: and `[^`]+`)?) for Entities\b",
                        guideline, re.M)
    subfolders = re.findall(r"`([^`]+?)/?`", section["folders"]) if section else []
    entity_folders = [f"{w}/{d}" for w in wiki for d in subfolders]
    life = re.search(r"^Only lifecycle notes carry `status`: (.*)$", guideline, re.M)
    book_types = re.findall(r"^Book Entities of `type: ([^`]+)`", guideline, re.M)
    product_types = re.findall(r"^Product Entities of `type: ([^`]+)`", guideline, re.M)
    declared = {"wiki": wiki, "entity_folders": entity_folders, "book_types": book_types,
                "product_types": product_types,
                "lifecycle": re.findall(r"`type: ([^`]+)`", life[1]) if life else []}
    if any(sorted(values) != sorted(spec["policy"][key]) for key, values in declared.items()):
        sys.exit("evals.json policy %s is not what %s declares: %s" % (
            spec["policy"], spec["policy"]["source"], declared))
    scripts = os.path.join(a.skill_dir, "scripts")
    policy = [x for w in wiki for x in ("--wiki", w)]
    policy += [x for d in entity_folders for x in ("--entity-folder", d)]
    policy += [x for t in book_types for x in ("--book-type", t)]
    policy += [x for t in product_types for x in ("--product-type", t)]
    policy += ["--lifecycle", ",".join(declared["lifecycle"])]

    python = run(os.path.join(scripts, "link-lint.py"), ["--vault", vault, "--checks", "all", *policy])
    if python[0] is None and python[2] == 2 and os.path.realpath(a.skill_dir) != os.path.realpath(os.path.join(ROOT, "skills", "lint")):
        # A release without the policy checks (0.28.1) still gets credit for its link-form rules.
        python = run(os.path.join(scripts, "link-lint.py"), ["--vault", vault])
    runs = {
        "python": python,
        "marksman": run(os.path.join(scripts, "marksman-lint.py"), ["--vault", vault]),
    }
    if a.cli:
        runs["obsidian-cli"] = run(os.path.join(scripts, "obsidian-lint.py"), ["--vault", vault, *policy])

    cases = [c for c in spec["evals"] if "paths" in c]
    # A misspelt path would make a clean-file or finding check pass vacuously.
    named = {x[1] for c in cases for x in c["findings"]} | {p for c in cases for p in c.get("clean_files", [])}
    absent = sorted(p for p in named if not os.path.isfile(os.path.join(vault, p)))
    if absent:
        sys.exit("evals.json names files missing from the fixture: " + ", ".join(absent))
    if any(not c["findings"] and not c.get("clean_files") for c in cases):
        sys.exit("evals.json has a case with neither findings nor clean_files")
    results = []

    def record(path, eid, name, missing, unexpected):
        ok = not missing and not unexpected
        results.append({"path": path, "eval_id": eid, "eval_name": name, "passed": ok,
                        "missing": missing, "unexpected": unexpected})
        print("%-13s %-28s %s" % (path, name, "PASS" if ok else "FAIL"))
        for m in missing:
            print("    missing     " + "\t".join(map(str, m)))
        for m in unexpected:
            print("    unexpected  " + "\t".join(map(str, m)))

    for path, (got, why, _) in runs.items():
        mine = [c for c in cases if path in c["paths"]]
        if got is None:
            print("%-13s not run: %s" % (path, why))
            for c in mine:
                record(path, c["id"], c["eval_name"], [tuple(x) for x in c["findings"]] or [("not run", why)], [])
            record(path, 0, "no-unexpected-findings", [("not run", why)], [])
            continue
        for c in mine:
            want = {tuple(x) for x in c["findings"]}
            clean = set(c.get("clean_files", []))
            record(path, c["id"], c["eval_name"], sorted(want - got), sorted(r for r in got if r[1] in clean))
        expected = {tuple(x) for c in mine for x in c["findings"]}
        record(path, 0, "no-unexpected-findings", [], sorted(got - expected))

    passed = sum(r["passed"] for r in results)
    print("pass rate %d/%d" % (passed, len(results)))
    if a.json:
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump({"skill_dir": os.path.abspath(a.skill_dir), "passed": passed, "total": len(results),
                       "results": results}, f, indent=2, ensure_ascii=False)
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
