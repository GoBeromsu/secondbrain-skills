# Excalidraw plugin features

Labels: **observed** means run on plugin 2.29.2 under Obsidian 1.15.1 and read back or rendered; **documented** means taken from the plugin documentation or typings and not run here. A documented feature stays unverified until it is run.

Contents: surfaces, CLI, skeleton fields, features, styles, frontmatter, export, EA methods, feature-to-surface table.

## Surfaces

| Surface | Needs | Use for |
| --- | --- | --- |
| `scripts/draw.py` | Python 3 | the only offline writer: a new plain-JSON drawing from a spec |
| `scripts/export.py` | Python 3, plugin CLI | PNG export to a path outside the vault, for looking |
| Plugin CLI | Obsidian 1.12.2+, plugin enabled, CLI on | create, edit, read, export; the default |
| Trusted EA script | `trusted=true`, a vault `.md` script | anything the CLI rejects: elbow arrows, Mermaid, embeds, custom data |

## CLI

The plugin ships its own guide and schemas; they are authoritative and match the installed version. Run them instead of relying on a copy here:

- `obsidian vault=<v> obsidian-excalidraw-plugin:skill` for the protocol (loop, `requestId`, receipts, `idMap`, revisions, failure codes).
- `obsidian vault=<v> obsidian-excalidraw-plugin:schema action=<create|export|apply|read|...>` for fields, limits and an example per command (an example block does not mean anything ran).
- `icons query=<word>` for Lucide names; `api surface=ea name=<method>` for EA signatures.

Facts observed here (plugin 2.29.2, Obsidian 1.15.1) that those texts do not state:

- Every write needs a `requestId` (`^[A-Za-z0-9_.-]{1,80}$`); a changed request under a used id fails, so use a fresh unique id per attempt. Check `ok`, `mutation` and `persistence`; exit code zero proves nothing.
- Limits: 500 skeletons and 2 MiB per request; export is capped at 16,000,000 pixels, so pass `maxWidth` (`export.py` does).
- `export` `out` must be a visible vault-relative `.svg` or `.png` (no leading dot, no absolute path). Copy the file out and delete it, or use `export.py`.
- `status` reads `ready` false until a drawing view is open; `create` and `icons` work before that.
- `create` never overwrites; fix an existing drawing with `apply` (open it, `read source=live`, pass `expectedRevision`).
- Never edit the compressed drawing markdown by hand; opening a drawing makes the plugin re-save it compressed.
- A file written from outside the app may be missing from the vault for about two seconds. After writing an input JSON into the vault, confirm it is indexed (`obsidian vault=<v> file path=<json>`) before `create input=<json>`, which otherwise fails `NOT_FOUND`. Get help from `:skill` and `:schema`, not `--help`.

### Skeleton notes

- Text inside a shape or sticky note goes in `label: {"text": "..."}`; `text` there is rejected. Free `text` elements use `text`.
- `arrow`/`line`: `points` are offsets from `x`,`y`. `start`/`end` bind to skeleton ids.
- `frame`: `name` is the title, `children` lists member ids; it cannot nest and clips children, so size it to contain them.
- `stickynote` always carries a date stamp; width is honoured, height has a minimum of 75.
- Arrowhead `dot` is rejected by the CLI, but a `dot` value written by `scripts/draw.py` renders as a filled dot.
- `elbowed` is rejected: "use a trusted EA script".
- `connect` op made a bound arrow that was unlabeled and crossed shapes in between; check the render.
- `latex` op needs Extras; without it the call fails `DEPENDENCY_UNAVAILABLE`.
- `image` op takes an image that already lives in the vault. It is not for web images: see Images below.

## Features

- **Lucide icons**: `icons` array in `create` or `{"op":"lucide",...}` in `apply`: `{"id":"ic","icon":"database","x":40,"y":120,"size":64,"roughness":0}`. Optional `strokeColor`, `strokeWidth`, `opacity`. Find names with `icons query=<word> limit=50` (names come back as `lucide-<name>`; pass the plain name). The icon becomes a group of editable line elements; `groupMap[id].elementIds` lists them and the group id cannot be used as a binding target. No network, no Extras. Observed.
- **Frames**: above. Observed. A frame name can be linked or styled only by script.
- **Sticky notes**: above; script form `ea.addStickyNote(x, y, text, {width, height, fontSize, textAlign})`. Observed (CLI and script).
- **Groups**: `group` op returns a group id; `ungroup` needs `ids` and `groupId`. Documented. Icons come grouped. Observed.
- **Images**: only an image that already lives in the vault is referenced as a vault file (`image` op, or `ea.addImage(x, y, path, scale)`). An external image (logo, icon, web screenshot) stays a URL in the drawing's Embedded Files, as `draw.py` `icon` writes it; never download it into the vault. To check layout offline, run `export.py --placeholder-images`; otherwise export live with network. Tell the user it loads from a third party on first open.
- **LaTeX**: `latex` op or `ea.addLaTex(x, y, tex)`; needs Extras MathJax (MathJax component 1.1.0 or newer, documented). Observed through the CLI op.
- **Mermaid to elements**: `ea.addMermaid(source, true)` inside a trusted script, then `await ea.addElementsToView(false, true, true)`. With Extras 0.2.0 a flowchart (3 nodes, labelled edges, a back edge) became 11 editable elements and rendered readable in the PNG; it lands at the origin or cursor, so place other content away from it or move it. Without Extras it returns the string "Mermaid to Excalidraw requires the Excalidraw Extras companion plugin." Observed both. Extras bundles Pele as its parser, not the Mermaid library. `versions.mermaid` reads 3.0.0 in the installed bundle; from static reading it is a contract version, not a library version. Mermaid conversion needs Extras component 3.0.0 (documented). Other diagram kinds: documented only. Not a CLI operation: `{"op":"mermaid"}` is "Unsupported operation". Observed. Rendering a Mermaid code block in a note is a separate path owned by the Pele guidance in this package.
- **Embedded notes, web pages, transclusions**: `ea.addIFrame(x, y, w, h, url, file, html)` creates an embeddable element for a URL, a vault file, or raw HTML. Documented. Not available through the CLI.
- **Element links**: the `link` field takes a wiki link such as `[[Note]]`, `[[Note#Heading]]`, `[[Note#^blockid]]`, or a plain URL; the CLI accepts `link` in `update` and as a skeleton key. Accepting the field is documented; link navigation is not verified here.
- **Fonts**: for `fontFamily` 1 to 9 Latin is hand-drawn in 1, 5 and 8, bold in 7, sans in 2, 4, 6 and 9, and a rounder sans in 3 (visual readings); 5 is the only hand-style Hangul, as free text and as a shape label (the export was byte-identical from disk and live and unchanged after the first live `apply`); 1, 2, 3 and 8 share one plain sans face (first syllable pixel compared at x3: 1 and 2 identical, 3 and 8 under 4% different from 1, 5 about 41% different), and the other families, read only from an older, smaller probe, look sans (visual reading). In the app, family 5 Hangul came with Xiaolai woff2 requests to `esm.sh` (a new drawing with rare syllables added 2 requests; observed). Settings `loadKoreanFonts` and `fontAssetsPath` exist, with setting text about rendering CJK without an internet connection (documented from `main.js`); behaviour with no network was not tested. By stored width only 3 and 8 are fixed-width (observed).
- **Roundness**: `roundness: null` gave square corners; omit for rounded. Observed. `strokeWidth` 4, `fillStyle` `cross-hatch`, `opacity` 60 rendered. Observed. `hachure` and `solid` fill also rendered. Observed.
- **Dashed and dotted**: `strokeStyle` `dashed` rendered on a diamond and an arrow. `dotted`: documented.
- **Roughness**: 0 architect, 1 artist, 2 cartoonist. 0 observed on an icon.
- **Elbow arrows**: only through `ea.connectObjects(a, pointA, b, pointB, {elbowed: true})` or `addArrow`-family script calls. Typings show `elbowed` in `connectObjects` formatting. Documented.

## Per-file frontmatter keys

Set in the drawing's YAML frontmatter (documented, none run here): `excalidraw-plugin: parsed` (required marker), `excalidraw-export-transparent`, `excalidraw-export-dark`, `excalidraw-export-padding`, `excalidraw-export-svgpadding`, `excalidraw-export-pngscale`, `excalidraw-export-embed-scene`, `excalidraw-export-internal-links`, `excalidraw-autoexport` (none, both, png, svg), `excalidraw-default-mode` (view, zen), `excalidraw-font`, `excalidraw-font-color`, `excalidraw-border-color`, `excalidraw-css`, `excalidraw-link-prefix`, `excalidraw-url-prefix`, `excalidraw-link-brackets`, `excalidraw-linkbutton-opacity`, `excalidraw-onload-script`, `excalidraw-embeddable-theme`, `excalidraw-iframe-theme`, `excalidraw-open-md`, `excalidraw-embed-md`, `excalidraw-mask`. `create` keeps the template's frontmatter; it has no key for setting these, so a trusted script sets them.

## Export

- CLI `export`: SVG or PNG, vault-relative `out`, `source=live|disk`, `theme`, `padding`, `scale`, `area`. Exports follow the `theme` parameter (`dark` or `light`), not the app theme. Observed. With `theme` omitted, a live export followed the view's theme (a view set to dark gave dark under either app theme; a freshly reopened view gave light), and a disk export of a closed drawing gave light under either app theme, on a file stored light. Disk behaviour for a stored dark theme is unknown, because saving a dark view still read back light. Source reading, not run on that branch: `theme ?? (view ? view.getViewExportTheme() : scene.appState.theme ?? "light")` in `src/core/cli/cliExport.ts`. Pass `theme` when it matters. A disk export of an unopened drawing worked and returned bytes, size and a scene-to-preview map. Observed.
- Looking at the result: `python3 scripts/export.py <drawing>` writes the PNG outside the vault and prints its path; open it with an image viewer; a successful export proves the file exists, not that the layout reads well. Observed.
- Script: `await ea.createSVG(templatePath, embedFont, exportSettings, loader, theme, padding)`, `ea.createPNG(...)`, `ea.createPNGBase64(...)`, `ea.createPDF(...)`. Documented; `createPDF` is covered under Needs.

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

- Extras plugin (community plugin id `excalidraw-extras`, plugin 0.0.15 or newer required, documented): Mermaid-to-Excalidraw, LaTeX, PDF printing (documented, but it failed when run on plugin 2.29.1 with Extras 0.2.0), file access outside the vault. Installing it in a vault changes that vault, so do it only when the user asks: `plugin:install id=excalidraw-extras enable` installed 0.2.0 and enabled it in the test vault with restricted mode off. Observed. `ea.createPDF` through a trusted script produced no PDF on plugin 2.29.1 with Extras 0.2.0: with only `scale` it threw "Cannot read properties of null (reading 'settings')", and with `pageProps` the promise hung for over 45 s, no file appeared and the target stayed `BUSY`; what cleared it is unknown. Whether a different setup works is unknown; do not offer it as a working path. Outside-vault access has no CLI operation and was not run.
- Network: external images (URL) and web embeds; Lucide and core shapes need none.
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
| Vault images (already in the vault) | no | `image` op | `addImage` |
| External image by URL | `draw.py` `icon` | no | script |
| LaTeX | no | `latex` (Extras) | `addLaTex` (Extras) |
| Mermaid conversion | no | no | `addMermaid` (Extras) |
| Embedded notes and pages | no | no | `addIFrame` |
| Element links | no | `link` field | element `link` |
| Frontmatter keys | no | no | yes |
| SVG and PNG export | no | `export` | `createSVG` and friends |
