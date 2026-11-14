#!/usr/bin/env python3
"""Place remote images and web embeds on an existing Excalidraw drawing and print one JSON line.

Usage: place.py <vault-relative drawing> <items.json|-> --vault <name> [--vault-root DIR]

items: [{"x", "y", "width", "image": URL, "height": max height, "link": URL},
        {"x", "y", "width", "height", "embed": URL, "link": URL}]

An image keeps its URL (nothing is downloaded into the vault) and is scaled to `width`, then
down to `height` when taller. The plugin CLI cannot do this, so a trusted ExcalidrawAutomate
script is written into the vault, run once and always removed.
Output: {drawing, placed}. Save afterwards with save.py.
"""
import argparse, json, os, subprocess, sys, time, uuid

X = "obsidian-excalidraw-plugin"
JS = """const a = utils.input; let n = 0;
for (const p of a.items) {
  let id;
  if (p.embed) {
    id = ea.addEmbeddable(p.x, p.y, p.width, p.height, p.embed);
  } else {
    id = await ea.addImage({topX: p.x, topY: p.y, imageFile: p.image, scale: true});
    const el = ea.getElement(id);
    let w = p.width, h = Math.round(p.width * el.height / el.width);
    if (p.height && h > p.height) { w = Math.round(w * p.height / h); h = p.height; }
    el.width = w; el.height = h;
  }
  if (p.link) ea.getElement(id).link = p.link;
  n++;
}
const ok = await ea.addElementsToView(false, true, true);
return {ok, placed: n};
"""


def run(*args):
    try:
        r = subprocess.run(["obsidian", *args], capture_output=True, text=True, timeout=180)
    except (OSError, subprocess.TimeoutExpired) as e:
        sys.exit(f"obsidian CLI failed: {e}")
    return r.stdout.strip()


def parse(out):
    try:
        return json.loads(out[out.find("{"):])
    except ValueError:
        sys.exit(f"unparseable CLI response: {out[:400]}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("drawing")
    p.add_argument("items")
    p.add_argument("--vault", required=True)
    p.add_argument("--vault-root")
    a = p.parse_args()

    items = json.load(sys.stdin if a.items == "-" else open(a.items))
    if not isinstance(items, list) or not items:
        sys.exit("items must be a non-empty JSON array")
    for i in items:
        if not (i.get("image") or i.get("embed")):
            sys.exit(f"item needs image or embed: {json.dumps(i)[:200]}")
        if i.get("embed") and not i.get("height"):
            sys.exit(f"embed needs height: {json.dumps(i)[:200]}")

    root = a.vault_root
    if not root:
        out = run(f"vault={a.vault}", "vault", "info=path")
        root = out.splitlines()[-1].strip() if out else ""
    if not root or not os.path.isdir(root):
        sys.exit("cannot find vault root; pass --vault-root")
    drawing = a.drawing.strip("/")
    if not os.path.isfile(os.path.join(root, drawing)):
        sys.exit(f"drawing not found in vault: {drawing}")

    rid = "place-" + uuid.uuid4().hex[:16]
    rel = os.path.join(os.path.dirname(drawing), f"{rid}.md")
    path = os.path.join(root, rel)
    try:
        with open(path, "w") as f:
            f.write(JS)
        for _ in range(20):
            if rel in run(f"vault={a.vault}", "file", f"path={rel}"):
                break
            time.sleep(0.5)
        parse(run(f"vault={a.vault}", f"{X}:open", f"path={drawing}"))
        res = parse(run(f"vault={a.vault}", f"{X}:script", "json=" + json.dumps({
            "apiVersion": 1, "command": "script", "requestId": rid, "path": drawing,
            "script": rel, "trusted": True, "args": {"items": items}})))
        data = res.get("data") or {}
        if not res.get("ok") or not data.get("ok"):
            sys.exit(f"place failed: {json.dumps(res.get('error') or res)[:500]}")
        print(json.dumps({"drawing": drawing, "placed": data.get("placed")}, ensure_ascii=False))
    finally:
        if os.path.exists(path):
            os.remove(path)


if __name__ == "__main__":
    main()
