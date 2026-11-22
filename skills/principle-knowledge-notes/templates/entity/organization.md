# Organization Entity

Use this scaffold for a company, lab, team, school, church or government body. The two-zone and frontmatter rules in the [common Entity template](../entity.md) apply.

- Title it with the name the organization uses for itself; put abbreviations, former names and translations in `aliases`. A branch with its own address is its own Entity.
- Record `website` and `address` only when the source states them. A product it makes, a channel it runs and a place it occupies are separate Entities linked from `### Related`.
- The owner zone holds the owner's basic information and dated notes. Facts a source states go to the auto zone.

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
website: "{{url}}"
address: "{{address}}"
source:
  - "[[{{raw_source}}]]"
related: []
---

# {{name}}

## Basic Information

## Notes

## From Sources

- {{YYYY-MM-DD}} {{fact_or_mention}} — [[{{raw_source}}]]

### Sources

- [[{{raw_source}}]]

### Related

- [[{{related_page}}]]
```
