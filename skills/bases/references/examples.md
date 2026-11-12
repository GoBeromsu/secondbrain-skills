# Complete Examples

### Task Tracker Base

```yaml
filters:
  and:
    - file.hasTag("task")
    - 'file.ext == "md"'

formulas:
  days_until_due: 'if(due, (date(due) - today()).days, "")'
  is_overdue: 'if(due, date(due) < today() && status != "done", false)'
  priority_label: 'if(priority == 1, "🔴 High", if(priority == 2, "🟡 Medium", "🟢 Low"))'

properties:
  status:
    displayName: Status
  formula.days_until_due:
    displayName: "Days Until Due"
  formula.priority_label:
    displayName: Priority

views:
  - type: table
    name: "Active Tasks"
    filters:
      and:
        - 'status != "done"'
    order:
      - file.name
      - status
      - formula.priority_label
      - due
      - formula.days_until_due
    groupBy:
      property: status
      direction: ASC
    summaries:
      formula.days_until_due: Average

  - type: table
    name: "Completed"
    filters:
      and:
        - 'status == "done"'
    order:
      - file.name
      - completed_date
```

### Reading List Base

```yaml
filters:
  or:
    - file.hasTag("book")
    - file.hasTag("article")

formulas:
  reading_time: 'if(pages, (pages * 2).toString() + " min", "")'
  status_icon: 'if(status == "reading", "📖", if(status == "done", "✅", "📚"))'
  year_read: 'if(finished_date, date(finished_date).year, "")'

properties:
  author:
    displayName: Author
  formula.status_icon:
    displayName: ""
  formula.reading_time:
    displayName: "Est. Time"

views:
  - type: cards
    name: "Library"
    order:
      - cover
      - file.name
      - author
      - formula.status_icon
    filters:
      not:
        - 'status == "dropped"'

  - type: table
    name: "Reading List"
    filters:
      and:
        - 'status == "to-read"'
    order:
      - file.name
      - author
      - pages
      - formula.reading_time
```

### Daily Notes Index

```yaml
filters:
  and:
    - file.inFolder("Daily Notes")
    - '/^\d{4}-\d{2}-\d{2}$/.matches(file.basename)'

formulas:
  word_estimate: '(file.size / 5).round(0)'
  day_of_week: 'date(file.basename).format("dddd")'

properties:
  formula.day_of_week:
    displayName: "Day"
  formula.word_estimate:
    displayName: "~Words"

views:
  - type: table
    name: "Recent Notes"
    limit: 30
    order:
      - file.name
      - formula.day_of_week
      - formula.word_estimate
      - file.mtime
```

### Worked Example: Expected Rows and Order

Three notes, one base, and the exact result the view should produce. Use this shape to state an expectation *before* opening the app, so a mismatch is a finding instead of a surprise.

`Study-A.md`, `Study-B.md`, `Study-C.md`:

```markdown
---
kind: study
status: active
priority: 2
---
Alpha preserved.
```

```markdown
---
kind: study
status: active
priority: 1
---
Beta preserved.
```

```markdown
---
kind: study
status: archived
priority: 0
---
Gamma preserved.
```

`Studies.base`:

```yaml
filters:
  and:
    - kind == "study"
    - status == "active"
views:
  - type: table
    name: Active studies
    groupBy:
      property: status
      direction: ASC
    sort:
      - property: priority
        direction: ASC
    order:
      - file.name
      - priority
    limit: 2
```

Expected rendered result:

| # | Group | `file.name` | `priority` |
|---|-------|-------------|------------|
| 1 | `status active` | `Study-B` | 1 |
| 2 | `status active` | `Study-A` | 2 |

- `Study-C` is absent because `status == "active"` excludes it, not because of the limit.
- `Study-B` precedes `Study-A` because `sort` orders by `priority` ascending, while `order` only decides that the name column sits left of the priority column.
- One group header appears, because every surviving row shares the same `status` value.
- The toolbar reports the number of results in the view; compare it with the row count you expected rather than reading it as a vault-wide count.

This result was observed in Obsidian 1.12.7 with the Bases core plugin enabled, over exactly these three notes. Scope any behavioural claim to the build you actually ran; another build is a separate observation.

Recording the expectation this way makes two failures distinguishable: a wrong document (the readback does not match what you wrote) and a wrong result (the document is right and the rendered rows still differ).

