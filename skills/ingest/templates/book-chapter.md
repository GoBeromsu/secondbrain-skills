---
type: raw-source
status: stub
aliases:
  - "ch{{NN}} {{chapter_title}}"
description: "Chapter {{N}} of {{book}}: {{toc_one_liner_in_english}}. Stub until read."
author:
  - "[[{{book_author}}]]"
model: {{runtime_model}}
effort: {{runtime_effort_or_default}}
date_created: {{today}}
date_modified: {{today}}
date_ingested: {{scaffold_date}}
tags:
  - raw-source
  - stub
  - {{book_slug}}
  - {{topic_tag_from_toc}}
source: "{{verified_direct_chapter_url}}"
category: {{Books|live_policy_or_owner_task_category}}
collectionPurpose: "{{inherited_book_purpose}}"
related: []
referenced: []
book: "[[{{book_entity}}]]"
chapterNumber: {{integer}}
chapterPart: "{{part_in_original_language}}"
chapterPrev: "[[{{previous_stub}}]]"
chapterNext: "[[{{next_stub}}]]"
# chapterPrev is null on the first chapter, chapterNext null on the last.
# Fill slots as YAML-serialized values: one author item per person; a name containing " or \ is escaped by YAML double-quoted rules inside "[[...]]".
# Promotion: status stub -> completed (full chapter) or reading (partial), only after the chapter was actually read and fetched.
---

# Ch{{NN}}: {{full_chapter_title}}

> [!info] Reading Status: Stub
> This chapter has not been read yet. Only the TOC one-liner is preserved. Re-invoke ingest on this file after reading to fill the body verbatim, compile its Wiki pages and promote the status.

## Source

- Original URL: {{verified_direct_chapter_url}}
- Book: [[{{book_entity}}]]
- Previous: [[{{previous_stub}}]] · Next: [[{{next_stub}}]]

## TOC Preview

{{verbatim_toc_one_liner}}

## Original Content

<!-- STUB: pending verbatim fill. Placeholder intentionally non-empty to satisfy the Raw pre-flight. -->

_This chapter body is empty while `status: stub`. Re-invoking ingest on this file fetches the chapter from its original URL and fills this section verbatim._

## Reading Notes

<!-- Notes, questions, wiki-promotion candidates added while reading -->
