# Paper Entity

Use this scaffold for one scholarly work: a journal or conference paper, preprint, thesis or report. The paper Entity is the paper's hub. The two-zone and frontmatter rules in the [common Entity template](../entity.md) apply.

- Identity is `doi` and `citekey`, resolved against the actual paper and identical to the values on its Raw. Surname plus year is a search hint, never identity. A provisional citekey carries `citekeyProvisional: true`; a later key is recorded, and the note is never renamed for it.
- Title it with the citekey (`Duan2022Revisiting`) unless the live policy titles papers by their title; put the full title in `aliases` and `title`.
- `author` holds the paper's authors as quoted wikilinks in source order, as on its Raw, not the writing agent.
- The owner zone holds the owner's summary, annotations and thinking. The owner cites the paper as `[@{{citekey}}]`.
- The auto zone lists the paper's Raws under `### Sources` and every Term, Concept and Guide compiled from it under `### Derived`, plus dated source-grounded facts, each citing its Raw.

## Scaffold

```markdown
---
type: {{live_policy_type}}
aliases:
  - "{{full_title}}"
description: "{{english_one_or_two_sentences}}"
author:
  - "[[{{author_1}}]]"
  - "[[{{author_n}}]]"
model: {{runtime_model}}
effort: {{runtime_effort_or_default}}
date_created: {{today}}
date_modified: {{today}}
tags: []
title: "{{full_title}}"
year: {{year}}
venue: "{{journal_or_conference}}"
citekey: {{citekey}}
doi: "{{doi}}"
source:
  - "[[{{paper_raw}}]]"
related: []
---

# {{citekey_or_title}}

## Summary

## Annotations

## Thinking

## From Sources

- {{YYYY-MM-DD}} {{fact_or_finding}} — [[{{paper_raw}}]]

### Derived

- [[{{term_concept_or_guide}}]]

### Sources

- [[{{paper_raw}}]]

### Related

- [[{{related_page}}]]
```
