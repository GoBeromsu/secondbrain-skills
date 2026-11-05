---
name: obsidian-visualize
description: Chooses the visual form for vault knowledge and builds it — a JSON Canvas of existing notes, a .excalidraw.md drawing, or a mermaid block rendered by Pele (Obsidian 1.15+ draws Mermaid with Pele). Use for an architecture, data-flow, pipeline, sequence, dependency or status diagram; a flowchart, sequence, class, state, ER, gantt, journey, pie, mindmap, timeline, sankey, kanban, treemap, architecture, xychart, swimlane, gitGraph, quadrant or C4 block; a mermaid block showing a parse error, raw text or an empty box in Reading view or Live Preview, or working in mermaid.live but not in the vault; a beta prefix needing a version-gated fallback; generating, replacing, inspecting, importing, editing or rendering Excalidraw in Obsidian, including plugin Mermaid import; or deciding between Canvas, Excalidraw, Pele and a plain table. 플로우차트·아키텍처도·개념도·머메이드·펠레. Not for JSON Canvas schema details, note prose and properties, or installing a plugin — use obsidian-canvas, obsidian-markdown or obsidian-cli.
license: MIT
---

# Obsidian Visualize

Pick the visual form the evidence supports, then produce the file that carries it — a diagram is a file with a documented shape, not a runtime object that needs a plugin to exist.

Done means: the form fits what is being shown, every claim in the drawing traces to inspected evidence, the drawing is a new file unless changing a named one was asked for, its references resolve, readback proves the intended bytes landed, and the report says exactly which evidence level was reached instead of implying a picture was seen.

## Choose the form first

| What the nodes are | Form | Why |
| --- | --- | --- |
| Existing vault notes to navigate — a map of content, a reading path, a note dependency map | **JSON Canvas** (`.canvas`) | Nodes are file references; clicking one opens the note |
| Free shapes with no backing note — architecture, data flow, deployment, status cards, labelled routes | **Excalidraw** (`.excalidraw.md`) | Arbitrary geometry, styling, bound labels, frames |
| A small structural diagram that belongs *inside* a note's prose | **Pele diagram** (a `mermaid` fence) | Travels with the note; no attachment to manage; Obsidian 1.15.0+ draws it with Pele in the vault theme |
| Values, comparisons, ordered attributes | **Markdown table** | A table that answers the question beats a diagram that decorates it |

This is a decision, not a fallback ladder. Do not deliver a Canvas because Excalidraw geometry looked tedious, and do not deliver an Excalidraw drawing of note titles when the user wants to click through to the notes. If the request names a form, that form is the answer unless it cannot carry the content — then say so before switching.

This package owns three branches: Canvas, Excalidraw and Pele. `obsidian-canvas` owns the `.canvas` node/edge schema, colors, and ID rules; `obsidian-markdown` owns note prose, links, and properties. This package owns the choice above, Excalidraw authoring, Pele diagram source, and the vault-specific checks in the workflow below. Compose those packages by name when the task genuinely reaches into them; nothing here dispatches to them automatically.

## Pele branch

A diagram inside a note is a ```` ```mermaid ```` fence. Since Obsidian 1.15.0 the app no longer includes Mermaid and draws that fence with Pele, Obsidian's own renderer for Mermaid 12.1.0 syntax. Follow [`references/pele.md`](references/pele.md) for the meaning-first workflow, family choice, syntax rules, fences, safe note edits, fallbacks and its own evidence ladder; [`references/pele-catalog.md`](references/pele-catalog.md) for copy-ready blocks; and [`references/pele-compatibility.md`](references/pele-compatibility.md) for the app-version gate, Pele's differences from Mermaid and the probes. The rest of this file is the Canvas and Excalidraw branches; the fence is written directly like them, without opening the note.

## CLI rule

Run packaged CLIs directly: `obsidian` (owned by `obsidian-cli`) for read-only checks and the plugin path, `python3` and `node` for this package's own files. Pele has no CLI; its in-app `pele.render()` is reached through `obsidian eval`, written into the command, not into a launcher. A script here only writes or checks this package's own artifacts or runs inside the plugin path — the drawing script, the read-only inspector and the in-app workbench payload. None of them shells out to a CLI, and none may: a wrapper, hook, launcher, queue, debounce or alias around a packaged CLI is the anti-pattern this collection forbids.

## Evidence ladder

The Canvas and Excalidraw branches make four separate claims; the Pele branch's ladder is in its reference. Never report a higher one on the strength of a lower one.

| Level | What it proves | How it is produced |
| --- | --- | --- |
| A — Author check | The file is structurally sound: unique 8-character ids, mirrored two-way references, finite geometry, JSON that parses | `node scripts/inspect.mjs lint <file>` for Excalidraw when Node exists, otherwise say it was skipped; the resolve check in workflow step 5 for Canvas |
| B — Materialized readback | The intended bytes are at the intended path and still parse | Reading the file back and parsing the `## Drawing` fence or the Canvas JSON |
| C — Runtime load | The running app indexed the file and its loader reports the expected element count, with no leaf opened | Read-only `obsidian` commands; see [Verification](#verification) |
| D — Render QA | The drawing is actually legible: no overlaps, no clipping, correct hierarchy | Exporting an image through the installed plugin and looking at it. Only on request, because it adds app round trips that A to C do not need; the image goes outside the vault |

A and B need only the filesystem; the lint also needs Node. It refuses `compressed-json`, so it works only before the drawing's first open. C needs a running target installation. If Obsidian is not running, stop at B and say so; a check does not start an app. D additionally needs the Excalidraw plugin present and a human or vision-capable reviewer looking at the export. This package cannot install or enable a plugin and carries no rasteriser: its native helper asks an already-enabled plugin to export the reloaded drawing. An SVG or PNG assembled from the same numbers, or rendered in a standalone Excalidraw app, does not prove the Obsidian plugin parses it.

When C or D cannot be reached, name the level reached and list the rest as unverified. "Validated and written" is a complete, honest result at level B. "Rendered correctly" is a lie at level B.

## Workflow

1. **Ground the content.** Collect the evidence for every claim the diagram will make: files at a pinned revision, note contents, measured values. Label declared configuration as declared and inspected behavior as inspected; do not merge a name-similar concept into a box because the words matched. Keep sources, assumptions and caveats in the report and draw only what the request asked to show, with no title or note unless requested, because a reader takes everything on the canvas as part of the diagram; labelling a box as declared when the request is about declared configuration still belongs in the drawing. A reference image supplies visual language only — never services, protocols, or numbers.
2. **Choose the form** with the table above, and choose the view the evidence supports (pipeline, sequence, data contract, deployment, observability). An architectural request answered with a three-box linear overview is the wrong view even when it validates.
3. **Lay it out with the script when the drawing is boxes joined by arrows.** Write a spec and run [`scripts/draw.py`](scripts/draw.py), as in [Drawing script](#drawing-script), because writing layout code or coordinates is where most of the time and tokens go. For anything else, size each box with the label formula in [`references/style.md`](references/style.md) and place it on that file's grid, because a label estimated by eye clips or overlaps.
4. **Write a new file directly** with the host's file tool, after confirming the path is empty, because the tool overwrites without warning. Excalidraw: follow the anatomy and element template below. Canvas: write the JSON; the schema belongs to `obsidian-canvas`. Pele: write the fence as [`references/pele.md`](references/pele.md) says. The drawing script does this step itself. Writing needs no running Obsidian.
5. **Check the file** (levels A and B). Excalidraw: run the lint and read the file back. Canvas: unique ids, every `fromNode`/`toNode` resolves, no two nodes overlap, and — this package's own check — every `file` node path and every wikilink target actually resolves in the destination vault. A plausible note name is not a resolved one. Fix the file and check again.
6. **Finish with a read-only CLI check** (level C), as in [Verification](#verification). Do not open the file to verify it: the plugin rewrites an opened file as `compressed-json`, which the lint then refuses, and the check does not need it.
7. **Render QA** (level D) only when asked and the plugin is present: export an image through it to a path outside the vault, look at the result for overlapping cards, clipped labels, unreadable text, and wrong hierarchy, then fix the file. A fix after the first open goes through the plugin path. [`references/workbench.md`](references/workbench.md) has the admission probe, the async handshake the CLI needs, and the reload-then-render order.
8. **Report** the path, the form and why, the evidence trail, and the highest level actually reached.

## Excalidraw file anatomy

An `.excalidraw.md` drawing is Markdown, top to bottom:

````text
---
excalidraw-plugin: parsed
---
Optional plaintext description shown in Reading view.

# Excalidraw Data

## Text Elements
Ingest ^Kh3nD0pQ

Store ^b7TqL1wR

## Embedded Files
a1b2c3d4: https://api.iconify.design/logos/google-cloud.svg

%%
## Drawing
```json
{"type":"excalidraw","version":2,"source":"https://github.com/zsviczian/obsidian-excalidraw-plugin","elements":[…],"appState":{"gridSize":null,"viewBackgroundColor":"#ffffff"},"files":{}}
```
%%
````

- `excalidraw-plugin: parsed` is the marker that makes the note a drawing.
- `## Text Elements` lists every text element: its text, a space, then `^<elementId>`, one blank line between entries. A multi-line label keeps its line breaks and ends with the marker.
- Keep the JSON `text` and the index line identical, because the index overrides the JSON on load.
- Make every element id exactly 8 characters, because the plugin re-rolls longer text ids and link-bearing element ids on load.
- Omit `## Embedded Files` when the drawing has no icon.
- The `%%` pair hides the scene from Reading view.
- The plugin can also store the scene as `compressed-json`, and with its `compress` setting on it re-saves a plain file that way after the first open. That is codec output. Never author or hand-edit it.

Observed on plugin 2.29.1: 8-character ids load unchanged, and an opened file is rewritten as `compressed-json`.

## Element template

Copy these whole, change the values, and keep the ids consistent. This is one labelled box and an arrow leaving it toward `Rect0002`:

```json
{"id":"Rect0001","type":"rectangle","x":0,"y":0,"width":200,"height":72,"angle":0,"strokeColor":"#1971c2","backgroundColor":"#a5d8ff","fillStyle":"solid","strokeWidth":2,"strokeStyle":"solid","roughness":0,"opacity":100,"groupIds":[],"frameId":null,"roundness":{"type":3},"seed":1,"version":1,"versionNonce":1,"isDeleted":false,"boundElements":[{"type":"text","id":"Text0001"},{"type":"arrow","id":"Arro0001"}],"updated":1,"link":null,"locked":false}
{"id":"Text0001","type":"text","x":94,"y":24,"width":12,"height":25,"angle":0,"strokeColor":"#1e1e1e","backgroundColor":"transparent","fillStyle":"solid","strokeWidth":2,"strokeStyle":"solid","roughness":0,"opacity":100,"groupIds":[],"frameId":null,"roundness":null,"seed":2,"version":1,"versionNonce":2,"isDeleted":false,"boundElements":[],"updated":1,"link":null,"locked":false,"text":"A","rawText":"A","originalText":"A","fontSize":20,"fontFamily":2,"textAlign":"center","verticalAlign":"middle","containerId":"Rect0001","autoResize":true,"lineHeight":1.25}
{"id":"Arro0001","type":"arrow","x":206,"y":36,"width":108,"height":0,"angle":0,"strokeColor":"#1e1e1e","backgroundColor":"transparent","fillStyle":"solid","strokeWidth":2,"strokeStyle":"solid","roughness":0,"opacity":100,"groupIds":[],"frameId":null,"roundness":null,"seed":3,"version":1,"versionNonce":3,"isDeleted":false,"boundElements":[],"updated":1,"link":null,"locked":false,"points":[[0,0],[108,0]],"startArrowhead":null,"endArrowhead":"arrow","startBinding":{"elementId":"Rect0001","focus":0,"gap":6},"endBinding":{"elementId":"Rect0002","focus":0,"gap":6}}
```

- **Free text** is the text line with `containerId: null`, `textAlign: "left"` and `verticalAlign: "top"`, at its real position. A bound label's geometry is recomputed by the plugin on load, so the box size is what must fit.
- **Arrow label** is a bound label whose `containerId` is the arrow, listed in the arrow's `boundElements`, with `fontSize` 15.
- **Frame** is the rectangle line with `type: "frame"`, a `name`, `roundness: null` and a transparent background, placed before its members; each member sets `frameId` to its id.

A **bound label** needs `containerId` on the text *and* a mirrored `{"type":"text","id":…}` entry in the container's `boundElements`; an **arrow** needs `startBinding`/`endBinding` of `{elementId, focus, gap}` mirrored as `{"type":"arrow","id":…}` on both endpoints, with `points` relative to the arrow's own origin and the first point exactly `[0, 0]`; **groups** relate elements through `groupIds`. Missing either half of a two-way reference renders wrong or breaks on reload, which is what level A checks.

## Service icons

When the request names a real service or product, show its icon in that element's box next to the text label, without being asked.

- Add `<fileId>: <url>` under `## Embedded Files` and an `image` element (the rectangle line with `type: "image"`, a transparent background and `roundness: null`) with the same `fileId`, `scale: [1, 1]` and `crop: null`. Leave the JSON `files` object empty.
- Reference by URL only and do not save the bytes in the vault; the owner keeps images out of Obsidian.
- Use the first URL that returns 200 and depicts that service: `https://api.iconify.design/{logos,simple-icons,mdi}/<slug>.svg`, then `https://cdn.jsdelivr.net/npm/@lobehub/icons-static-svg/icons/<slug>.svg`, then the service's own favicon.
- If none is found, keep a text-only box and say so; an approximated logo misidentifies the service.
- Report that the icon loads over the network from a third party on first open.

A 40-character hex `fileId`, as the plugin's own drawings use, loaded and rendered with the URL line and an empty `files` object on plugin 2.29.1. Say so when reporting an icon that was not seen rendered.

## Drawing script

`python3 scripts/draw.py <spec.json|-> <new.excalidraw.md>` lays out frames, boxes, arrows, icons and groups, writes the file and reads it back. It refuses an existing path, a box overlap, an arrow running through a box, and a broken binding, then exits 1 with the reason. On success it prints one JSON line: `path`, `sha256`, `elements`, `by_type`, `crossings`, `warnings`.

```json
{"direction":"LR","title":null,
 "frames":[{"id":"f1","label":"Payments"}],
 "nodes":[{"id":"a","label":"Ingest","frame":"f1","shape":"rectangle","color":"blue","icon":"https://api.iconify.design/logos/grok.svg","group":"g1","link":null}],
 "edges":[{"from":"a","to":"b","label":null,"dashed":false}]}
```

Only `nodes[].id`, `nodes[].label`, `edges[].from` and `edges[].to` are required, so leave out what the drawing does not need. `direction` is `LR` or `TB`; `shape` is `rectangle`, `ellipse`, `diamond` or `text`; `color` is `blue`, `green`, `yellow`, `red`, `purple`, `gray` or `note`. Output is byte-identical for the same spec, so fix the spec and rerun rather than patching the file. A non-zero `crossings` count is information, not a failure.

Write the file by hand from the template above only when the drawing is not boxes joined by arrows. Mermaid, LaTeX and embedded notes need the plugin, on the [plugin path](#live-plugin-edits-exception-path).

## Existing drawings

A new request is a new file. Changing an existing or open drawing still needs the plugin, and therefore a running Obsidian: there is no offline replace path, because the plugin discards an incoming element with a lower `version` and a drawing that has been opened may already be compressed. Use [`references/plugin-workflow.md`](references/plugin-workflow.md), which covers selected-id native edits, Mermaid addition, independent plugin readback and native export QA. Existing plugin drawings, their text indexes, frontmatter, prose and assets are not replaced with a fresh standalone scene.

The package-local tools are [`scripts/draw.py`](scripts/draw.py) (new drawing from a spec),
[`scripts/inspect.mjs`](scripts/inspect.mjs) (read-only inspection/layout lint)
and [`scripts/plugin-workbench.js`](scripts/plugin-workbench.js) (native
ExcalidrawAutomate snapshot, selected update, Mermaid addition and PNG export).
Read [`references/skeleton.md`](references/skeleton.md) for upstream shorthand
adaptation boundaries and [`references/style.md`](references/style.md) for
palette/spacing/layout recipes. Their capability mapping is in
[`source-map.json`](references/source-map.json).

Resolve exact artifact and authorized effect; inspect current bytes and live
preimages; preserve everything outside the selected ids/fields; use the selected
supported native surface; reload the exact persisted result; report actual
evidence and prerequisites; leave unresolved version/runtime facts unknown.
No default destination, standalone app lifecycle or plugin installation is added.

## Safety rules

- Producing a valid drawing is not authorization to write into a vault. Resolve the exact target path and the authorized effect first; stay read-only when either is missing.
- Back up and diff before a plugin edit; report every id it removed.
- Never author `compressed-json`, and never write a drawing through a shell redirect or stream editor.
- Never save an image in the vault: icons stay URLs, and a render export goes outside it.
- Never put a host path, vault name, account identifier, private note content, or secret into a shipped example, a frontmatter field, or an element link.
- Never click through a trust, permission, or plugin-installation dialog in the target app to make a drawing render. Report the missing layer and hand that decision to the operator.
- A failed check, an unresolved link, or an uninspected render is a partial result. Report it as a blocker, not a success.

## Live plugin edits (exception path)

Use the plugin's automation API for an authorized selected edit of a plugin-managed drawing or Mermaid insertion into that drawing. A new drawing does not belong here: in one measured comparison per size, driving the plugin took 93 to 124 s and 7,034 to 9,895 output tokens where the drawing script took 16 to 23 s and 1,446 to 2,379, and the plugin runs lost arrows on the first pass. Native workbench updates preserve the existing document instead of regenerating it.

[`references/workbench.md`](references/workbench.md) covers plugin and API admission, the build-and-persist calls, the caller-owned token handshake the CLI's synchronous `eval` requires, and the reload-then-render order that separates "the live scene looks right" from "the file on disk holds it".

## Requirements

- Python 3.9+ for `draw.py`, standard library only.
- Node.js for optional read-only `inspect.mjs` (author checks used 24.21.0). No npm dependency or build is required. `plugin-workbench.js` runs in the admitted Obsidian JavaScript context using its native EA API and Web Crypto; it has no server or browser dependency.
- Level C needs a running target Obsidian; `obsidian-cli` owns the command surface for reading back what loaded.
- Level D additionally needs the Excalidraw plugin already installed and enabled in that vault. Its absence is a normal outcome to report, not a failure to work around.
- Primary sources: the [Excalidraw plugin repository](https://github.com/zsviczian/obsidian-excalidraw-plugin) and its published [ExcalidrawAutomate API surface](https://github.com/zsviczian/obsidian-excalidraw-plugin/blob/master/docs/API/ExcalidrawAutomate.d.ts) for the drawing format and API, the [JSON Canvas 1.0 spec](https://jsoncanvas.org/spec/1.0/) for the Canvas branch, and the [Obsidian 1.15.0 changelog](https://obsidian.md/changelog/2026-10-22-desktop-v1.15.0/), the [Pele repository](https://github.com/obsidianmd/pele) and [pele.run/compatibility](https://pele.run/compatibility) for the Pele branch.
- The Pele branch needs no plugin or script. Level B needs a running Obsidian 1.15.0+ reached through `obsidian eval`; level D needs the target installation.

## Verification

Finish with `obsidian` commands, naming the vault first, so the app confirms what the file tool wrote. Each call took under 0.1 s on a 100-element drawing, so this check costs almost nothing. A new file is indexed within about 0.1 s; if the path is not found yet, retry once.

Excalidraw, level C. `getSceneFromFile` is async and `eval` is synchronous, so start it and then read the result:

```bash
obsidian vault=<name> eval code='(()=>{const r=window.__check={s:"run"};ExcalidrawAutomate.getSceneFromFile(app.vault.getAbstractFileByPath("<path>")).then(x=>{r.n=x.elements.filter(e=>!e.isDeleted).length;r.s="done"},e=>{r.e=String(e);r.s="fail"});return "ok"})()'
obsidian vault=<name> eval code='JSON.stringify(window.__check)'
```

Pele, level B. `obsidian version` gives the app and installer versions the report states. `pele` and `loadMermaid` are not globals until something loads them, and the `obsidian` module cannot be required from `eval`. Reach `loadMermaid` through the Excalidraw plugin:

```bash
obsidian vault=<name> eval code='(()=>{const r=window.__check={s:"run"};const f=app.vault.getAbstractFileByPath("<path>");app.vault.cachedRead(f).then(t=>{const b=[...t.matchAll(/```mermaid\n([\s\S]*?)```/g)].map(m=>m[1]);return ExcalidrawAutomate.obsidian.loadMermaid().then(()=>Promise.all(b.map(s=>window.pele.render(s))))}).then(a=>{r.n=a.length;r.s="done"},e=>{r.e=String(e);r.s="fail"});return "ok"})()'
obsidian vault=<name> eval code='JSON.stringify(window.__check)'
```

Without the Excalidraw plugin, open the note in a preview tab with `app.workspace.getLeaf("tab").openFile(file,{state:{mode:"preview"}})`, wait about a second, count `.mermaid svg` in `leaf.view.previewMode.containerEl`, then `leaf.detach()`.

- [ ] The chosen form matches the selection table, and the reason is stated.
- [ ] A Pele diagram also passed the verification list in `references/pele.md`.
- [ ] No script added or run here wraps a packaged CLI.
- [ ] Every box, label, and arrow traces to inspected evidence; declared configuration is labelled as declared.
- [ ] Every element id is unique (8 characters); bindings are mirrored; the lint ran or is reported as skipped.
- [ ] The drawing is a new file; existing drawings stayed on the plugin path.
- [ ] Every named real service has a URL icon that returned 200 or a reported text-only fallback; no image file was added to the vault.
- [ ] Wikilink and Canvas `file` targets resolve in the destination vault.
- [ ] The report names the highest evidence level reached (A, B, C, or D) and lists the rest as unverified.
- [ ] No host path, vault name, account identifier, or secret appears in the output.

## Attribution

The native workbench helper and plugin workflow are original work under the repository's MIT `LICENSE`. Inspection/layout lint and the skeleton/style resources are adapted from Jonghak Seo's MIT-licensed pi-extension at the pin in [source-map.json](references/source-map.json), with its full grant retained in [NOTICE](references/NOTICE). No standalone app, font, binary or Obsidian plugin is redistributed. See Git history for source facts, versions, modifications and unrun runtime checks.
