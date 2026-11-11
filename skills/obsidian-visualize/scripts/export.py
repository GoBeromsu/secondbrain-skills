#!/usr/bin/env python3
"""Export an Excalidraw drawing to PNG through the plugin CLI and print one JSON line.

Usage: export.py <vault-relative drawing> [--out ABS.png] --vault <name>
       [--vault-root DIR] [--max-width 1600] [--scale 1] [--placeholder-images]
       [--source auto|live|disk]

The plugin only writes inside the vault, so the PNG is written next to the drawing,
moved to --out (default: a temp dir) and the vault copy is always removed.
"""
import argparse, json, os, shutil, struct, subprocess, sys, tempfile, uuid

MAX_PIXELS = 15_000_000


def fail(msg):
    print(msg, file=sys.stderr)
    sys.exit(1)


def cli(*args):
    try:
        r = subprocess.run(["obsidian", *args], capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.TimeoutExpired) as e:
        fail(f"obsidian CLI failed: {e}")
    return r.stdout.strip(), r.stderr.strip()


def parse(out):
    for start in (out.find("{"),):
        if start >= 0:
            try:
                return json.loads(out[start:])
            except ValueError:
                pass
    return None


def main():
    p = argparse.ArgumentParser()
    p.add_argument("drawing")
    p.add_argument("--out")
    p.add_argument("--vault", required=True)
    p.add_argument("--vault-root")
    p.add_argument("--max-width", type=int, default=1600)
    p.add_argument("--scale", type=float, default=1)
    p.add_argument("--placeholder-images", action="store_true")
    p.add_argument("--source", default="auto", choices=["auto", "live", "disk"])
    a = p.parse_args()

    root = a.vault_root
    if not root:
        out, _ = cli(f"vault={a.vault}", "vault", "info=path")
        root = out.splitlines()[-1].strip() if out else ""
    if not root or not os.path.isdir(root):
        fail("cannot find vault root; pass --vault-root")
    drawing = a.drawing.strip("/")
    if not os.path.isfile(os.path.join(root, drawing)):
        fail(f"drawing not found in vault: {drawing}")

    rid = "export-" + uuid.uuid4().hex[:16]
    tmp_rel = os.path.join(os.path.dirname(drawing), f"{rid}.png")
    tmp_abs = os.path.join(root, tmp_rel)
    payload = {
        "apiVersion": 1, "command": "export", "requestId": rid, "path": drawing,
        "out": tmp_rel, "overwrite": True, "source": a.source, "scale": a.scale,
        "maxWidth": a.max_width, "maxPixels": MAX_PIXELS,
    }
    if a.placeholder_images:
        payload["imagePolicy"] = {"default": "placeholder"}

    try:
        stdout, stderr = cli(f"vault={a.vault}", "obsidian-excalidraw-plugin:export",
                             "json=" + json.dumps(payload))
        res = parse(stdout)
        if res is None:
            fail(f"unparseable CLI response: {(stdout or stderr)[:500]}")
        if not res.get("ok"):
            err = res.get("error") or res
            fail(f"export failed: {json.dumps(err)[:500]}")
        if not os.path.isfile(tmp_abs):
            fail("export reported ok but no PNG was found in the vault")
        with open(tmp_abs, "rb") as f:
            head = f.read(24)
        if head[:8] != b"\x89PNG\r\n\x1a\n":
            fail("output is not a PNG")
        width, height = struct.unpack(">II", head[16:24])
        dest = a.out or os.path.join(tempfile.mkdtemp(prefix="excalidraw-"),
                                     os.path.basename(drawing).split(".")[0] + ".png")
        dest = os.path.abspath(dest)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.move(tmp_abs, dest)
        print(json.dumps({"drawing": drawing, "png": dest, "width": width,
                          "height": height, "bytes": os.path.getsize(dest)}))
    finally:
        if os.path.exists(tmp_abs):
            os.remove(tmp_abs)


if __name__ == "__main__":
    main()
