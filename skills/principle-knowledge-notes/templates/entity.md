# Entity

Use this scaffold for a named individual of an optional type (an event, a movie, an album, a game title). Each required type has its own template under `entity/`. Follow the [shared frontmatter contract](../../ingest/references/frontmatter.md) and the destination's live policy.

## Maintenance

The selected template defines the writing area and update mode. Existing pages keep their current boundaries until the owner request or live policy authorizes a change; a template change is not a bulk migration.

| Template | Agent-written area | Update mode |
| --- | --- | --- |
| [Product](entity/product.md) | Sourced body under the Product headings | Revise and consolidate |
| Other Entity types | Bottom `## From Sources`, or the live policy's auto zone such as `## Wiki` | Append only |

Keep a before-image on updates. Preserve original records, meaningful historical distinctions, and owner prose outside the requested writing area.

- **Revise:** have a separate preservation reviewer compare the proposed synthesis with its evidence and before-image. Metadata corrections stay within the requested scope; preserve creation date, identity and provenance. Rewriting generated prose does not reclassify `authorship`. Verification fields belong to the verification workflow.
- **Append:** leave owner headings empty on creation and never rephrase their contents. Keep earlier auto-zone lines; add dated facts with their Raw, `### Sources` and `### Related`. Frontmatter permits only additions to `source`, `related`, `aliases` and an updated `date_modified`. Put newly observed type-specific values in the auto zone. If it is absent, append it on first touch; its absence is not a defect.

The live policy decides `type`, folder and metadata keys. Use its existing key for each meaning, fill source-backed values on creation, and omit unsupported optional fields. When it uses `wiki-page`, apply the full Wiki page field set of that frontmatter contract.

## Scaffold

```markdown
---
type: {{live_policy_type}}
aliases:
  - "{{alternative_name_or_romanization}}"
description: "{{english_one_or_two_sentences}}"
author:
  - "{{live_policy_author_or_agent_role}}"
model: {{runtime_model}}
effort: {{runtime_effort_or_default}}
date_created: {{today}}
date_modified: {{today}}
tags: []
source:
  - "[[{{raw_source}}]]"
related: []
# Fill slots as YAML-serialized values: lists stay lists (one item per existing source); a value containing " or \ is escaped by YAML double-quoted rules.
---

# {{name}}

## Notes

## From Sources

- {{YYYY-MM-DD}} {{fact_or_mention}} — [[{{raw_source}}]]

### Sources

- [[{{raw_source}}]]

### Related

- [[{{related_page}}]]
```
