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
| Who does what at each stage | Swimlane: stages as columns, actors as rows, the artifact they share as the middle row |
| A quantity over time, against events | Bars: one bar per period on a shared time axis, event markers as vertical dashed lines |
| Sources in the order they appeared | Source timeline: the Timeline recipe with each source's preview image under its dot |
| One topic, many branches | Mind map: centre `ellipse`, one hue per branch |
| Screen layout | Wireframe: outer frame, grey blocks, one coloured action |
| A phase change | Gap: extra whitespace and a dashed divider, left empty |

When one drawing holds several ideas, give each a different arrangement; a grid of identical cards means no structure was chosen. Judge a layout by covering the text: the arrangement alone should still suggest branching, merging, looping or before/after.

## Boxes

Text is free by default. A shape is for something an arrow lands on, a shape whose form carries meaning (diamond for a decision, ellipse for start or end), or a container of other elements. Titles, annotations, tree labels and timeline labels stay unboxed; size and colour rank them.

## Real values and zoom

Put evidence (a three-line payload, an endpoint, a sample row) in a small neutral `rectangle` with `fontFamily` 3 text beside the box it explains, tied by a thin dashed line.

Rules that hold: one hue per meaning; edge labels on the arrow; numbered section pills with a dashed rule and whitespace between phases; icons labelled, never decorative; a diamond kept neutral while its exits are coloured.

## Palette

Six pairs, one neutral and five with a meaning; use at most four of the five in one drawing. The meanings are fixed; the hues come from the source the skill's Palette step selects. Prefer `fillStyle: "solid"`; hachure muddies small shapes.

| Meaning | `draw.py` name | Theme variable |
|---|---|---|
| Normal step, service | `blue` | `--color-blue` |
| Start, success, output | `green` | `--color-green` |
| Decision, caution | `yellow` | `--color-yellow` |
| Error, risk | `red` | `--color-red` |
| Data store, memory | `purple` | `--color-purple` |
| External actor, neutral | `gray` | `--text-muted` |
| Sticky note | `note` | `--color-yellow` |

Theme colours: read the resolved variables from `document.body` with a read-only `obsidian eval` (assigning to a detached canvas context's `fillStyle` returns `#rrggbb`), plus `--text-normal` (`ink`), `--background-primary` (`background`) and `theme-dark` (`dark`). Each `palette` hue becomes the stroke (shifted to 3:1 contrast) and a fill mixed three quarters toward the background. `draw.py` with `dark: true` writes a dark scene whose stored colours render as the theme's; native `create` makes a light scene, so under a dark app give `draw.py` hues only and run it without an output path to get the pairs. When the app cannot be read, use the built-in pairs (`draw.py` prints them for an empty spec) and say so.

Text is `ink`, inside a fill and on an arrow alike; a hue colours strokes and fills, never text. Native `create` gives a label its shape's or arrow's stroke colour, so set labels to `ink` with `apply` afterwards. With the built-in pairs `ink` is `#1e1e1e`, and on a dark canvas free text uses `#e9ecef` and structural lines `#868e96`. Spend one accent color once, on the thing the reader must not miss.

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

Coordinates for native `create`, each exported and looked at on plugin 2.29.1. Field names are in the live `schema action=create`. Facts that bit:

- A bound arrow still needs `points`. With only `start`/`end` it drew a short stub in the wrong place. Set `x,y` to the start point and `points: [[0,0],[dx,dy]]` to the end point; the plugin then snaps both ends to the shapes.
- Text-only `text` elements are free; bound labels use `label.text`.
- A `frame` is moved and resized around its `children` and clips anything that is assigned to it, including an arrow that ends inside it. For arrows that cross zones use a dashed `rectangle` plus a `text` name, as in the zone recipe.
- Frame `x,y` should equal the children's top-left minus 10; place children at the coordinates you want and size the frame to wrap them.

Notation: `box(id,x,y,w,h,"Label",color)` is a skeleton `rectangle` with `label`, solid fill and the palette pair; `a(from,to,x,y,dx,dy)` is an `arrow` with `start`/`end` ids and `points [[0,0],[dx,dy]]`; `t(x,y,"text",size)` is a free `text`; `l(x,y,[[0,0],[dx,dy]])` is a `line`.

**Fan-out.** `ellipse` hub `(0,160,160,80)` "Order placed". Targets `box` at `x=320`, `y=0/160/320`, `200x80`, one color per role. Arrows start `(160,200)`, `dx=160`, `dy=-160/0/160`.

**Convergence.** Sources `(0,n*160,160,80)`. Receiver `(360,100,200,240)`. Arrows start `(160,n*160+40)`, `dx=200`, `dy=180-n*160`. Output `ellipse (680,180,160,80)` with an arrow `(560,220)`, `dx=120`.

**Timeline.** Spine `l(0,0,[[0,0],[0,420]])`. Dots `ellipse 14x14` at `(-7, n*140-7)` filled with the `blue` stroke. Step name `t(32,n*140-14,.,20)`, grey 16 px date under it at `+28`. No boxes.

**Tree.** Root `t(0,0,.,24)`. Trunk `l(12,40,[[0,0],[0,200]])`. Each child: a 24 px horizontal `line` at its row and `t` 36 px further right per level; row pitch 40.

**Cycle.** Nodes `160x64` at `(0,0)`, `(280,0)`, `(280,160)`, `(0,160)`. Arrows `(160,32)` `dx=120`; `(360,64)` `dy=96`; `(280,192)` `dx=-120`; `(80,160)` `dy=-96`. Grey loop name at `(86,100)`.

**Assembly line.** Dashed `rectangle (-20,-20,220,230)` holding five unlabelled grey boxes of different sizes at irregular offsets, captioned "raw" above. `box (320,40,200,120)` "Normalize". Right: five identical green `60x32` boxes at `x=640`, pitch 44, captioned "clean". Arrows `(200,100)` `dx=120` and `(520,100)` `dx=120`.

**Side-by-side.** Headers `t(0,0,.,28)` and `t(420,0,.,28)`. Divider dashed `line` at `x=380`, height 300. Rows `300x56` at `y=80+n*80` in both columns; color only the cells that differ.

**Zones.** Dashed `rectangle (x,0,300,200)` in the `gray` stroke with a grey 16 px `t(x+16,12)` name. Members at `(x+50,70,200,80)`. Cross-zone arrow starts at `(250,110)`, `dx=200`.

**Sequence.** Participants `box` `160x56` at `x=0/280/560`. Lifelines dashed `line` from `(x+80,56)` down 300. Messages are free `arrow`s with `points [[0,0],[dx,0]]`, `label` 16 px, `y` pitch 50, replies `strokeStyle: "dashed"`. Past five participants or fifteen messages, use Mermaid instead.

**Swimlane.** Stage names as free `t` at `x=200+k*260`; one row per actor at `y` pitch 130, cells `240x90`, row name free at `x=0`. The shared artifact (note, ticket, file) takes the middle row; a cell an actor skips is a dashed neutral cell holding a dash.

**Bars.** Axis `l(x0,base,[[0,0],[n*40,0]])`; bar `k` is `rectangle (x0+k*40, base-v*scale, 30, v*scale)`, `roundness: null`, tallest about 400 px. Colour by period, never by value. To relate two measures stack a second row on the same `x` and run each event as one dashed vertical `line` through both.

**Source timeline.** The Timeline laid horizontally, each source's preview image under its dot at one shared width, image and name linked to the source.

**Mind map.** Centre `ellipse (0,0,180,90)`. Branches `160x60` on a radius of about 300 at 45, 135, 225, 315 degrees snapped to 20, one hue each. Arrows run from the centre (`90,45`) to each branch centre.

**Wireframe.** Outer `rectangle (0,0,320,560)` no fill. Grey blocks inside with 20 px margins: header `(20,20,280,56)`, image `(20,96,280,160)`, cards `(20,276,280,72)`, `(20,368,280,72)`. One blue button `(60,468,200,56)`; it is the only color.

## Text budget

A node label is a name or a value with at most one qualifying line. Legends, reading instructions, summaries and the question a section answers belong in the note. If the labels alone tell the story, the drawing is a list: let position say it.

## Fidelity to the request

Go through the request sentence by sentence and match every stated relationship to one arrow's source and target, before exporting. "Order reads Postgres on a cache miss" is an arrow from Order to Postgres, labelled, even if routing it through Redis looks tidier. A route that changes who talks to whom misinforms the reader, so a tidy layout never outranks the stated edge. Then check the reverse: no arrow exists that no sentence supports.

Labels follow the user's language; the user's own proper names, product names and code identifiers stay as written. A Korean request gets Korean labels, with `Redis` and `Postgres` left alone.

## When the user asks for a sketch

A request for a sketch or hand-drawn look changes the look, not only the font. Clean boxes at default roughness are the wrong answer. Choose in this order:

- `roughness` 2 on every shape and arrow; `fillStyle` `hachure` for fills.
- Vary shapes by meaning (ellipse, diamond, rectangle) rather than one box type.
- A loop must curve: give the closing arrows three `points` with `roundness: {"type": 2}`, and place the nodes on a ring, not a square grid. Observed: a four-node loop with such arrows rendered as a curved ring.
- Lines and connectors curved or slightly bent, free title text, unequal spacing.
- `fontFamily` and `fontSize` on a shape go inside its `label`, not on the shape; the CLI rejects them on the shape.

For hand-style Korean set `fontFamily` 5 (the only hand-style Hangul on plugin 2.29.1) and check the export. `draw.py` hard-codes family 2 and its edges take no `roughness` or curve; use node `roughness` and shapes there, or the CLI for more of the sketch look.

## Sticky notes

A CLI or `ea.addStickyNote` sticky note always carries a date stamp (`6 Nov`) that no field or `apply delete` removes. `draw.py`'s `note` shape had none. For a dateless note through the CLI, draw a yellow `rectangle` with `label`.

## Fixing a drawing

`create` never overwrites, so do not delete and recreate. `open` the drawing, `read source=live` for the `revision` and real ids, then `apply` with `expectedRevision`. One `apply` may combine `update`, `delete` and `add`; a bound label moves with its shape and is deleted with it. For a redesign, `create` a new path.

## Render, look, fix

Rendering is the plugin's own export; judge the exported image. After each pass:

1. Run the fidelity check above, then compare to the intent: does the structure show the chosen pattern, does the eye enter at the focal element and leave at the result?
2. List defects and fix them all before re-exporting: clipped text; an arrow passing over or touching any box or frame title that is not its endpoint (fix by giving the edge its own port and lane, or moving the box); a fan-out or fan-in whose arrows share a trunk (each edge gets its own exit or entry point); columns not aligned on a shared centre line; an edge label touching a node; a label on a vertical segment when a horizontal one exists touching a node; an arrow ending in empty space; arrows drawn as stubs (missing `points`); uneven gaps; one cramped region beside a void; text under 14; more than four palette pairs; a box that could be free text.
3. Stop when you would show it without caveats, usually after two to four passes. Build large drawings zone by zone in separate batches.
