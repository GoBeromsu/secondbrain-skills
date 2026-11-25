#!/usr/bin/env python3
"""Policy lint through the running Obsidian app: `obsidian eval` over app.metadataCache, plus
`obsidian aliases` (Entity names) and `obsidian unresolved` (BROKEN, body and frontmatter).

Prints the same TSV as link-lint.py (`RULE<TAB>path<TAB>line<TAB>text`, then `# violations=N`).
It never opens or switches a vault: if Obsidian is not running with this vault already open it
exits 3, and the caller runs `link-lint.py --checks policy` instead.
"""
import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
NOT_RUNNING = 3
LEGACY_KEYS = {"youtube", "x"}


def nfc(s):
    return unicodedata.normalize("NFC", s)


def obsidian_config():
    system = platform.system()
    if system == "Darwin":
        base = os.path.expanduser("~/Library/Application Support")
    elif system == "Windows":
        base = os.environ.get("APPDATA", "")
    else:
        base = os.environ.get("XDG_CONFIG_HOME") or os.path.expanduser("~/.config")
    return os.path.join(base, "obsidian", "obsidian.json")


def app_running():
    names = {"Darwin": "Obsidian", "Windows": "Obsidian.exe"}.get(platform.system(), "obsidian")
    if platform.system() == "Windows":
        run = subprocess.run(["tasklist", "/FI", "IMAGENAME eq " + names], capture_output=True, text=True)
        return names.lower() in run.stdout.lower()
    return subprocess.run(["pgrep", "-x", names], capture_output=True).returncode == 0


def open_vault_name(vault):
    """Name of `vault` if Obsidian has it open, else None. Reads the app's vault list only."""
    try:
        with open(obsidian_config(), encoding="utf-8") as f:
            known = json.load(f).get("vaults", {})
    except (OSError, ValueError):
        return None
    real = os.path.realpath(vault)
    hits = [v for v in known.values() if os.path.realpath(v.get("path", "")) == real]
    if len(hits) != 1 or not hits[0].get("open"):
        return None
    name = os.path.basename(real)
    same = [v for v in known.values() if os.path.basename(os.path.realpath(v.get("path", ""))) == name]
    return name if len(same) == 1 else None


def cli(exe, name, *args):
    run = subprocess.run([exe, "vault=" + name, *args], capture_output=True, text=True,
                         timeout=600 if args[0] == "eval" else 120)
    if run.returncode != 0 or run.stdout.startswith("Error"):
        raise RuntimeError("obsidian %s failed: %s" % (args[0], (run.stderr or run.stdout).strip()[:300]))
    return run.stdout


def evaluate(exe, name, args):
    """Run obsidian-lint.js. Arguments travel in a temp file outside the vault: the Entity map of a
    large vault does not fit on a command line."""
    with tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8", delete=False) as t:
        json.dump(args, t, ensure_ascii=False)
    try:
        with open(os.path.join(HERE, "obsidian-lint.js"), encoding="utf-8") as f:
            code = f.read().replace("__ARGS_FILE__", json.dumps(t.name))
        out = cli(exe, name, "eval", "code=" + code).strip()
    finally:
        os.unlink(t.name)
    if out.startswith("=>"):
        out = out[2:].strip()
    try:
        return json.loads(out)
    except ValueError:
        raise RuntimeError("obsidian eval returned no JSON: %s" % out[:300])


def split_paths(joined, files):
    """The CLI joins several paths with ", " and file names may contain ", ". Return the one way to
    split `joined` into vault files; raise if there is none or more than one."""
    pieces = joined.split(", ")
    ways = {len(pieces): [[]]}
    for i in range(len(pieces) - 1, -1, -1):
        ways[i] = [[", ".join(pieces[i:j])] + rest for j in range(i + 1, len(pieces) + 1)
                   if ", ".join(pieces[i:j]) in files for rest in ways[j]][:2]
    if len(ways[0]) != 1:
        raise RuntimeError("cannot tell which vault files %r names" % joined[:200])
    return ways[0][0]


def aliases(exe, name, files):
    """{path: [alias, ...]} from `obsidian aliases verbose` (`alias<TAB>path[, path...]` per line)."""
    out = {}
    for line in cli(exe, name, "aliases", "verbose").splitlines():
        alias, sep, joined = line.rpartition("\t")
        for path in split_paths(joined, files) if sep else []:
            out.setdefault(nfc(path), []).append(alias)
    return out


def property_counts(exe, name, keys):
    """{key: notes using it} from `obsidian properties counts`, for the retired and lifecycle keys."""
    out = {}
    for line in cli(exe, name, "properties", "counts", "format=tsv").splitlines():
        key, sep, count = line.rpartition("\t")
        if not sep or not count.strip().isdigit():
            raise RuntimeError("obsidian properties: unexpected line %r" % line[:200])
        if key in keys:
            out[key] = int(count)
    return out


def unresolved(exe, name, files):
    """{source path: [link, ...]} from `obsidian unresolved verbose`."""
    out = {}
    for item in json.loads(cli(exe, name, "unresolved", "verbose", "format=json") or "[]"):
        for path in split_paths(str(item.get("sources", "")), files):
            out.setdefault(path, []).append(item["link"])
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--vault", required=True)
    ap.add_argument("--scope", nargs="*", default=["."])
    ap.add_argument("--baseline")
    ap.add_argument("--wiki", action="append", required=True, help="wiki-role folder from the live policy (repeatable)")
    ap.add_argument("--lifecycle", required=True, help="comma-separated `type` values the live policy names as lifecycle notes")
    ap.add_argument("--obsidian", default="obsidian", help="Obsidian CLI executable")
    a = ap.parse_args(argv)
    root = os.path.abspath(a.vault)
    try:
        name = open_vault_name(root) if app_running() else None
        if not name:
            raise RuntimeError("Obsidian is not running with %s open" % root)
        if not shutil.which(a.obsidian):
            raise RuntimeError("the Obsidian CLI %r is not on PATH" % a.obsidian)
        if os.path.realpath(cli(a.obsidian, name, "vault", "info=path").strip()) != os.path.realpath(root):
            raise RuntimeError("obsidian vault=%s does not point at %s" % (name, root))
        return report(a, root, name)
    except (RuntimeError, ValueError, KeyError, OSError, subprocess.SubprocessError) as e:
        sys.stderr.write("%s; Step 12 is Not checked through Obsidian, run link-lint.py --checks policy\n" % e)
        return NOT_RUNNING


def report(a, root, name):
    index = evaluate(a.obsidian, name, {"mode": "index"})
    files = set(index["files"])
    alias_map = aliases(a.obsidian, name, files)
    entities = {}
    for path in sorted(nfc(p) for p in index["entities"]):
        for n in [os.path.basename(path)[:-3]] + alias_map.get(path, []):
            n = nfc(n.strip())
            if n and not n.startswith("[[") and path not in entities.get(n, []):
                entities.setdefault(n, []).append(path)
    scope = [os.path.relpath(os.path.realpath(os.path.join(root, s)), os.path.realpath(root)) for s in a.scope]
    if any(s == ".." or s.startswith("../") for s in scope):
        raise RuntimeError("a scope is outside the vault")
    in_scope = lambda p: any(s == "." or p == s or p.startswith(s.rstrip("/") + "/") for s in scope)
    findings = evaluate(a.obsidian, name, {
        "mode": "check",
        "scope": scope,
        "wiki": [w.strip("/") for w in a.wiki],
        "lifecycle": [t.strip() for t in a.lifecycle.split(",") if t.strip()],
        "entities": entities,
        "unresolved": {p: v for p, v in unresolved(a.obsidian, name, files).items() if in_scope(p)},
    })

    known = set()
    if a.baseline:
        with open(a.baseline, encoding="utf-8") as f:
            for line in f:
                p = line.rstrip("\n").split("\t")
                if len(p) == 4:
                    known.add((p[0], p[1], p[3]))
    rows = sorted((nfc(path), line or 0, rule, str(snip)[:120].replace("\t", " ").replace("\n", " "))
                  for rule, path, line, snip in findings)
    counts = property_counts(a.obsidian, name, LEGACY_KEYS | {"status"})
    sys.stdout.write("# properties %s\n" % " ".join("%s=%d" % (k, counts.get(k, 0)) for k in sorted(LEGACY_KEYS | {"status"})))
    n = 0
    for path, line, rule, snip in rows:
        if (rule, path, snip) in known:
            continue
        sys.stdout.write("%s\t%s\t%d\t%s\n" % (rule, path, line, snip))
        n += 1
    sys.stdout.write("# violations=%d\n" % n)
    return 1 if n else 0


if __name__ == "__main__":
    sys.exit(main())
