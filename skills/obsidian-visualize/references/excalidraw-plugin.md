# Excalidraw plugin features

Labels: **observed** means run on plugin 2.29.1 under Obsidian 1.15.1 and read back or rendered; **documented** means taken from the plugin documentation or typings and not run here. A documented feature stays unverified until it is run.

Contents: surfaces, CLI, skeleton fields, features, styles, frontmatter, export, EA methods, feature-to-surface table.

## Surfaces

| Surface | Needs | Use for |
| --- | --- | --- |
| `scripts/draw.py` | Python 3 | the only offline writer: a new plain-JSON drawing from a spec; never edit the compressed block by hand |
| Plugin CLI | Obsidian 1.12.2+, plugin enabled, CLI on | create, edit, read, export; the default |
| Trusted EA script | `trusted=true`, a vault `.md` script | anything the CLI rejects: elbow arrows, Mermaid, embeds, custom data |

Every CLI call is `obsidian vault=<name> obsidian-excalidraw-plugin:<command> key=value`, vault first. Check `ok`, `mutation` and `persistence` in the JSON reply; exit code zero proves nothing. Observed.

## CLI

Commands: `help`, `status`, `schema action=<cmd>`, `list`, `read`, `open`, `create`, `apply`, `export`, `result`, `icons`, `api`, `script`, `skill`. `schema` returns the exact JSON schema, limits and an example per command (an example block, such as in `schema action=export`, does not mean anything ran); read it before authoring. Observed for all except `list`, `result`, `skill`.

- `status`: `ready`, `lucideIcons` and `converter` read false until a drawing view is open; with Extras installed all three were true after `open`. Observed. `icons` and `create` worked before that. Observed.
- `create`: needs `apiVersion:1`, `requestId`, `path` (exact, with `.excalidraw.md`), optional `elements`, `icons`, `template`. Never overwrites: replaying with a used `requestId` or an existing path fails with a terse error, so use a new id and a new path, or the update surface. Observed.
- `apply`: needs `expectedRevision` from a `read source=live`, so the drawing must be open (`open path=...`). It holds one to 100 operations. Observed.
- `read`: `source=disk` works on a closed drawing and returns counts per type; `source=live` returns the `revision`; `detail=elements` pages 50 at a time. Observed for summary, documented for `detail`.
- `export`: `out` must be a visible vault-relative `.svg` or `.png`; an absolute path was rejected with `INVALID_INPUT`. Copy the file out afterwards, taking the vault's disk path from `vault info=path`. Observed. Options `theme`, `padding` 0-200, `scale` 0.1-4, `area`, `overwrite=true`, size caps: documented. Re-export over an existing file with `overwrite=true` succeeded; refusal without it is documented.
- `open` creates a tab. Close it when finished; deleting the drawing file closed it. Observed.
- Large requests go in a vault JSON file passed as `input=`; a file just written from outside the app was not found for about two seconds, so retry once. Small requests use inline `json=`; give not both. Observed.

### Request rules

- `requestId`: 1 to 80 characters of letters, digits, `_`, `.`, `-`. Replaying identical content returns the stored receipt; the same id with different content fails `INVALID_INPUT`, so a corrected request needs a new id. Observed. Receipts last 15 minutes, 128 at most; `result requestId=<id>` recovers a lost reply (documented).
- Skeleton `id` values are local labels. The reply `data.idMap` maps each to the real eight-character id; use the real ids in later `apply` calls. Omitted ids become `@0`, `@1`. Observed.
- Stale guard: `apply` with an old `expectedRevision` fails `STALE_REVISION` and changes nothing; re-read and rebuild. Observed.
- Limits (documented): 2 MiB input, 500 skeletons per batch, 100 operations, 100 points per line, 5000 scene elements, 100 icons per request, 512 KiB output.
- Failure codes seen: `INVALID_INPUT` (with `field`), `STALE_REVISION`, `DEPENDENCY_UNAVAILABLE`, `NOT_FOUND`, `OUTCOME_UNKNOWN`. Documented extras: `BUSY` (retry with the same `requestId` only if refused before it ran), `NOT_READY`, `TRUST_REQUIRED`, `INTERACTION_REQUIRED`, `INTERNAL_ERROR`. After `OUTCOME_UNKNOWN` read the drawing back before retrying.

### Skeleton fields (create `elements`, apply `add`)

Types: `rectangle`, `ellipse`, `diamond`, `text`, `arrow`, `line`, `frame`, `stickynote`. Observed all eight.

Allowed keys (the schema rejects others with `INVALID_INPUT` naming the field): `x y width height angle strokeColor backgroundColor fillStyle strokeWidth strokeStyle roughness opacity locked link text fontSize fontFamily textAlign verticalAlign id type roundness label points start end startArrowhead endArrowhead children name`.

- Text inside a shape or sticky note goes in `label: {"text": "..."}`; `text` on a shape or sticky note is rejected with "Use label for container text". Free `text` elements use `text`. Observed.
- `arrow`/`line`: `points` is required; `x`,`y` is the origin and `points` are offsets from it. An arrow with `start:{"id":"a"}` and `end:{"id":"b"}` binds to those skeletons and a `label` sits on its midpoint. Observed.
- `frame`: `name` is the title and `children` lists member ids; a frame needs children and cannot nest. Children are clipped to the frame box, so size it to contain them. Observed.
- `stickynote`: yellow card; made through the CLI it carries an automatic date stamp in the corner. Observed.
- Arrowheads accepted: `arrow`, `bar`, `circle`, `circle_outline`, `triangle`, `triangle_outline`, `diamond`, `diamond_outline`, `null`. `dot` was rejected by the CLI ("Unknown arrowhead"); a `dot` value written to the file by `scripts/draw.py` rendered as a filled dot. Observed for `circle`, `bar`, `triangle` and the file value `dot`; rest documented.
- `elbowed` is not a skeleton field: rejected, "use a trusted EA script". Observed.

### `apply` operations

`add`, `update` (id, `set` with geometry, colors, fillStyle, strokeWidth, strokeStyle, roughness, opacity, locked, link, text and font fields; no linear resize), `delete` (`ids`; frames need `children: "delete"|"detach"`), `connect`, `group`, `ungroup`, `image`, `imageMetadata`, `latex`, `lucide`. Observed: `add`, `update`, `delete`, `connect`, `latex`. Documented: the rest.

- `connect`: `{"op":"connect","id":"cn","from":"<realId>","to":"<realId>","fromSide":"bottom","toSide":"top"}` made a bound arrow; it was unlabeled and crossed the shapes in between, so check the render. Observed.
- `latex`: `{"op":"latex","id":"lx","text":"E = mc^2","x":250,"y":0}` saved and rendered as typeset math in the export. Needs Extras; without it the call fails `DEPENDENCY_UNAVAILABLE` ("Enable a compatible Excalidraw Extras MathJax feature"). Observed both, with Extras 0.2.0.
- `image`: `{"op":"image","asset":"<vault image path>","x":0,"y":0,"scale":true}`; PNG, JPEG, GIF, WebP, SVG. Documented.

## Features

- **Lucide icons**: `icons` array in `create` or `{"op":"lucide",...}` in `apply`: `{"id":"ic","icon":"database","x":40,"y":120,"size":64,"roughness":0}`. Optional `strokeColor`, `strokeWidth`, `opacity`. Find names with `icons query=<word> limit=50` (names come back as `lucide-<name>`; pass the plain name). The icon becomes a group of editable line elements; `groupMap[id].elementIds` lists them and the group id cannot be used as a binding target. No network, no Extras. Observed.
- **Frames**: above. Observed. A frame name can be linked or styled only by script.
- **Sticky notes**: above; script form `ea.addStickyNote(x, y, text, {width, height, fontSize, textAlign})`. Observed (CLI).
- **Groups**: `group` op returns a group id; `ungroup` needs `ids` and `groupId`. Documented. Icons come grouped. Observed.
- **Images**: vault file via `image` op, or `ea.addImage(x, y, fileOrPath, scale)`; remote images need network. Documented.
- **LaTeX**: `latex` op or `ea.addLaTex(x, y, tex)`; needs Extras MathJax (MathJax component 1.1.0 or newer, documented). Observed through the CLI op.
- **Mermaid to elements**: `ea.addMermaid(source, true)` inside a trusted script, then `await ea.addElementsToView(false, true, true)`. With Extras 0.2.0 a flowchart (3 nodes, labelled edges, a back edge) became 11 editable elements and rendered readable in the PNG; it lands at the origin or cursor, so place other content away from it or move it. Without Extras it returns the string "Mermaid to Excalidraw requires the Excalidraw Extras companion plugin." Observed both. The plugin requires the Mermaid component at exactly 3.0.0 (documented, version not read from the install). Other diagram kinds: documented only. Not a CLI operation: `{"op":"mermaid"}` is "Unsupported operation". Observed. Rendering a Mermaid code block in a note is a separate path owned by the Pele guidance in this package.
- **Embedded notes, web pages, transclusions**: `ea.addIFrame(x, y, w, h, url, file, html)` creates an embeddable element for a URL, a vault file, or raw HTML. Documented. Not available through the CLI.
- **Element links**: the `link` field takes a wiki link such as `[[Note]]`, `[[Note#Heading]]`, `[[Note#^blockid]]`, or a plain URL; the CLI accepts `link` in `update` and as a skeleton key. Accepting the field is documented; link navigation is not verified here.
- **Fonts**: `fontFamily` 1 hand-drawn, 2 sans, 3 mono (older), and 5 and 6 rendered as a hand-drawn face and a clean sans face. Observed for 5 and 6; 4 is the local font setting per the typings (documented).
- **Roundness**: `roundness: null` gave square corners; omit for rounded. Observed. `strokeWidth` 4, `fillStyle` `cross-hatch`, `opacity` 60 rendered. Observed. `hachure` and `solid` fill also rendered. Observed.
- **Dashed and dotted**: `strokeStyle` `dashed` rendered on a diamond and an arrow. `dotted`: documented.
- **Roughness**: 0 architect, 1 artist, 2 cartoonist. 0 observed on an icon.
- **Elbow arrows**: only through `ea.connectObjects(a, pointA, b, pointB, {elbowed: true})` or `addArrow`-family script calls. Typings show `elbowed` in `connectObjects` formatting. Documented.

## Per-file frontmatter keys

Set in the drawing's YAML frontmatter (documented, none run here): `excalidraw-plugin: parsed` (required marker), `excalidraw-export-transparent`, `excalidraw-export-dark`, `excalidraw-export-padding`, `excalidraw-export-svgpadding`, `excalidraw-export-pngscale`, `excalidraw-export-embed-scene`, `excalidraw-export-internal-links`, `excalidraw-autoexport` (none, both, png, svg), `excalidraw-default-mode` (view, zen), `excalidraw-font`, `excalidraw-font-color`, `excalidraw-border-color`, `excalidraw-css`, `excalidraw-link-prefix`, `excalidraw-url-prefix`, `excalidraw-link-brackets`, `excalidraw-linkbutton-opacity`, `excalidraw-onload-script`, `excalidraw-embeddable-theme`, `excalidraw-iframe-theme`, `excalidraw-open-md`, `excalidraw-embed-md`, `excalidraw-mask`. `create` keeps the template's frontmatter; it has no key for setting these, so a trusted script sets them.

## Export

- CLI `export`: SVG or PNG, vault-relative `out`, `source=live|disk`, `theme`, `padding`, `scale`, `area`. A disk export of an unopened drawing worked and returned bytes, size and a scene-to-preview map. Observed.
- Looking at the result: copy the PNG out of the vault and open it with an image viewer; a successful export proves the file exists, not that the layout reads well. Observed.
- Script: `await ea.createSVG(templatePath, embedFont, exportSettings, loader, theme, padding)`, `ea.createPNG(...)`, `ea.createPNGBase64(...)`, `ea.createPDF(...)`. Documented.

## ExcalidrawAutomate for a trusted script

Run with `script path=<drawing> script=<vault script .md> trusted=true json={...,"args":{...}}`; arguments arrive as `utils.input`. The `.md` script is raw JavaScript, not a fenced block: a fenced file failed with `OUTCOME_UNKNOWN` even for `return "ok"`, and the raw body ran. Top-level `await` and `return` work. Observed. The CLI-made `ea` is already pointed at the target view. Returned data must be plain JSON. Await every write and save; completion does not prove persistence (`persistence: unknown`). Observed. Not sandboxed; use only in a disposable or approved vault.

Look up a signature with `api surface=ea name=<method>` (observed) or `api surface=lib` for the Excalidraw library subset.

- Shapes: `addRect`, `addEllipse`, `addDiamond`, `addBlob`, `addText`, `addLine`, `addArrow`, `addLabelToLine`, `addFrame`, `addStickyNote`.
- Connections: `connectObjects` (options include `elbowed`, arrowheads, `numberOfPoints`), `addToGroup`.
- Content: `addImage`, `addLaTex`, `addMermaid`, `addIFrame`, `addLucideIcon`.
- Style: `style` object, `setFillStyle`, `setStrokeStyle`, `setFontFamily`, `setStyle`.
- Scene: `setView`, `getViewElements`, `getViewSelectedElements`, `copyViewElementsToEAforEditing`, `addElementsToView(reposition, save, onTop)`, `deleteViewElements`, `getElement`, `elementsDict` for custom fields.
- Layout: `getBoundingBox`, `getMaximumGroups`, `getElementsInFrame`, `measureText`.
- Output: `createSVG`, `createPNG`, `createPNGBase64`, `createPDF`, `toClipboard`.
- Lifecycle: `create` (write a new drawing file), `clear`, `reset`, `ea.obsidian` for the Obsidian API, `getExcalidrawAPI` for the live scene.

## Needs

- Extras plugin (community plugin id `excalidraw-extras`, plugin 0.0.15 or newer required, documented): Mermaid-to-Excalidraw, LaTeX, PDF printing, file access outside the vault. Installing it in a vault changes that vault, so do it only when the user asks: `plugin:install id=excalidraw-extras enable` installed 0.2.0 and enabled it in the test vault with restricted mode off. Observed. PDF (`ea.createPDF({SVG, scale, pageProps, filename})`) and outside-vault access have no CLI operation and were not run: documented only.
- Network: remote images and web embeds; Lucide and core shapes need none.
- Trusted script: elbow arrows, Mermaid, embeds, frontmatter edits, custom data, linear resizing, binding edits.
- Nothing extra: shapes, text, arrows, lines, frames, sticky notes, Lucide icons, groups, vault images, SVG and PNG export.

## Feature to surface

| Feature | Offline writer | Plugin CLI | EA script |
| --- | --- | --- | --- |
| Shapes, text, lines, arrows, labels | `draw.py` | yes | yes |
| Frames, sticky notes | `draw.py` | yes | yes |
| Lucide icons | no | yes | yes |
| Bound connectors | `draw.py` | `connect` | `connectObjects` |
| Elbow arrows | no | no | yes |
| Groups | `draw.py` | yes | yes |
| Vault images | no | `image` op | `addImage` |
| LaTeX | no | `latex` (Extras) | `addLaTex` (Extras) |
| Mermaid conversion | no | no | `addMermaid` (Extras) |
| Embedded notes and pages | no | no | `addIFrame` |
| Element links | no | `link` field | element `link` |
| Frontmatter keys | no | no | yes |
| SVG and PNG export | no | `export` | `createSVG` and friends |
