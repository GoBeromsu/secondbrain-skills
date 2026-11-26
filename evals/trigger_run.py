#!/usr/bin/env python3
"""Plugin-level trigger eval: which skill does Claude invoke when the whole plugin is loaded?

skill-creator's run_eval.py tests one description alone. This runner loads the real plugin
(`--plugin-dir`, user settings, plugins and MCP servers off) in a temp copy of the fixture vault and
records the skills each query invokes, so siblings compete as they do in use. It checks:

- each skill's `trigger_evals`: a should-trigger query invokes that skill in at least half the runs,
  a should-not-trigger query in fewer than half;
- `principle-*` principles and `secondbrain-mode` (`disable-model-invocation: true`) are invoked 0 times.

Set --fixtures DIR or SB_EVAL_FIXTURES to the fixture root.

  python3 evals/trigger_run.py                         # term, concept, entity, secondbrain-mode
  python3 evals/trigger_run.py --skills term --runs 1
"""
import argparse
import json
import os
import re
import select
import shutil
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PLUGIN = "secondbrain-skills"
SKILL_MD = re.compile(r"skills/([a-z0-9-]+)/SKILL\.md")


def invoked(query, model, timeout, plugin, fixture, full=False):
    """{'first': skill the model reached for first or None, 'skill_calls': every Skill tool call in the run
    (main thread and subagents), 'leaf_reads': principle SKILL.md files opened by path, 'status': ...}.

    Without `full` the run stops at the first invocation, as skill-creator's run_eval.py does. With `full`
    it runs to its final result, so later invocations (after a skill is active, inside subagents) count too.
    """
    sys.path.insert(0, HERE)
    from agent_run import copy_subagents, load_subagents, sandbox_profile
    tmp = tempfile.mkdtemp(prefix="sb-trig-")
    vault = os.path.join(os.path.realpath(tmp), "vault")
    shutil.copytree(fixture, vault)
    cmd = ["sandbox-exec", "-f", sandbox_profile(tmp), "claude", "-p", query, "--output-format", "stream-json",
           "--verbose", "--model", model, "--setting-sources", "project,local", "--strict-mcp-config",
           "--plugin-dir", plugin, "--disallowedTools", "Bash(obsidian:*)"]
    if full:
        cmd += ["--permission-mode", "bypassPermissions"]
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
    log = os.path.join(tmp, "transcript.jsonl")
    out = {"first": None, "skill_calls": [], "leaf_reads": [], "status": "timeout"}

    def scan(c):
        inp = c.get("input") or {}
        if c.get("name") == "Skill":
            name = str(inp.get("skill", "")).split(":")[-1]
            out["skill_calls"].append(name)
            return name
        m = SKILL_MD.search(json.dumps(inp))
        if m and c.get("name") in ("Read", "Bash"):
            if m.group(1).startswith("principle-"):
                out["leaf_reads"].append(m.group(1))
            return m.group(1) if c.get("name") == "Read" else None
        return None

    p = subprocess.Popen(cmd, cwd=vault, env=env, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    buf, t0, top_started = b"", time.time(), False
    try:
        with open(log, "wb") as lf:
            while time.time() - t0 < timeout:
                if p.poll() is not None:
                    buf += p.stdout.read() or b""
                elif select.select([p.stdout], [], [], 1.0)[0]:
                    chunk = os.read(p.stdout.fileno(), 65536)
                    if not chunk:
                        break
                    buf += chunk
                else:
                    continue
                *lines, buf = buf.split(b"\n")
                for line in lines:
                    lf.write(line + b"\n")
                    try:
                        ev = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if ev.get("type") == "result":
                        out["status"] = "error" if ev.get("is_error") else "ok"
                        if not full or p.poll() is not None:
                            raise StopIteration
                    if ev.get("type") != "assistant":
                        continue
                    for c in (ev.get("message") or {}).get("content") or []:
                        if c.get("type") != "tool_use":
                            continue
                        name = scan(c)
                        if ev.get("parent_tool_use_id") is None and not top_started:
                            top_started = True  # only the main thread's first action decides `first`
                            out["first"] = name
                            if not full:
                                out["status"] = "ok"
                                raise StopIteration
                if p.poll() is not None and not buf:
                    out["status"] = "ok" if out["status"] == "ok" else "no result"
                    break
    except StopIteration:
        pass
    finally:
        if full and p.poll() is None and out["status"] == "ok":
            try:
                p.wait(timeout=max(1, timeout - (time.time() - t0)))
            except subprocess.TimeoutExpired:
                pass
        if p.poll() is None:
            p.kill()
            p.wait()
        if full:
            copy_subagents(log, vault, os.path.join(tmp, "subagents"))
            for meta, events in load_subagents(os.path.join(tmp, "subagents")).values():
                for ev in events:
                    for c in ((ev.get("message") or {}).get("content") or []) if ev.get("type") == "assistant" else []:
                        if isinstance(c, dict) and c.get("type") == "tool_use":
                            scan(c)
        shutil.rmtree(tmp, ignore_errors=True)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--fixtures", metavar="DIR", help="fixture root (default: SB_EVAL_FIXTURES)")
    ap.add_argument("--skills", default="term,concept,entity,secondbrain-mode")
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--workers", type=int, default=10)
    ap.add_argument("--model", default="opus")
    ap.add_argument("--timeout", type=int, default=90)
    ap.add_argument("--plugin", default=ROOT)
    ap.add_argument("--full", action="store_true", help="run each query to its final result and scan every Skill call")
    ap.add_argument("--json", default=None)
    a = ap.parse_args(argv)
    fixture_root = a.fixtures or os.environ.get("SB_EVAL_FIXTURES")
    if not fixture_root:
        ap.error("set --fixtures DIR or SB_EVAL_FIXTURES to the fixture root")
    fixture = os.path.abspath(os.path.join(os.path.expanduser(fixture_root), "fixture-vault"))
    if not os.path.isdir(fixture):
        ap.error(f"fixture vault is not a directory: {fixture}")
    items = []
    for s in a.skills.split(","):
        with open(os.path.join(HERE, s, "evals.json"), encoding="utf-8") as f:
            # A typed slash command is the user invoking the skill, not the model choosing it.
            items += [dict(q, owner=s) for q in json.load(f)["trigger_evals"] if not q["query"].startswith("/")]
    runs = {}
    with ThreadPoolExecutor(a.workers) as pool:
        futs = {pool.submit(invoked, q["query"], a.model, a.timeout, a.plugin, fixture, a.full): i
                for i, q in enumerate(items) for _ in range(a.runs)}
        for fu in as_completed(futs):
            runs.setdefault(futs[fu], []).append(fu.result())
    rows, per, leaked, errors = [], {}, [], []
    for i, q in enumerate(items):
        got = runs[i]
        firsts = [r["first"] for r in got]
        rate = sum(q["owner"] == f for f in firsts) / len(got)
        ok = rate >= 0.5 if q["should_trigger"] else rate < 0.5
        if q["owner"] == "secondbrain-mode":
            ok = rate == 0  # disable-model-invocation: the model never invokes it, whatever the query
        bad = [s for r in got for s in r["skill_calls"] if s.startswith("principle-") or s == "secondbrain-mode"]
        errors += [r["status"] for r in got if r["status"] != "ok"]
        ok = ok and all(r["status"] == "ok" for r in got)
        leaked += bad
        rows.append(dict(q, runs=got, rate=rate, passed=ok))
        per.setdefault(q["owner"], [0, 0])
        per[q["owner"]][0] += ok
        per[q["owner"]][1] += 1
        print("%s %-16s %-5s rate=%.2f %s calls=%s :: %s" % ("PASS" if ok else "FAIL", q["owner"], q["should_trigger"], rate,
              [f or "-" for f in firsts], sorted({s for r in got for s in r["skill_calls"]}), q["query"][:60]))
    for s, (p, t) in per.items():
        print("%-16s %d/%d" % (s, p, t))
    reads = sum(len(r["leaf_reads"]) for g in runs.values() for r in g)
    print("Skill-tool invocations of principle-* or secondbrain-mode: %d %s" % (len(leaked), sorted(set(leaked))))
    print("principles opened by path from a skill step: %d; runs not ok: %d %s" % (reads, len(errors), sorted(set(errors))))
    path = a.json or os.path.join(HERE, "results", "trigger-plugin%s.json" % ("-full" if a.full else ""))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump({"model": a.model, "runs_per_query": a.runs, "full": a.full, "plugin": a.plugin, "results": rows,
                   "summary": {s: {"passed": p, "total": t} for s, (p, t) in per.items()},
                   "auto_invoked_disabled": leaked, "leaf_reads": reads, "errors": errors}, f, indent=2, ensure_ascii=False)
    return 0 if not leaked and not errors and all(p == t for p, t in per.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
