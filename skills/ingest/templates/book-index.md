---
type: raw-source
aliases:
  - "{{book_title_short}}"
description: "{{english_one_or_two_sentences_about_the_book}}"
author:
  - "[[{{book_author}}]]"
model: {{runtime_model}}
effort: {{runtime_effort_or_default}}
date_created: {{today}}
date_modified: {{today}}
date_ingested: {{scaffold_date}}
date_published: {{publication_date_when_known}}
tags:
  - raw-source
  - {{book_slug}}
source: "{{preface_or_index_url}}"
category: {{Books|live_policy_or_owner_task_category}}
collectionPurpose: "{{owner_answer_verbatim_or_stated_inference_with_reason}}"
related: []
referenced: []
status: ingested
# No chapter keys on the Index. Omit date_published when inapplicable.
---

# {{book_title}}

> [!info] Source
> Original source: {{preface_or_index_url}}

---

## Original Content

{{verbatim_preface}}

---

## TOC

### {{part_in_original_language}}

- [ ] [[{{chapter_stub}}]] — {{verbatim_toc_one_liner}}

---

## Reading Paths

<!-- Only when the author provides reading paths; verbatim. Omit the section otherwise. -->
{{author_reading_paths_verbatim}}

---

## Progress Tracking

| Ch | Title | Status | Read on |
| --- | --- | --- | --- |
| {{chapter_number}} | [[{{chapter_stub}}]] | stub | — |

---

## Ingest Notes

{{verified_chapter_url_pattern_and_coverage_limits}}
