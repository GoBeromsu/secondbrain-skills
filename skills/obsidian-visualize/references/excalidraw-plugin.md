# Excalidraw plugin features

Labels: **observed** means run on plugin 2.29.2 under Obsidian 1.15.1 and read back or rendered; **documented** means taken from the plugin documentation or typings and not run here. A documented feature stays unverified until it is run.

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
- `create` rejects `strokeColor` inside `label`; set label colour with `apply` afterwards. `apply` takes 1 to 100 operations per request, and `read` returns at most 200 elements per page (`offset` with the first page's `revision`). `apply` rejects `width` or `height` on a `line` or `arrow` ("Linear resizing requires a trusted EA script"); delete and add the line instead.
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
- **Images**: a vault image via the `image` op or `ea.addImage(x, y, path, scale)`. External images stay URLs in Embedded Files (see SKILL.md).
- **Images and web embeds by URL**: `scripts/place.py` runs `ea.addImage({topX, topY, imageFile: <url>, scale: true})` and `ea.addEmbeddable(x, y, w, h, url)` in a trusted script, sets each element's `link`, and removes the script from the vault. Items: `{x, y, width, image, height?, link?}` (scaled to `width`, then down to the `height` cap) or `{x, y, width, height, embed, link?}`. Observed: JPEG, PNG and WebP previews and PNG icons export; web embeds export as a frame showing only the URL. A GitHub social preview (`opengraph.githubassets.com`) is stored as `application/octet-stream` and makes export fail with `ASSETS_UNAVAILABLE`; use an image file URL from the repository instead.
- **LaTeX**: `latex` op or `ea.addLaTex(x, y, tex)`; needs Extras MathJax (MathJax component 1.1.0 or newer, documented). Observed through the CLI op.
- **Mermaid to elements**: `ea.addMermaid(source, true)` in a trusted script, then `await ea.addElementsToView(false, true, true)`; needs Extras (without it the call returns "Mermaid to Excalidraw requires the Excalidraw Extras companion plugin."). With Extras 0.2.0 a flowchart became editable elements at the origin; move other content away. Not a CLI op (`{"op":"mermaid"}` is unsupported). Observed. A Mermaid fence in a note is Pele's, not this.
- **Embedded notes, web pages, transclusions**: `ea.addIFrame(x, y, w, h, url, file, html)` creates an embeddable element for a URL, a vault file, or raw HTML. Documented. Not available through the CLI.
- **Element links**: the `link` field takes a wiki link such as `[[Note]]`, `[[Note#Heading]]`, `[[Note#^blockid]]`, or a plain URL; the CLI accepts `link` in `update` and as a skeleton key. Accepting the field is documented; link navigation is not verified here.
- **Fonts**: `fontFamily` 1, 5, 8 are hand-drawn Latin, 7 bold, 3 and 8 fixed-width, the rest sans. 5 is the only hand-style Hangul (shape labels and free text); it fetches Xiaolai woff2 from `esm.sh` in the app. Observed.
- **Roundness**: `roundness: null` gave square corners; omit for rounded. Observed. `strokeWidth` 4, `fillStyle` `cross-hatch`, `opacity` 60 rendered. Observed. `hachure` and `solid` fill also rendered. Observed.
- **Dashed and dotted**: `strokeStyle` `dashed` rendered on a diamond and an arrow. `dotted`: documented.
- **Roughness**: 0 architect, 1 artist, 2 cartoonist. 0 observed on an icon.
- **Elbow arrows**: only through `ea.connectObjects(a, pointA, b, pointB, {elbowed: true})` or `addArrow`-family script calls. Typings show `elbowed` in `connectObjects` formatting. Documented.

## Per-file frontmatter keys

`excalidraw-plugin: parsed` is the required marker. Export, font, link and CSS keys (`excalidraw-export-dark`, `excalidraw-export-padding`, `excalidraw-autoexport`, `excalidraw-font`, ...) are documented, not run; `create` cannot set them, a trusted script can.

## Export

- CLI `export`: SVG or PNG, vault-relative `out`, `source=live|disk`, `theme`, `padding`, `scale`, `area`. Exports follow the `theme` parameter, not the app theme; with it omitted a disk export of a light-stored file is light. A dark export stores colours by `invert(93%) hue-rotate(180deg)`, so `draw.py dark: true` writes the inverse; saturated hues clip. `create`/`apply` have no scene-theme field. Pass `theme` when it matters. Observed.
- Looking at the result: `python3 scripts/export.py <drawing>` writes the PNG outside the vault and prints its path; open it with an image viewer; a successful export proves the file exists, not that the layout reads well. Observed.

## ExcalidrawAutomate for a trusted script

Run with `script path=<drawing> script=<vault script .md> trusted=true json={...,"args":{...}}`; arguments arrive as `utils.input`. The `.md` script is raw JavaScript, not a fenced block: a fenced file failed with `OUTCOME_UNKNOWN` even for `return "ok"`, and the raw body ran. Top-level `await` and `return` work. Observed. The CLI-made `ea` is already pointed at the target view. Returned data must be plain JSON. Await every write and save; completion does not prove persistence (`persistence: unknown`). Observed. Not sandboxed; use only in a disposable or approved vault.

Look up any method (`addArrow`, `connectObjects`, `addIFrame`, `createSVG`, ...) with `api surface=ea name=<method>`.

## Needs

- Extras plugin (`excalidraw-extras`): Mermaid-to-Excalidraw, LaTeX, PDF. Install only when the user asks; it changes the vault. `ea.createPDF` failed on plugin 2.29.1 with Extras 0.2.0 (threw or hung with the target `BUSY`): do not offer PDF as a working path.
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
| External image by URL | `draw.py` `icon` | no | `place.py` |
| LaTeX | no | `latex` (Extras) | `addLaTex` (Extras) |
| Mermaid conversion | no | no | `addMermaid` (Extras) |
| Embedded notes and pages | no | no | `place.py` (web), `addIFrame` |
| Element links | no | `link` field | element `link` |
| Frontmatter keys | no | no | yes |
| SVG and PNG export | no | `export` | `createSVG` and friends |
