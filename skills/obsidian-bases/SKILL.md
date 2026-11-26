---
name: "obsidian-bases"
description: "Creates and edits Obsidian Bases: .base files and embedded base code blocks with table, cards, list, kanban or map views, filters, formulas, properties and summaries. Use for a database-like view of notes, or groupBy, sort or limit in a base. Not for note frontmatter, Dataview queries or vault CLI operations."
license: MIT
---

# Obsidian Bases Skill

A `.base` file is YAML. This package owns its schema, expressions, functions, views and validation. The full function catalog is [references/FUNCTIONS_REFERENCE.md](references/FUNCTIONS_REFERENCE.md); no remote lookup is needed. Where a base lives, what it is for and its naming follow the target vault's policy and the user's task. Valid YAML is not permission to write: resolve the exact path and effect first, and stay read-only when either is missing.

## Workflow

1. Resolve the target path (a `.base` file, or the note holding a `base` block) and the effect. If the file exists, read and parse it first.
2. Set `filters` to choose which notes appear. With no filters, every file in the vault matches, attachments included.
3. Add `formulas`, then `views` with `order` (columns), plus `sort`, `groupBy` and `limit` as needed.
4. Run the validation checklist below, write once, then re-read the file from its path. Whether the view renders the expected rows is a separate claim: check it in Obsidian or report it as unverified.

## Schema

```yaml
filters:                         # global: apply to every view
  and:                           # a filter object has exactly ONE key: and, or, not
    - 'status == "active"'
    - not:
        - 'file.hasTag("archived")'

formulas:
  formula_name: 'expression'

properties:                      # display settings; note properties need `note.`
  note.property_name:
    displayName: "Display Name"
  formula.formula_name:
    displayName: "Formula Display Name"

summaries:                       # custom summary formulas
  custom_summary_name: 'values.mean().round(3)'

views:
  - type: table | cards | list | kanban | map
    name: "View Name"
    limit: 10                    # max rows shown
    groupBy:                     # one property only
      property: property_name
      direction: ASC | DESC
    groupOrder:                  # only these groups, in this order
      - value_one
      - null                     # files with no value
    sort:                        # a list; first entry primary, later ones break ties
      - property: property_name
        direction: ASC | DESC
    filters:                     # view filters, ANDed with the global filters
      and:
        - 'status == "active"'
    order:                       # columns, left to right -- NOT row order
      - file.name
      - property_name
      - formula.formula_name
    summaries:                   # property -> summary name
      property_name: Average
```

- `order` is columns; `sort` is row order. Confusing them is the usual reason a base "ignores" an ordering.
- `direction` must be uppercase `ASC` or `DESC`. Another value, or `sort` written as a string, is silently ignored.
- `groupBy` takes one property; order inside groups with `sort`. Rows with an empty group value are grouped under the empty value, not dropped.
- A view may carry keys not listed here (the app stores layout settings such as column sizes in the view). Keep unknown keys unchanged when editing.

## Filters

```yaml
filters: 'status == "done"'      # a single expression string

filters:
  or:
    - file.hasTag("tag")
    - and:
        - file.hasTag("book")
        - file.hasLink("Textbook")
    - not:
        - file.inFolder("Required Reading")
```

The value of `and`/`or`/`not` is a list of expression strings or nested filter objects. To combine `and` with `or`, nest one inside the other; a single object cannot hold both keys. Filters and formulas share one expression language: `== != > < >= <=`, `&& || !`, `+ - * / %`, parentheses.

## Properties

- **Note properties** (frontmatter, Markdown only): `author` or `note.author`.
- **File properties** (every file): `file.name`, `file.basename`, `file.path`, `file.folder`, `file.ext`, `file.size`, `file.ctime`, `file.mtime` (dates), `file.tags`, `file.links`, `file.backlinks`, `file.embeds` (lists), `file.properties` (object), `file.file` (the file object).
- **Formula properties**: `formula.name`, defined in `formulas`.

In `order`, `filters`, `groupBy` and `sort` a note property may be bare or prefixed. In the top-level `properties:` section always write `note.author`: a bare key is ignored and the raw name shows as the header. `displayName: ""` does not hide a header; it falls back to the property name.

`file.backlinks` is expensive; prefer `file.links` from the other side. `file.backlinks` and `file.properties` may not refresh as the vault changes.

### `this`

- Base opened in the main area: the base file itself (`this.file.folder` is the base's folder).
- Base embedded in a note, or a `base` code block: the embedding note. `file.inFolder(this.file.folder)` and `file.hasLink(this.file)` give per-note views.
- Sidebar: the active file in the main area.

## Formulas

```yaml
formulas:
  total: "price * quantity"
  status_icon: 'if(done, "✅", "⏳")'
  formatted_price: 'if(price, price.toFixed(2) + " dollars")'
  created: 'file.ctime.format("YYYY-MM-DD")'
  days_old: '(now() - file.ctime).days'
  days_until_due: 'if(due_date, (date(due_date) - today()).days, "")'
```

- Guard optional properties with `if()`; `date(due)` on an empty value errors.
- A formula may reference another formula, but not in a cycle.
- Global functions: `date()`, `duration()`, `now()`, `today()`, `if()`, `min()`, `max()`, `number()`, `link(path, display?)`, `list()`, `file(path)`, `image()`, `icon()`, `html()`, `escapeHTML()`. Methods per type (String, Number, Date, List, File, Link, Object, RegExp) are in [FUNCTIONS_REFERENCE.md](references/FUNCTIONS_REFERENCE.md). Use only functions listed there.

### Dates and Durations

Subtracting two dates gives a **Duration**, not a number. A Duration has fields `.days`, `.hours`, `.minutes`, `.seconds`, `.milliseconds` and does NOT support `.round()`, `.floor()`, `.ceil()` or division. Read a field first, then use number functions.

```yaml
"(date(due_date) - today()).days.round(0)"     # CORRECT
"(now() - file.ctime).hours.round(0)"          # CORRECT
"(now() - file.ctime).round(0)"                # WRONG: Duration is not a number
"((date(due) - today()) / 86400000).round(0)"  # WRONG

# Add a duration string to a date. Units: y/year/years, M/month/months, d/day/days,
# w/week/weeks, h/hour/hours, m/minute/minutes, s/second/seconds
"today() + \"7d\""
"date(due) - \"2h\""
"now() + (duration('1d') * 2)"
```

`date.format()` takes a Moment.js pattern. Dates also expose `.year`, `.month`, `.day`, `.hour`, `.minute`, `.second`, `.millisecond`.

## Views

| Layout | Since | Notes |
|--------|-------|-------|
| `table` | 1.9 | per-view `summaries` show under columns |
| `cards` | 1.9 | an image property in `order` becomes the card cover |
| `list` | 1.10 | |
| `kanban` | 1.14 | needs `groupBy`; columns are its values |
| `map` | 1.10 | needs the Maps plugin and lat/lng properties |

Kanban: `groupOrder` picks which columns show and in what order (`null` for no value); without it every value gets a column. Dragging a card writes the grouped property to the note (or moves the file when grouping by `file.folder`); with a formula or other file property as the group, cards cannot move.

Layout availability depends on the installed app and plugins, which YAML cannot assert. An unknown `type` does not render; report it as unverified rather than "fixing" the syntax.

## Summaries

Default names: `Average`, `Min`, `Max`, `Sum`, `Range`, `Median`, `Stddev` (numbers); `Earliest`, `Latest`, `Range` (dates); `Checked`, `Unchecked` (booleans); `Empty`, `Filled`, `Unique` (any).

A custom summary goes in the top-level `summaries`; inside it `values` is the list of that column's values and the expression returns one value. A view's `summaries` maps a property to a default or custom name.

```yaml
summaries:
  customAverage: 'values.mean().round(3)'
views:
  - type: table
    name: "Prices"
    order: [file.name, price]
    summaries:
      price: customAverage
```

## Embedding

```markdown
![[MyBase.base]]             <!-- first view in `views` -->
![[MyBase.base#View Name]]   <!-- view selected by name -->
```

Keep the `.base` extension. Reordering views changes plain embeds; renaming a view breaks `#View Name` embeds, and nothing in the base records them. A fenced `base` code block in a note uses the identical schema.

## YAML Quoting

- Wrap an expression containing double quotes in single quotes: `'if(done, "Yes", "No")'`. `"if(done, "Yes", "No")"` does not parse.
- Quote any string containing `: { } [ ] , & * # ? | - < > = ! % @` or a backtick, e.g. `displayName: "Status: Active"`.
- Text literals inside an expression must be quoted, which is why the nesting exists.

## Editing an Existing Base

Amend the parsed document; do not regenerate it. Change only what was asked. Keep every other view with its name, position (the first view is what a plain embed shows) and settings, every other formula, display name and unknown key, and the existing key order and quoting. Do not rename views or formulas to tidy up: both are referenced elsewhere. Report problems you find but were not asked to fix, with their key path. [references/operations.md](references/operations.md) has the error-reporting table, empty-result triage and verification steps.

## Validation Checklist

1. The file parses as YAML.
2. Every filter object has exactly one of `and`, `or`, `not`, whose value is a list.
3. Every `formula.X` used in `order`, `properties`, `summaries`, `sort`, `groupBy` or another formula is defined in `formulas`, without cycles.
4. Every view has a `type` and a `name`; names are unique; a kanban view has `groupBy`.
5. `sort` is a list of `{property, direction}`; every `direction` is `ASC` or `DESC`.
6. Note properties under top-level `properties:` use the `note.` prefix.
7. View summary names are defaults or top-level `summaries` entries.
8. Date differences read a Duration field before number functions; optional properties are guarded with `if()`.
9. Every function used appears in FUNCTIONS_REFERENCE.md.

Passing this list proves the document is well formed, not that it was written where intended or that any note matches.

More: [references/examples.md](references/examples.md) (complete bases and an expected-rows worked example), [references/operations.md](references/operations.md) (errors, empty results, readback vs render).

## Attribution

The format documentation and examples in this package are derived from the `obsidian-bases` skill in [kepano/obsidian-skills](https://github.com/kepano/obsidian-skills) at commit `3ccff5338ea700537839b21900aa5358a0402c98`, MIT License, Copyright (c) 2026 Steph Ango (@kepano). That material has been modified here. See Git history for the recorded revision, the modifications, and the evidence behind the additions.
