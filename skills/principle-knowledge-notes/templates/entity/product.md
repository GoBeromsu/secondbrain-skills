# Product Entity

Use this scaffold for software, a service, a model or a dataset. The two-zone and frontmatter rules in the [common Entity template](../entity.md) apply.

- Title it with the product's own name; put former names and common abbreviations in `aliases`. A version gets its own Entity only when sources treat it as a separate product.
- Record `maker`, `url` and `repository` only from the source. The maker is its own Entity; the idea or technique the product implements is a Term or Concept, never this page.
- The owner zone holds how the owner uses it and their notes. Features, releases and changes a source states go to the auto zone as dated lines.

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
maker: "[[{{organization_or_person}}]]"
url: "{{url}}"
repository: "{{url}}"
source:
  - "[[{{raw_source}}]]"
related: []
---

# {{name}}

## Usage

## Notes

## From Sources

- {{YYYY-MM-DD}} {{fact_or_mention}} — [[{{raw_source}}]]

### Sources

- [[{{raw_source}}]]

### Related

- [[{{related_page}}]]
```
