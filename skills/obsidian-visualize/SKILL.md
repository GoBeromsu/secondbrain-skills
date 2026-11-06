---
name: obsidian-visualize
description: "Chooses the visual form and builds it: a JSON Canvas of notes, an Excalidraw drawing (.excalidraw.md; plugin CLI or script), or a mermaid block drawn by Pele (Obsidian 1.15+). Use for an architecture, data-flow, pipeline, sequence, dependency, status or concept diagram; a mind map, sketchnote or sticky notes; a flowchart, sequence, class, state, ER, gantt, journey, pie, mindmap, timeline, sankey, kanban, treemap, architecture, xychart, swimlane, gitGraph, quadrant or C4 block; a mermaid block with a parse error, raw text or empty box in Reading view or Live Preview, or fine in mermaid.live but not the vault; a beta prefix needing a version-gated fallback; generating, replacing, inspecting, importing, editing, exporting or rendering Excalidraw, including plugin Mermaid import; or choosing between Canvas, Excalidraw, Pele and a plain table. 플로우차트·아키텍처도·개념도·머메이드·펠레·손그림·마인드맵·스케치노트. Not for Canvas schema, note prose or properties, or plugin installs: use obsidian-canvas, obsidian-markdown or obsidian-cli."
license: MIT
---

# Obsidian Visualize

Pick the form the content supports, build it on the surface that fits, and look at the result before calling it done. A table that answers the question beats a diagram that decorates it.

## Choose the form

| What the nodes are | Form | Writer |
| --- | --- | --- |
| Existing vault notes to navigate | **JSON Canvas** (`.canvas`) | direct file write; schema in `obsidian-canvas` |
| Free shapes with no backing note: architecture, data flow, mind map, sketch, annotated figure | **Excalidraw** (`.excalidraw.md`) | plugin CLI, or `scripts/draw.py` offline |
| A small structural diagram inside a note's prose | **Pele** (a `mermaid` fence) | the note edit itself |

If the request names a form, that form is the answer unless it cannot carry the content; say so before switching. Do not deliver a Canvas because Excalidraw looked tedious, nor an Excalidraw of note titles when the reader should click through to notes. For a Canvas, every `file` node and wikilink target must resolve in the destination vault; a plausible name is not a resolved one.

Ground every box and arrow in inspected evidence (files at a pinned revision, note contents, measured values). Label declared configuration as declared. A reference image supplies visual language only, never services or numbers.

## Excalidraw

Open [`references/excalidraw-plugin.md`](references/excalidraw-plugin.md) for the CLI, skeleton fields and feature-to-surface table, and [`references/excalidraw-design.md`](references/excalidraw-design.md) to choose the drawing's pattern, palette and spacing before placing anything; its fidelity check (each stated relationship is one arrow, labels in the user's language) and its sketch guidance apply to every drawing.

1. **Probe.** `obsidian vault=<name> obsidian-excalidraw-plugin:status` and `schema action=<cmd>`. If the plugin or CLI is absent, make a new drawing with `draw.py`, the only offline writer; never install or enable a plugin to make a drawing work. Editing an existing drawing without the app is an unmet prerequisite: report it, write nothing.
2. **Create.** Native `create` with a new `path`: skeleton elements, Lucide `icons`, frames, sticky notes, arrows bound by `start`/`end`. It never overwrites. Choose coordinates from the pattern; the reply's `data.idMap` holds the real ids.
3. **Edit.** Fix in place, never delete and recreate: `open`, `read source=live` for the `revision`, then `apply` with `expectedRevision`. A stale revision changes nothing; re-read and rebuild.
4. **Export and look.** `export` (with `requestId`, `path`, `source`, and a vault-relative `out` ending `.png`) writes the image; copy it out of the vault, view it. Fix every defect listed in the design reference's render loop, re-export, repeat until you would show it unqualified. An export that was not looked at is not render QA.
5. **Clean up.** Close tabs you opened and delete any export from the vault.

Offline, or for a plain boxes-and-arrows graph, `scripts/draw.py` lays out and writes the file:

`python3 scripts/draw.py <spec.json|-> <out.excalidraw.md> [--replace]`

It writes a new file and prints one JSON line with `path`, `sha256`, `elements`, `by_type`, `crossings`, `warnings`. Non-empty `warnings` means look at the drawing. Unknown spec keys are ignored and named there. If it warns about crossings, do not rerun hoping for better: draw by hand through native `create` with chosen coordinates and a pattern from the design reference. `--replace` redoes only this script's own output; any other existing file is refused.

- Top level: `direction` (`LR`, `TB`), `title`, `frames` `[{id,label}]`, `nodes`, `edges`.
- Node: `id`, `label` (required), `shape` (`rectangle`, `ellipse`, `diamond`, `text`, `note`), `color` (`blue`, `green`, `yellow`, `red`, `purple`, `gray`, `note`), `frame`, `group`, `link`, `icon` (URL), `roughness` 0/1/2, `strokeStyle` `solid`/`dashed`/`dotted`.
- Edge: `from`, `to` (required), `label`, `dashed`, `head` (`arrow`, `triangle`, `bar`, `dot`, `none`).

`node scripts/inspect.mjs lint <file>` checks a plain file's ids, two-way bindings and overlaps; it refuses `compressed-json`, which the plugin writes once a drawing has been opened.

What the CLI cannot do (elbow arrows, Mermaid-to-elements, embedded notes and pages, frontmatter keys) goes through a trusted EA script, as `excalidraw-plugin.md` describes, only in a disposable or approved vault. `obsidian eval` is synchronous: start an async call that stores its result on `window`, then read it in a second call. Opening a drawing makes the plugin re-save it compressed, so never hand-edit the compressed block.

Icons for named services stay URLs (`icon` in the spec); never save an image in the vault, and say it loads from a third party on first open.

## Pele

A diagram inside a note is a `mermaid` fence. On Obsidian 1.15+ Pele draws it, so correct syntax is the work and a probe only confirms it.

- `pele` and `loadMermaid` are not globals. Run `ExcalidrawAutomate.obsidian.loadMermaid()` first; then `window.pele.render(src)` is synchronous and throws on a parse error.
- Without the Excalidraw plugin, open the note in a preview tab and count `svg.pele`; a failed block shows as text beginning "Parse error".
- The commands are in [`references/pele.md`](references/pele.md), with no second copy here. Its "Syntax pitfalls" section is what to check when a block fails; [`references/pele-catalog.md`](references/pele-catalog.md) has copy-ready blocks and [`references/pele-compatibility.md`](references/pele-compatibility.md) the version gate for beta prefixes.

Extras (the `excalidraw-extras` companion plugin) adds two things to a drawing: Mermaid converted to editable elements, when the user wants to hand-edit a Mermaid diagram, and LaTeX for math. Otherwise use a Pele fence. Its absence is normal; install it only when asked. Details are in `excalidraw-plugin.md`; `pele.md` does not own them.

## Evidence ladder

Report the highest level actually reached; a lower one never stands in for a higher one.

| Level | Proves | Produced by |
| --- | --- | --- |
| A static | Structure is sound: unique ids, mirrored bindings, finite geometry, grammar by the rules | `inspect.mjs lint`, `draw.py`'s own readback, the schema, reading the source |
| B readback | The intended bytes are at the intended path and parse | `read source=disk`, re-reading the file |
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
