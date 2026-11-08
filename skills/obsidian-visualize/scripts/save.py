#!/usr/bin/env python3
"""Save, open or close an Excalidraw drawing through the plugin and print one JSON line.

Usage: save.py <vault-relative drawing> [--vault Ataraxia] [--close] [--open]

default  save every open view of the drawing (saveWithOutcome) and require `persisted`
--close  save first, and only if every save is `persisted` detach the views; never discards edits
--open   open the drawing, save it so the plugin writes the file in its own format, and check
         `:read source=disk` has the same element count as the live view
Output: {drawing, saved, closed, elements}. Exit 1 when a save is not confirmed.
"""
import argparse, json, subprocess, sys, time

X = "obsidian-excalidraw-plugin"


def run(*args):
    try:
        r = subprocess.run(["obsidian", *args], capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.TimeoutExpired) as e:
        sys.exit(f"obsidian CLI failed: {e}")
    return r.stdout.strip()


def plugin(vault, cmd, payload):
    out = run(f"vault={vault}", f"{X}:{cmd}", "json=" + json.dumps(dict(payload, apiVersion=1)))
    try:
        return json.loads(out[out.find("{"):])
    except ValueError:
        sys.exit(f"unparseable CLI response: {out[:400]}")


def js(vault, body):
    """Run an async snippet in Obsidian; it must assign its JSON-able result to window.__s."""
    run(f"vault={vault}", "eval", "code=delete window.__s")
    run(f"vault={vault}", "eval", "code=(async()=>{" + body + "})()")
    for _ in range(40):
        out = run(f"vault={vault}", "eval", "code=window.__s")
        if out.startswith("=> ") and out[3:].strip() != "undefined":
            return json.loads(out[3:])
        time.sleep(0.5)
    sys.exit("no answer from Obsidian eval")


def leaves(path):
    return ("const L=app.workspace.getLeavesOfType('excalidraw').filter(l=>l.view.file&&l.view.file.path===%s);" % json.dumps(path))


def save(vault, path):
    return js(vault, leaves(path) + "const r=[];for(const l of L){r.push(await l.view.saveWithOutcome(true))}window.__s=r;")


def live_total(vault, path):
    r = plugin(vault, "read", {"path": path, "source": "live", "detail": "summary"})
    return r["data"].get("total") if r.get("ok") else None


def main():
    p = argparse.ArgumentParser()
    p.add_argument("drawing")
    p.add_argument("--vault", default="Ataraxia")
    p.add_argument("--close", action="store_true")
    p.add_argument("--open", action="store_true")
    a = p.parse_args()
    path, v = a.drawing.strip("/"), a.vault
    if a.open:
        for _ in range(10):
            if plugin(v, "open", {"path": path}).get("ok"):
                break
            time.sleep(1.5)
        else:
            sys.exit("could not open the drawing (indexed? check `obsidian vault=<n> file path=<path>`)")
        time.sleep(1.5)
    res = save(v, path)
    ok = all(r.get("status") == "persisted" for r in res)
    if ok and a.close and res:
        if js(v, leaves(path) + "window.__s=L.some(l=>l.view.isDirty());"):
            ok = False
    closed = False
    if not ok:
        print(json.dumps(dict(drawing=path, saved=False, closed=False, elements=None, outcomes=res)))
        sys.exit("save not confirmed as persisted and clean; nothing was closed")
    elements = None
    if a.open:
        live, disk = live_total(v, path), plugin(v, "read", {"path": path, "source": "disk", "detail": "summary"})
        elements = disk["data"].get("total") if disk.get("ok") else None
        if not res or live is None or live != elements:
            print(json.dumps(dict(drawing=path, saved=ok, closed=False, elements=elements, live=live)))
            sys.exit("disk element count differs from the live view")
    if a.close:
        js(v, leaves(path) + "L.forEach(l=>l.detach());window.__s=L.length;")
        closed = True
    print(json.dumps(dict(drawing=path, saved=ok, closed=closed, elements=elements)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
