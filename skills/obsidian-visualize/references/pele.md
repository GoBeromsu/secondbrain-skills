# Pele diagrams

Produce a `mermaid` fence that carries the intended meaning and renders in the renderer the target Obsidian installation actually ships: Pele from 1.15.0, an older pinned Mermaid bundle before that.

Done means: the diagram family fits the relationship being shown, the prefix and grammar are accepted by the target renderer, the source sits in an exact `mermaid` fence, unrelated note content is byte-for-byte untouched, and every claim is backed by the evidence level that actually produced it.

## What changed

Obsidian 1.15.0 stopped bundling Mermaid. The fence is still written ```` ```mermaid ```` and the grammar is still Mermaid 12.1.0's, but Pele draws it with its own layout and the vault theme's colors and fonts, and runs no code, so there is no setting to enable. **Writing the right fence is the work; a probe only confirms it.** [`pele-compatibility.md`](pele-compatibility.md) holds the differences, limits and the gate for older apps.

Pele has no command-line tool and needs no plugin. To confirm a fence without opening the note, call Pele's runtime from `obsidian eval`. `window.pele` is not guaranteed to exist yet and `loadMermaid` is not a global, so load it through the Excalidraw plugin first, then call `window.pele.render(source)`. `render` is synchronous: it returns `{svg}` or throws a `PeleError` carrying the parse error text.

```bash
obsidian vault=<name> eval code='(()=>{const r=window.__check={s:"run"};ExcalidrawAutomate.obsidian.loadMermaid().then(()=>{try{r.n=window.pele.render("flowchart LR\n  A --> B").svg.length;r.s="ok"}catch(e){r.s="fail";r.e=String(e.message)}});return "ok"})()'
obsidian vault=<name> eval code='JSON.stringify(window.__check)'
```

To check every fence of a note, read the file with `app.vault.cachedRead`, take each ```` ```mermaid ```` body and render it the same way. Without the Excalidraw plugin, open the note as a preview tab and count what drew, then close the tab:

```bash
obsidian vault=<name> eval code='(()=>{const f=app.vault.getAbstractFileByPath("<path>");const l=app.workspace.getLeaf("tab");window.__leaf=l;l.openFile(f,{state:{mode:"preview"}}).then(()=>setTimeout(()=>{window.__n=l.view.previewMode.containerEl.querySelectorAll("svg.pele").length},1500));return "ok"})()'
obsidian vault=<name> eval code='window.__n'
obsidian vault=<name> eval code='window.__leaf.detach()'
```

To look at the result, take a screenshot while the preview tab is open and before it is detached, with a path outside the vault, then open the PNG:

```bash
obsidian vault=<name> dev:screenshot path=<absolute-path>.png
```

It captures the whole app window, so it also shows other open tab titles: keep it out of the vault and out of anything shipped. Colors come from the app's theme (a light theme in the run that was checked; a dark theme was not). Do not rasterize a saved `pele.render` SVG with `rsvg-convert` or similar: the SVG draws with `var(--pele-*)` theme variables that only resolve inside the app, and flowchart and sequence boxes come out solid black. Korean text, colors and layout were correct in the screenshot of flowchart, sequence and pie.

A block that fails to draw in the preview stays in the page as a box of text beginning with `Parse error` or `Lexical error`, so reading the text of each `.el-pre` element names the failing block. `window.pele.supports("<keyword>")` answers whether a diagram keyword exists without rendering.

## Evidence ladder

The ladder is in [`../SKILL.md`](../SKILL.md). For a Pele block: A is the source read against [`pele-catalog.md`](pele-catalog.md) and the rules here; B is the note's bytes re-read after the write; C is `window.pele.render(source)` accepting the grammar, with the version from `obsidian version` stated (mermaid.live or the Mermaid CLI prove real Mermaid, not Pele); D is the note open in the target Obsidian and looked at.

C is not D: `pele.render()` proves grammar acceptance in one app, not the note's layout, theme, or an older device's bundle. B is not D either: writing a fence is not rendering it.

When a level cannot be reached — no app access, no vault authorization, headless environment — say which level was reached and name the rest as unverified.

## Workflow

1. **State the meaning first.** Write the sentence the diagram must communicate (sequence of steps, message order, state transitions, proportions, hierarchy, flow quantities). The sentence chooses the family.
2. **Pick the smallest family that carries it** using the table below.
3. **Apply the compatibility gate** in [`pele-compatibility.md`](pele-compatibility.md). An unknown app version is an old one.
4. **Start from the catalog entry**, not from memory. Replace labels and data; leave the grammar alone.
5. **Write labels** under the escaping and readability rules below.
6. **Fence it exactly** (see Fences and placement).
7. **Only if the task actually edits a note:** confirm write authorization for that exact note, make the narrowest possible edit, and read the file back (see Editing a note safely).
8. **Render QA** in the target installation only when asked, because level C already proves the grammar and needs no opened note. Record the app and installer versions from `obsidian version`.
9. **On a renderer failure, fall back without losing meaning** (see Failing without degrading meaning).

## Choosing the family

| The meaning to carry | Family | Notes |
| --- | --- | --- |
| Ordered steps with branches | `flowchart TD` / `flowchart LR` | The default; also the fallback for any structural diagram |
| Who sends what to whom, in order | `sequenceDiagram` | Name participants explicitly; arrow type encodes sync/async/return |
| Types, fields, and cardinality | `classDiagram` | Use for a domain model, not for runtime steps |
| Lifecycle of one thing | `stateDiagram-v2` | Exact `-v2` suffix |
| Stored entities and their keys | `erDiagram` | Schema shape, not process |
| Dated work with durations | `gantt` | Needs `dateFormat`; durations, not vibes |
| Step-by-step experience with scores | `journey` | Score and actor follow each task label |
| Parts of one whole | `pie` | Quote every label; one level only |
| Branching outline of one topic | `mindmap` | Indentation is the grammar — keep it consistent |
| Dated milestones in order | `timeline` | One period line, then its events |
| Quantified flow between stages | `sankey-beta` | CSV-shaped rows: source, target, value |
| Work items across workflow columns | `kanban` | Version-gated before 1.15.0 |
| Nested proportions | `treemap-beta` | Version-gated before 1.15.0 |
| Services, groups, and their links | `architecture-beta` | Version-gated before 1.15.0 |
| Numeric series over categories | `xychart-beta` | Version-gated before 1.15.0 |
| Several actors handing off one process | `swimlane-beta` | Pele-only |
| A page or screen divided into a grid | `block-beta` | Pele-only |
| Agents splitting work and calling tools | `agentflow-beta` | Pele-only |
| Versions, branches and merges | `gitGraph` | Pele-only; case-exact keyword |
| Screens, commands and events changing state | `eventmodeling` | Pele-only |
| A few subjects profiled on several criteria | `radar-beta` | Pele-only |
| Items placed on two criteria | `quadrantChart` | Pele-only |
| Overlap of two or three sets | `venn-beta` | Pele-only |
| Requirements traced to what satisfies them | `requirementDiagram` | Pele-only |
| People, systems and external systems | `C4Context` | Pele-only |
| What actors want from a system | `usecase-beta` | Pele-only |
| Fixed-width fields of an identifier | `packet-beta` | Pele-only |
| A notation rule as EBNF | `railroad-ebnf-beta` | Pele-only |
| Folder and file paths | `treeView-beta` | Pele-only |
| Causes of one problem by category | `ishikawa-beta` | Pele-only |
| Work sorted into Cynefin domains | `cynefin-beta` | Pele-only |
| Value chain by visibility and evolution | `wardley-beta` | Pele-only |

Each catalog pattern also names when to avoid its family and the size past which it stops being readable. Use a Pele-only family only when every device that reads the note runs 1.15.0+.

Split a diagram at a real boundary (phase, actor, subsystem) as soon as labels overlap or edges cross unreadably. Pele scales wide diagrams down and lets the reader zoom and pan; that is not readability. Two readable diagrams beat one complete unreadable one.

## Syntax pitfalls

Every row failed in Obsidian 1.15.1 (installer 1.15.0) through `window.pele.render()` or a preview tab. Quote every label as a habit: it is cheap, and `(` and `|` fail without it.

| You wrote | Pele says | Fix |
| --- | --- | --- |
| `A[Renewal (second request)]` | `Parse error ... got 'PS'` | `A["Renewal (second request)"]` |
| `A -->\|yes (ok)\| B` | `Parse error ... got 'PS'` | `A -->\|"yes (ok)"\| B` |
| `A[a\|b]` | `Parse error ... got 'PIPE'` | quote the label |
| `participant X as "CI(빌드/테스트)"` | no error: the quotes print literally in the box | sequence has no quoted form: write `participant X as CI(빌드/테스트)` bare |
| `A --> end` | `Parse error ... got 'end'` | `End`, or `[end]`, which draws |
| `subgraph S1` with no `end` | `Parse error ... Expecting 'end'` | close every subgraph |
| `statediagram-v2`, `sequencediagram`, `gitgraph` | `No diagram type detected` | exact case: `stateDiagram-v2`, `sequenceDiagram`, `gitGraph` |
| `zenuml`, a comment-only fence, an empty fence | `No diagram type detected` | ZenUML is unsupported; use `sequenceDiagram` |
| `pie` with `A : 3` | `Lexical error` | quote labels: `"A" : 3` |
| `pie title "Loans"` | no error: the quotes print literally in the title | bare title: `pie title Loans` (slice labels stay quoted) |
| two diagrams in one fence | `Parse error` at the second prefix | one fence per diagram |
| `<!-- c -->` inside the diagram | `Parse error` | `%%` at line start |
| a fence tagged ```` ```Mermaid ```` | none: drawn as a plain code block (raw text) | lowercase `mermaid` |

Keep the user's own wording in a label, parentheses and slashes included; do not rename "CI(빌드/테스트)" to "CI 빌드·테스트" to dodge a parse error. Forms that printed the text exactly as written (screenshot or SVG text): flowchart, class and mindmap `["CI(빌드/테스트)"]`, ER relation label `: "has (many)"`, state `state "CI(빌드/테스트)" as S`, and in sequence a bare `participant X as CI(빌드/테스트)`, a bare participant id `CI(빌드/테스트)`, a bare message `A->>B: 빌드(테스트) 요청`, or entity codes `#40;` and `#41;` for the parentheses. If a form is missing for a type you need, say so to the user when you change a label.

Passed, and so not pitfalls: Korean labels bare or quoted, in flowchart, sequence, state, pie, mindmap, gantt, class, ER, journey, timeline and sankey; `<br>` and `<br/>`; `:`, `/`, `#`, `&` and `{}` in an unquoted flowchart label; a `mermaid` fence in a list item, a callout and a `~~~` fence; `graph` for `flowchart`; `stateDiagram` without `-v2`; `sankey`, `treemap` and `xychart` without `-beta`.

Accepted but ignored, so a diagram that "works in mermaid.live and looks different here" is usually this and not an error: `%%{init}%%` and front-matter `theme`, `themeVariables`, `layout`, and `flowchart.curve` all produced the same SVG as no config. Only front-matter `title` changed the output. Colors come from the vault theme.

Rules that hold beyond the table:

- **A node id starting with `o` or `x` right after an edge changes the edge.** `A---oB` is a circle edge in Mermaid grammar; add a space or capitalize.
- **Escape with entity codes when quoting is not enough.** `#quot;` for a double quote, `#35;` for `#`, `#lt;` and `#gt;` for angle brackets.
- **Line breaks.** `<br/>`, or a Markdown string label (a quoted label wrapped in backticks, which also takes `**bold**`). A literal `\n` also breaks in Pele but older bundles print it, so do not write it.
- **No HTML labels.** `<b>` draws as text; `<kbd>` and `<code>` lose the tag and use the mono font.
- **Math.** A `$$...$$` label is typeset by the host: MathJax in a rendered note, TeX source from a bare `pele.render()`.
- **Subgraph `direction` holds in Pele** even when an edge crosses the boundary; older bundles ignore it then.

## Fences and placement

The block must open with exactly three backticks followed by `mermaid`, with nothing else on the line, and close on its own line. There is no `pele` fence:

````markdown
```mermaid
flowchart LR
  A[Request received] --> B{In catalog?}
  B -->|Yes| C[Place hold]
  B -->|No| D[Open purchase suggestion]
```
````

- One diagram per fence. A second prefix inside the same fence is a parse error.
- To show a block as example text rather than render it, wrap it in a four-backtick fence, as above.
- Inside a callout or blockquote, every line of the block — including both fence lines — needs the `>` prefix.
- Inside a list item, indent the whole block to the item's content column.
- Obsidian links from diagram nodes use the `internal-link` class (`class NodeA,NodeB internal-link;`); quote note names containing special characters. Pele keeps the class on the node; whether the link navigates in 1.15.0 is unverified until checked at level D. Those links do not appear in Graph view.
- `click` statements that open an `http`, `https`, `mailto` or `tel` link work; JavaScript callbacks are ignored.

## Editing a note safely

Authoring a diagram grants no write permission. A write needs the task's own authorization for that exact note, and the vault's live policy still decides placement and house style.

- Read the note first; locate the exact insertion point or the exact existing fence to replace.
- Anchor the edit on unique surrounding text, replacing only the diagram block. Never reformat, re-wrap, reorder, or "clean up" anything else, including frontmatter, tags, and whitespace.
- Never write vault notes with shell redirection or stream editors. Use the host file-editing tool or the vault-aware surface the task selected.
- Read the file back after the write and confirm both that the fence is exactly as intended and that unrelated content is unchanged. A successful write call is not readback.
- Compose the `obsidian-markdown` package by identity only when the task genuinely also changes note prose, links, embeds, or properties.

## Failing without degrading meaning

When the target renderer rejects the chosen family, the replacement must still carry the sentence from step 1.

1. Re-state what the original diagram encoded: entities, relations, order, quantities, hierarchy.
2. Choose a fallback that keeps all of it — usually `flowchart` for structure, `pie` for a single-level proportion, or a Markdown table for values.
3. If the fallback cannot carry part of it (a `pie` drops hierarchy; a `flowchart` drops magnitudes), ship the fallback **and** the dropped information in a table or list beside it.
4. Say so in the note or the report: which family was intended, what the target rejected, what the fallback preserves, and what it does not.

Silently shipping a smaller diagram that says less is a wrong answer that looks like a right one. So is leaving a broken fence in place because the fallback would be uglier.

## Boundaries

- Mermaid rendered anywhere other than the target Obsidian install — a static site, a code host, a live editor — runs real Mermaid and does not inherit this baseline.
- The Excalidraw plugin's own Mermaid import (`addMermaid`) converts source into drawing elements; it belongs to the Excalidraw branch in [`excalidraw-plugin.md`](excalidraw-plugin.md), and whether it uses Pele is unverified.
- Vault policy owns whether the note may be written at all.

## Verification

- [ ] The sentence the diagram must carry is stated, and the family carries it.
- [ ] The prefix is exact, and any version-gated family passed the compatibility gate.
- [ ] Labels are quoted or escaped where the grammar needs it, and contain no literal `\n`.
- [ ] The block is in an exact `mermaid` fence, one diagram per fence, correctly nested if inside a callout or list.
- [ ] If a note was edited: authorization existed, the edit was anchored, and readback confirmed unrelated content is unchanged.
- [ ] The highest evidence level actually reached is reported, with the Obsidian app and installer versions when level C or D was reached.
- [ ] Any fallback preserves the original meaning, or explicitly lists what it drops.
