# Entity

Use this scaffold for a named individual of an optional type (an event, a movie, an album, a game title). Each required type has its own template under `entity/` that builds on these rules. Follow the [shared frontmatter contract](../../ingest/references/frontmatter.md) and the destination's live policy.

- An Entity is the owner's note. The owner zone sits on top: the type's headings, created empty. Never write, reorder or rephrase anything there, on creation or later.
- The auto zone starts at `## From Sources` at the end of the body, or is the section the live policy names for agent-written Entity content (for example `## Wiki`), kept in its existing sub-structure. Append dated, source-grounded facts and mentions, each citing its Raw, and add each Raw to `### Sources` and each linked page to `### Related`. A type's own `###` lists sit between the dated lines and `### Sources`. Never edit or remove an earlier line; record a change as a new dated line.
- The live policy decides `type` and the folder. When it files Entities as `type: wiki-page`, also set `layer: entities`, `explored: false` and `verificationStatus: unverified`.
- In frontmatter keep every owner key and value. Append to `source`, `related` and `aliases`, and update `date_modified`. Set a type-specific key only on creation and only from the source, omitting any key the source does not state (never an empty string or `"[[]]"`); on an existing note, record a newly observed value as a dated auto-zone line instead.
- Where existing notes of the same type already use their own key for a meaning (`feed_url`, `youtube_channel_id`), use that key, not a new one.
- An existing Entity with neither heading gets `## From Sources` appended at the end of its body on first touch. Nothing is converted in bulk.

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
