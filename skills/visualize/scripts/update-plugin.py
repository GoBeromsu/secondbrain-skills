#!/usr/bin/env python3
"""Update the Obsidian Excalidraw plugin to the latest release and print one JSON line.

Usage: update-plugin.py [--vault Ataraxia] [--plugin obsidian-excalidraw-plugin] [--timeout 60]

The Obsidian CLI has no plugin update command, so this drives the app's plugin manager
through `obsidian eval`. Fallback: Settings > Community plugins > Check for updates.
"""
import argparse, json, subprocess, sys, time


def run(vault, *args):
    r = subprocess.run(["obsidian", f"vault={vault}", *args], capture_output=True, text=True, timeout=60)
    return r.stdout.strip()


def ev(vault, code):
    out = run(vault, "eval", "code=" + code)
    return out[3:].strip() if out.startswith("=> ") else out


def version(vault, plugin):
    for line in run(vault, "plugin", f"id={plugin}").splitlines():
        if line.startswith("version"):
            return line.split("\t", 1)[1].strip()
    return None


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--vault", default="Ataraxia")
    p.add_argument("--plugin", default="obsidian-excalidraw-plugin")
    p.add_argument("--timeout", type=int, default=60)
    a = p.parse_args()
    before = version(a.vault, a.plugin)
    if before is None:
        print(f"plugin {a.plugin} not installed in vault {a.vault}", file=sys.stderr)
        sys.exit(1)
    code = (
        "window.__u=0;app.plugins.checkForUpdates().then(async()=>{"
        f"const u=app.plugins.updates[{json.dumps(a.plugin)}];"
        "if(u){await app.plugins.installPlugin(u.repo,u.version,u.manifest);"
        "await app.plugins.disablePlugin(u.manifest.id);"
        "await app.plugins.enablePlugin(u.manifest.id)}window.__u=1})"
        ".catch(e=>{window.__u='err '+e})"
    )
    ev(a.vault, code)
    end = time.time() + a.timeout
    state = "0"
    while time.time() < end:
        state = ev(a.vault, "window.__u")
        if state != "0":
            break
        time.sleep(1)
    if state != "1":
        print(f"update did not finish: {state}", file=sys.stderr)
        sys.exit(1)
    # the plugin's CLI commands vanish briefly after a reload; wait until they answer
    ok = False
    end = time.time() + a.timeout
    while time.time() < end and not ok:
        ok = '"ok":true' in run(a.vault, f"{a.plugin}:status")
        if not ok:
            time.sleep(1)
    if not ok:
        print("plugin CLI did not come back; run: obsidian vault=%s plugin:reload id=%s" % (a.vault, a.plugin), file=sys.stderr)
        sys.exit(1)
    print(json.dumps({"plugin": a.plugin, "before": before, "after": version(a.vault, a.plugin)}))


if __name__ == "__main__":
    main()
