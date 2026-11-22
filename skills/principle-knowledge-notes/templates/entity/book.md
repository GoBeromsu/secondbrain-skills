# Book Entity

Use this scaffold for one book work and edition. The book Entity is the book's hub: chapter Raws, reading progress and derived pages are listed in its auto zone. The two-zone and frontmatter rules in the [common Entity template](../entity.md) apply.

- Identity is the work and edition: search by ISBN, author, translator, publisher and edition before creating. A translated or alternate title alone is not a different work; differing editions are separate Entities, never merged silently. For a classic, distinguish the recognized local title, original-language title, translator and edition.
- `author` holds the book's authors as quoted wikilinks, not the writing agent. Set `isbn`, `publisher`, `date_published`, `total_page`, `cover_url` and `source_url` only from the bookstore or publisher page on creation.
- Label every bibliographic line in `### Bibliographic Record` by origin: `observed` (bookstore or publisher page, linked), `inferred` (OCR or summary) or `owner` (reading context the owner supplied). A three-line summary is never catalog fact, and a bookstore blurb is not a reading note.
- `### Table of Contents` holds the TOC in original order and language as observed, with its source linked, written once. An empty TOC is unfinished bibliographic work.
- List each chapter Raw (book chapter template in `ingest`) under `### Chapters` against its TOC entry. Record progress as an appended dated line per chapter state (`stub`, `reading`, `completed`); the latest line for a chapter is its state.
- The owner zone (summary callout, `Detail`, `Thinking`, `공명`, `Highlight`) is never written by ingest. `Highlight` is filled by the owner or a highlight-sync tool such as bstack `millie`, which quotes each highlight with a page or, where the bookstore gives none, the highlight date.
- `status`, `bookstore`, `date_started` and `date_finished` record the owner's reading and are omitted from a new note; ingest never sets or changes them.

## Scaffold

```markdown
---
type: {{live_policy_type}}
aliases: []
description: "{{english_one_or_two_sentences}}"
author:
  - "[[{{book_author}}]]"
model: {{runtime_model}}
effort: {{runtime_effort_or_default}}
date_created: {{today}}
date_modified: {{today}}
tags: []
title: "{{title}}"
subtitle: "{{subtitle}}"
isbn: "{{isbn13}}"
publisher: "{{publisher}}"
date_published: {{YYYY-MM-DD}}
total_page: {{integer}}
cover_url: "{{cover_url}}"
source_url: "{{bookstore_or_publisher_url}}"
source:
  - "[[{{raw_source}}]]"
related: []
---

# {{title}}

> [!summary]+ Summary

## Detail

## Thinking

## 공명

## Highlight

## From Sources

- {{YYYY-MM-DD}} {{fact_or_mention}} — [[{{raw_source}}]]

### Bibliographic Record

- ISBN {{isbn13}} · observed — [{{bookstore}}]({{url}})
- Publisher {{publisher}}, {{date_published}} · observed — [{{bookstore}}]({{url}})
- Cover {{cover_url}} · observed — [{{bookstore}}]({{url}})
- {{three_line_summary}} · inferred
- {{reading_context}} · owner

### Table of Contents

Source: [{{bookstore_or_publisher}}]({{toc_url}}) · {{observed|OCR}}

- {{part_or_chapter_title}}

### Chapters

- [[{{chapter_raw}}]] — {{toc_entry}}

### Reading Progress

- {{YYYY-MM-DD}} ch{{NN}} {{stub|reading|completed}} — [[{{chapter_raw}}]]

### Derived

- [[{{term_concept_or_guide}}]]

### Sources

- [[{{raw_source}}]]

### Related

- [[{{related_page}}]]
```
