---
name: "obsidian-visualize"
description: "Chooses the visual form and builds it: a JSON Canvas (.canvas), an Excalidraw drawing (.excalidraw.md), or a mermaid block drawn by Pele (Obsidian 1.15+). Use for creating, editing or validating a .canvas file (nodes, edges, groups, IDs); an architecture, data-flow, pipeline, sequence, dependency, status or concept diagram; a mind map, sketchnote or sticky notes; a flowchart, sequence, class, state, ER, gantt, journey, pie, mindmap, timeline, sankey, kanban, treemap, architecture, xychart, swimlane, gitGraph, quadrant or C4 block; a mermaid block with a parse error, raw text or empty box in Reading view or Live Preview, or fine in mermaid.live but not the vault; a `-beta` keyword question; generating, replacing, inspecting, importing, editing, exporting or rendering Excalidraw, including plugin Mermaid import; or choosing between Canvas, Excalidraw, Pele and a plain table. 캔버스·플로우차트·아키텍처도·개념도·머메이드·펠레·손그림·마인드맵·스케치노트·도구 연결도·로고·아이콘·인물 사진. Not for note prose or properties, or plugin installs: use markdown or obsidian-cli."
license: MIT
---

# Visualize

Pick the form the content supports, build it on the surface that fits, and look at the result before calling it done. A table that answers the question beats a diagram that decorates it.

## Choose the form

| What the nodes are | Form | Writer |
| --- | --- | --- |
| Existing vault notes to navigate | **JSON Canvas** (`.canvas`) | direct file write; schema in `references/canvas.md` |
| Free shapes with no backing note: architecture, data flow, mind map, sketch, annotated figure | **Excalidraw** (`.excalidraw.md`) | plugin CLI, or `scripts/draw.py` offline |
| A small structural diagram inside a note's prose | **Pele** (a `mermaid` fence) | the note edit itself |

If the request names a form, that form is the answer unless it cannot carry the content; say so before switching. Do not deliver a Canvas because Excalidraw looked tedious, nor an Excalidraw of note titles when the reader should click through to notes. For a Canvas, every `file` node and wikilink target must resolve in the destination vault; a plausible name is not a resolved one.

Ground every box and arrow in inspected evidence (files at a pinned revision, note contents, measured values). Label declared configuration as declared. A reference image supplies visual language only, never services or numbers.

## Canvas

A `.canvas` file is JSON Canvas 1.0, written directly as a file; no plugin or CLI is required. Open [`references/canvas.md`](references/canvas.md) for the node, edge, color and ID schema and its validation checklist, [`references/canvas-operations.md`](references/canvas-operations.md) before changing a canvas that already holds user data, and [`references/canvas-examples.md`](references/canvas-examples.md) for complete documents. Existing IDs, unrelated nodes and edges, unknown keys and node order survive an edit; a duplicate or dangling ID is reported, never repaired silently.

## Excalidraw

Open [`references/excalidraw-design.md`](references/excalidraw-design.md) to choose the drawing's pattern, palette and spacing before placing anything; its fidelity check (each stated relationship is one arrow, labels in the user's language) and its sketch guidance apply to every drawing. The common case is a loop of two scripts, so [`references/excalidraw-plugin.md`](references/excalidraw-plugin.md) is needed only to edit an existing drawing or for a plugin edge case.

**Update first.** Keep the Excalidraw plugin on its latest version: `python3 scripts/update-plugin.py --vault <name>` (prints `plugin`, `before`, `after`). The CLI has no update command; if the script fails, use Settings → Community plugins → Check for updates. If `obsidian-excalidraw-plugin:*` commands return "not found" while the plugin is enabled, run `obsidian vault=<name> plugin:reload id=obsidian-excalidraw-plugin` once.

**Write, then look:**

```
python3 scripts/draw.py <spec.json|-> [<out.excalidraw.md> [--replace]]
python3 scripts/export.py <vault-relative drawing> [--out <abs path outside vault>] --vault <name> [--max-width 1600] [--scale 1] [--placeholder-images] [--source auto|live|disk]
```

`export.py` writes the PNG outside the vault, deletes its vault copy even on failure, and prints one JSON line with `drawing`, `png`, `width`, `height`, `bytes`. View the PNG, fix defects, rerun. The plugin documents its own CLI: `obsidian vault=<name> obsidian-excalidraw-plugin:skill` and `:schema action=<create|export|apply|read>`.

1. **Probe.** `obsidian vault=<name> obsidian-excalidraw-plugin:status` and `schema action=<cmd>`. If the plugin or CLI is absent, make a new drawing with `draw.py`, the only offline writer; never install or enable a plugin to make a drawing work. Editing an existing drawing without the app is an unmet prerequisite: report it, write nothing.
2. **Palette.** Take colours from the palette the user or the vault's policy names, else from the running app's theme, else the built-in palette; the design reference's Palette section maps them. Report which source the drawing used.
3. **Create.** Native `create` with a new `path`: skeleton elements, Lucide `icons`, frames, sticky notes, arrows bound by `start`/`end`. It never overwrites. Choose coordinates from the pattern; the reply's `data.idMap` holds the real ids.
4. **Edit.** Fix in place, never delete and recreate: `open`, `read source=live` for the `revision`, then `apply` with `expectedRevision`. A stale revision changes nothing; re-read and rebuild.
5. **Export and look.** `scripts/export.py` writes the image outside the vault; view it. Fix every defect listed in the design reference's render loop (an arrow over or touching a non-endpoint box or frame title counts), re-export, repeat until you would show it unqualified. An export that was not looked at is not render QA.
6. **Clean up.** Close tabs you opened; `export.py` leaves no export in the vault.
7. **Save.** `:apply` saves itself; any other live edit reaches disk only via `python3 scripts/save.py <drawing> --vault <name>`. After `draw.py` writes a file run it with `--open`; before `draw.py` rewrites an open drawing run it with `--close` (saves first, closes only if saved and clean).
   An existing drawing may hold the owner's hand edits: change it with `:apply`, and use `draw.py --replace` only on new drawings or ones it accepts as unedited (`--force` overrides, never by default).

Offline, or for a plain boxes-and-arrows graph, `scripts/draw.py` (usage above) lays out and writes the file. It writes a new file and prints one JSON line with `path`, `sha256`, `elements`, `by_type`, `crossings`, `warnings`. Non-empty `warnings` means look at the drawing. Unknown spec keys are ignored and named there. If it warns about crossings, do not rerun hoping for better: draw by hand through native `create` with chosen coordinates and a pattern from the design reference. `--replace` redoes only this script's own output; any other existing file is refused. With no output path it writes nothing and prints the scene colours (`ink`, `background`, `palette` as `[fill, stroke]`) to use in native `create`.

- Top level: `direction` (`LR`, `TB`), `title`, `frames` `[{id,label}]`, `nodes`, `edges`, `palette` `{name: "#rrggbb"}` or `{name: [fill, stroke]}`, `ink`, `background`, `dark` (`true` when the colours were read from a dark theme).
- Node: `id`, `label` (required), `shape` (`rectangle`, `ellipse`, `diamond`, `text`, `note`), `color` (`blue`, `green`, `yellow`, `red`, `purple`, `gray`, `note`, or a `palette` name), `frame`, `group`, `link`, `icon` (URL), `roughness` 0/1/2, `strokeStyle` `solid`/`dashed`/`dotted`.
- Edge: `from`, `to` (required), `label`, `dashed`, `head` (`arrow`, `triangle`, `bar`, `dot`, `none`).

`node scripts/inspect.mjs lint <file>` checks a plain file's ids, two-way bindings and overlaps; it refuses `compressed-json`, which the plugin writes once a drawing has been opened.

What the CLI cannot do (elbow arrows, Mermaid-to-elements, embedded notes and pages, frontmatter keys) goes through a trusted EA script, as `excalidraw-plugin.md` describes, only in a disposable or approved vault. `obsidian eval` is synchronous: start an async call that stores its result on `window`, then read it in a second call. Opening a drawing makes the plugin re-save it compressed, so never hand-edit the compressed block.

Give every node that names a recognizable thing its image beside the label, unasked: a product, app, service or company gets its official logo or app icon, a public figure a public photo, a character its official art; a private person gets only an image already in the vault. Look first for a PNG on the thing's own site (`apple-touch-icon.png`, `icon.png`) or its GitHub organization avatar (`https://github.com/<org>.png`); keep a URL only after fetching it shows an image of that exact thing, never its maker's personal avatar or an unrelated favicon. When none is found, leave the node without one and list it as skipped with the reason; never draw a stand-in.

Images: an external image (logo, icon, web screenshot) stays a URL in the drawing's Embedded Files (`icon` in the spec); never download it into the vault, and tell the user it loads from a third party on first open. To check layout without the network use `export.py --placeholder-images`, otherwise a live export. If export fails with `ASSETS_UNAVAILABLE` on remote images (seen with SVG logos from `cdn.simpleicons.org`), do not retry or download them: rerun `export.py --placeholder-images` to check layout and tell the user to confirm the logos by opening the drawing in Obsidian. Only images already in the vault are referenced as vault files.

## Pele

A diagram inside a note is a `mermaid` fence. Pele draws it, so correct syntax is the work and a probe only confirms it. Obsidian 1.15.0+ only; earlier apps are out of scope.

- Probe commands and the `loadMermaid` step are in [`references/pele.md`](references/pele.md).
- When a block fails, check the "Syntax pitfalls" section of that file; [`references/pele-catalog.md`](references/pele-catalog.md) has copy-ready blocks for the rest.

Extras (the `excalidraw-extras` companion plugin) adds two things to a drawing: Mermaid converted to editable elements, when the user wants to hand-edit a Mermaid diagram, and LaTeX for math. Otherwise use a Pele fence. Its absence is normal; install it only when asked. Details are in `excalidraw-plugin.md`; `pele.md` does not own them.

## Evidence ladder

Report the highest level actually reached; a lower one never stands in for a higher one.

| Level | Proves | Produced by |
| --- | --- | --- |
| A static | Structure is sound: unique ids, mirrored bindings, finite geometry, grammar by the rules | `inspect.mjs lint`, `draw.py`'s own readback, the schema, reading the source |
| B readback | The intended bytes are at the intended path and parse | `read source=disk`, re-reading the file after the write; the write alone is not B |
| C runtime load | The running app loaded it and counts match | CLI `read`, `getSceneFromFile`, `pele.render` |
| D rendered | The picture is legible and was looked at | native `export` viewed, a preview tab inspected |

"Written and read back" is a complete result at B; "renders correctly" is not.

## Native procedure

For any change to an existing drawing, Canvas or note:

1. Resolve the exact path and the effect the task authorized; with no target path, stay read-only.
2. Read its current bytes (`read`, or the file) and keep the `revision`.
3. `apply` only the selected ids, so unrelated elements, frontmatter and prose stay as they were.
4. Use the least destructive surface that does it: `apply` over recreate, `create` for a new path, never an overwrite.
5. Read back the persisted result, not the live scene.
6. Report the level reached, plugin and app versions, and anything unmet.
7. Leave a runtime fact unknown when neither the docs nor the installed version settles it.

## Done when

- The form matches the table and the reason is stated.
- Every claim traces to evidence; every `file` and wikilink target resolves.
- A drawing was exported and looked at (D), or the report names the level it stopped at.
