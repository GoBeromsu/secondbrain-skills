# Designing drawings that carry the argument

Boxes joined by arrows only say "these things exist". Fix the structure of the whole drawing from what the idea does, then write labels. A drawing should show at least one real value (a field name, an endpoint, a sample row) so a reader learns something the surrounding text does not.

## Structure from the idea

| What the idea does | Arrangement |
| --- | --- |
| One thing feeds several | Fan-out: one anchor, arrows to targets sharing an `x` |
| Several become one | Convergence: sources stacked left, arrows meeting one tall receiver |
| Steps in order | Timeline: one `line` spine, small `ellipse` dots, free text beside each |
| Parent and child | Tree: trunk `line`, short branch `line`s, free text |
| Repeats | Cycle: nodes on a ring, the last arrow closes it, the loop named in the middle |
| Input becomes output | Assembly line: irregular pile left, one labelled step, aligned result right |
| Two options, before and after | Side-by-side: two columns, a dashed divider, identical rows |
| Layers or zones | Zones: a dashed `rectangle` per zone, its name top-left |
| Who says what, when | Sequence: participants on top, dashed lifelines, horizontal arrows down |
| One topic, many branches | Mind map: centre `ellipse`, one hue per branch |
| Screen layout | Wireframe: outer frame, grey blocks, one coloured action |
| A phase change | Gap: extra whitespace and a dashed divider, left empty |

When one drawing holds several ideas, give each a different arrangement; a grid of identical cards means no structure was chosen. Judge a layout by covering the text: the arrangement alone should still suggest branching, merging, looping or before/after.

## Boxes

Text is free by default. A shape is for something an arrow lands on, a shape whose form carries meaning (diamond for a decision, ellipse for start or end), or a container of other elements. Titles, annotations, tree labels and timeline labels stay unboxed; size and colour rank them.

## Real values and zoom

Put the evidence in a small neutral `rectangle` with `fontFamily` 3 text (fixed width, observed) beside the box it explains, tied by a thin dashed line: a three-line payload, an endpoint, a sample row. Synthetic values only. Layer the drawing for three reading distances: a one-line flow, labelled zones, then detail inside the zones; a small drawing needs the first two.

## What to look at

Open the one that matches the design problem before choosing; each is a picture to look at, not a template to copy.

| To decide | Look at |
| --- | --- |
| Colour restraint and neutral structure | the previews in https://github.com/excalidraw/excalidraw-libraries |
| A small repeated icon set | the communication and domain-storytelling icon previews there |
| Decision flows with coloured Yes and No exits | the decision-flow-control preview there |
| Type scale and section pills | the system-design template preview there |
| Hand-drawn flow with arrow-coloured edge labels | the sketchy-flow image at https://robtaylor.github.io/excalidraw-diagrams/ |
| Dense node graphs on a dark canvas | the mind-map views in the README of https://github.com/zsviczian/obsidian-excalidraw-plugin |

Rules that hold across them: one hue per meaning; edge labels on the arrow in the arrow's own colour; numbered section pills with a dashed rule and whitespace between phases; icons labelled and never decorative; a diamond kept neutral while its exits are coloured. A shaft that runs through a node or a label that collides with a line is the defect to look for in every gallery image, including your own.

Sketch fonts and `roughness: 1` suit informal and teaching drawings.

## Palette

Six pairs, one neutral and five with a meaning; use at most four in one drawing. Pale fill with the darker stroke of the same hue stays legible on light and dark canvases. Prefer `fillStyle: "solid"`; hachure muddies small shapes.

| Meaning | `backgroundColor` | `strokeColor` |
|---|---|---|
| Normal step, service | `#a5d8ff` | `#1971c2` |
| Start, success, output | `#b2f2bb` | `#2f9e44` |
| Decision, caution | `#ffec99` | `#f08c00` |
| Error, risk | `#ffc9c9` | `#e03131` |
| Data store, memory | `#d0bfff` | `#6741d9` |
| External actor, neutral | `#e9ecef` | `#495057` |

Text inside pale fills stays `#1e1e1e` or the stroke hue. On a dark canvas, free text uses `#e9ecef` and structural lines `#868e96`. Spend one accent color once, on the thing the reader must not miss.

## Type scale and spacing

| Role | `fontSize` |
|---|---|
| Title | 36 |
| Zone or section name | 28 |
| Node label | 20 |
| Annotation, edge label | 16 |
| Never below | 14 |

- Width estimate: about one font size per CJK character, 0.55 per Latin character. Rendered fonts run wider: keep 48 px side padding and break long labels with `\n`.
- Snap to multiples of 20; same column shares `x`, same row shares `y`.
- Sizes: standard 200x80, compact 140x60, marker dot 14x14, decision diamond 220x120; the focal element is about one and a half times the standard box.
- Gaps: 60 px or more for plain arrows. A labelled arrow needs a gap wider than the label itself, estimated by the width rule above.
- The focal element gets 200 px of clear air; supporting detail packs tighter.
- Flow left to right or top to bottom; radial only for hub-and-spoke.
- `roughness: 1` suits brainstorming and notes; `0` suits specs. Pick one per drawing.

## Recipes

Each recipe was submitted through the plugin's `create` on a disposable vault (plugin 2.29.1) and its exported PNG was looked at. Styling fields (`strokeColor`, `backgroundColor`, `fillStyle`, `strokeStyle`, `roughness`, `roundness`, `fontSize`, `fontFamily`, `points`, `label`) are in the live `schema action=create`; `label` accepted `{text, fontSize}`.

Facts that bit during testing:

- A bound arrow still needs `points`. With only `start`/`end` it drew a short stub in the wrong place. Set `x,y` to the start point and `points: [[0,0],[dx,dy]]` to the end point; the plugin then snaps both ends to the shapes.
- Text-only `text` elements are free; bound labels use `label.text`.
- A `frame` is moved and resized around its `children` and clips anything that is assigned to it, including an arrow that ends inside it. For arrows that cross zones use a dashed `rectangle` plus a `text` name, as in the zone recipe.
- Frame `x,y` should equal the children's top-left minus 10; place children at the coordinates you want and size the frame to wrap them.

Notation: `box(id,x,y,w,h,"Label",color)` is a skeleton `rectangle` with `label`, solid fill and the palette pair; `a(from,to,x,y,dx,dy)` is an `arrow` with `start`/`end` ids and `points [[0,0],[dx,dy]]`; `t(x,y,"text",size)` is a free `text`; `l(x,y,[[0,0],[dx,dy]])` is a `line`.

**Fan-out.** `ellipse` hub `(0,160,160,80)` "Order placed". Targets `box` at `x=320`, `y=0/160/320`, `200x80`, one color per role. Arrows start `(160,200)`, `dx=160`, `dy=-160/0/160`.

**Convergence.** Sources `(0,n*160,160,80)`. Receiver `(360,100,200,240)`. Arrows start `(160,n*160+40)`, `dx=200`, `dy=180-n*160`. Output `ellipse (680,180,160,80)` with an arrow `(560,220)`, `dx=120`.

**Timeline.** Spine `l(0,0,[[0,0],[0,420]])`. Dots `ellipse 14x14` at `(-7, n*140-7)` filled `#1971c2`. Step name `t(32,n*140-14,.,20)`, grey 16 px date under it at `+28`. No boxes.

**Tree.** Root `t(0,0,.,24)`. Trunk `l(12,40,[[0,0],[0,200]])`. Each child: a 24 px horizontal `line` at its row and `t` 36 px further right per level; row pitch 40.

**Cycle.** Nodes `160x64` at `(0,0)`, `(280,0)`, `(280,160)`, `(0,160)`. Arrows `(160,32)` `dx=120`; `(360,64)` `dy=96`; `(280,192)` `dx=-120`; `(80,160)` `dy=-96`. Grey loop name at `(86,100)`.

**Assembly line.** Dashed `rectangle (-20,-20,220,230)` holding five unlabelled grey boxes of different sizes at irregular offsets, captioned "raw" above. `box (320,40,200,120)` "Normalize". Right: five identical green `60x32` boxes at `x=640`, pitch 44, captioned "clean". Arrows `(200,100)` `dx=120` and `(520,100)` `dx=120`.

**Side-by-side.** Headers `t(0,0,.,28)` and `t(420,0,.,28)`. Divider dashed `line` at `x=380`, height 300. Rows `300x56` at `y=80+n*80` in both columns; color only the cells that differ.

**Zones.** Dashed `rectangle (x,0,300,200)` `strokeColor #868e96` with a grey 16 px `t(x+16,12)` name. Members at `(x+50,70,200,80)`. Cross-zone arrow starts at `(250,110)`, `dx=200`.

**Sequence.** Participants `box` `160x56` at `x=0/280/560`. Lifelines dashed `line` from `(x+80,56)` down 300. Messages are free `arrow`s with `points [[0,0],[dx,0]]`, `label` 16 px, `y` pitch 50, replies `strokeStyle: "dashed"`. Past five participants or fifteen messages, use Mermaid instead.

**Mind map.** Centre `ellipse (0,0,180,90)`. Branches `160x60` on a radius of about 300 at 45, 135, 225, 315 degrees snapped to 20, one hue each. Arrows run from the centre (`90,45`) to each branch centre.

**Wireframe.** Outer `rectangle (0,0,320,560)` no fill. Grey blocks inside with 20 px margins: header `(20,20,280,56)`, image `(20,96,280,160)`, cards `(20,276,280,72)`, `(20,368,280,72)`. One blue button `(60,468,200,56)`; it is the only color.

## Fidelity to the request

Go through the request sentence by sentence and match every stated relationship to one arrow's source and target, before exporting. "Order reads Postgres on a cache miss" is an arrow from Order to Postgres, labelled, even if routing it through Redis looks tidier. A route that changes who talks to whom misinforms the reader, so a tidy layout never outranks the stated edge. Then check the reverse: no arrow exists that no sentence supports.

Labels follow the user's language; the user's own proper names, product names and code identifiers stay as written. A Korean request gets Korean labels, with `Redis` and `Postgres` left alone.

## When the user asks for a sketch

A request for a sketch, hand-drawn look or 손그림 changes the look, not only the font. Clean boxes at default roughness are the wrong answer. Choose in this order:

- `roughness` 2 on every shape and arrow; `fillStyle` `hachure` for fills.
- Vary shapes by meaning (ellipse, diamond, rectangle) rather than one box type.
- A loop must curve: give the closing arrows three `points` with `roundness: {"type": 2}`, and place the nodes on a ring, not a square grid. Observed: a four-node loop with such arrows rendered as a curved ring.
- Lines and connectors curved or slightly bent, free title text, unequal spacing.
- `fontFamily` and `fontSize` on a shape go inside its `label`, not on the shape; the CLI rejects them on the shape.

For hand-style Korean set `fontFamily` 5 and check the export: it is the only family whose Hangul is hand-style on plugin 2.29.1 (visual reading; the per-family table and its network note are in [`excalidraw-plugin.md`](excalidraw-plugin.md)). Family 4 with a local font was not tried. `scripts/draw.py` hard-codes family 2 and its spec has no font field, so its Hangul should be that plain sans (inferred from family 2; no `draw.py` Hangul render was looked at). Use node `roughness` and shapes there, or create the drawing through the CLI when you need more of the sketch look: `draw.py` edges take no `roughness` or curve.

## Sticky notes

A `stickynote` made through the CLI always carries a date stamp (such as `6 Nov`); the CLI has no field to remove it, a `date` key is rejected, and the stamp is not a separate element `apply delete` can remove. `ea.addStickyNote` stamps it too. A raw `stickynote` element in a file written by `scripts/draw.py` had no stamp on a disk export and after opening and exporting live; the cause is unknown. For a dateless note through the CLI, draw a yellow `rectangle` with `label`.

## Fixing a drawing

`create` never overwrites, so do not delete and recreate. `open` the drawing, `read source=live` for the `revision` (detail `elements` lists ids), then `apply` with `expectedRevision`. Observed: one `apply` combining `update` (colour and roughness), `delete` and `add` succeeded, `saveStatus` was persisted, `read source=disk` showed the changes, a moved element's bound label moved with it, and deleting a shape also removed its bound text. Use the real ids from the read. For a redesign rather than a fix, `create` a new path. Operation fields are in [`excalidraw-plugin.md`](excalidraw-plugin.md).

## Render, look, fix

Rendering is the plugin's own export; judge the exported image. After each pass:

1. Run the fidelity check above, then compare to the intent: does the structure show the chosen pattern, does the eye enter at the focal element and leave at the result?
2. List defects and fix them all before re-exporting: clipped text; an arrow through a node; an edge label touching a node; an arrow ending in empty space; arrows drawn as stubs (missing `points`); uneven gaps; one cramped region beside a void; text under 14; more than four palette pairs; a box that could be free text.
3. Stop when you would show it without caveats, usually after two to four passes. Build large drawings zone by zone in separate batches.
