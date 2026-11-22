# Place Entity

Use this scaffold for a named location: a venue, shop, city or landmark. The two-zone and frontmatter rules in the [common Entity template](../entity.md) apply.

- Title it with the name in local use, qualified by area when the name is shared. A trip or an itinerary is not a place; it belongs to the owner's own notes.
- Record `address`, `coordinates` and `website` only when the source states them. The organization that runs the place is its own Entity.
- The owner zone holds details the owner keeps, their visits and notes. Facts a source states, such as opening hours or a closure, go to the auto zone as dated lines.

## Scaffold

```markdown
---
type: {{live_policy_type}}
aliases: []
description: "{{english_one_or_two_sentences}}"
author:
  - "{{live_policy_author_or_agent_role}}"
model: {{runtime_model}}
effort: {{runtime_effort_or_default}}
date_created: {{today}}
date_modified: {{today}}
tags: []
address: "{{address}}"
coordinates: "{{lat_lng}}"
website: "{{url}}"
source:
  - "[[{{raw_source}}]]"
related: []
---

# {{name}}

## Details

## Visits

## Notes

## From Sources

- {{YYYY-MM-DD}} {{fact_or_mention}} — [[{{raw_source}}]]

### Sources

- [[{{raw_source}}]]

### Related

- [[{{related_page}}]]
```
