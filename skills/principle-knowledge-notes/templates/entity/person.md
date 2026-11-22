# Person Entity

Use this scaffold for a named human. The two-zone and frontmatter rules in the [common Entity template](../entity.md) apply.

- Title the note with the real name the source confirms, in its original language and script. Put handles, channel names, localized names and romanizations in `aliases`; never infer a real name.
- Record contact and profile keys (`organization`, `emails`, `phones`, `linkedin`, `youtube`, `x`) only when the source states them; omit the rest.
- The owner zone holds the owner's introduction, basic information and dated personal notes. Facts a source states about the person go to the auto zone.

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
organization: "[[{{organization}}]]"
emails: []
phones: []
linkedin: "{{url}}"
youtube: "{{url}}"
x: "{{handle}}"
source:
  - "[[{{raw_source}}]]"
related: []
---

# {{real_name}}

## Introduction

## Basic Information

## Notes

## From Sources

- {{YYYY-MM-DD}} {{fact_or_mention}} — [[{{raw_source}}]]

### Sources

- [[{{raw_source}}]]

### Related

- [[{{related_page}}]]
```
