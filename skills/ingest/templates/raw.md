---
type: raw-source
aliases:
  - "{{short_name}}"
description: "{{english_one_or_two_sentences}}"
author:
  - "[[{{original_author}}]]"
model: {{runtime_model}}
effort: {{runtime_effort_or_default}}
date_created: {{today}}
date_modified: {{today}}
date_ingested: {{acquisition_date}}
date_published: {{publication_date_when_known}}
language: {{source_language}}
length: "{{source_length}}"
tags:
  - raw-source
  - {{topic_tag}}
source: "{{canonical_url_or_reference}}"
category: {{Articles|Papers|Books|Transcripts|Clippings|AI Research|live_policy_registered_category}}
collectionPurpose: "{{owner_answer_verbatim_or_stated_inference_with_reason}}"
related: []
referenced: []
status: ingested
# Omit date_published when inapplicable.
# Converted document: add source-attachment, source-format, conversion-tool, conversion_date, conversion-fidelity.
# Fill slots as YAML-serialized values: one author item per person; a name containing " or \ is escaped by YAML double-quoted rules inside "[[...]]".
---

# {{title}}

## Original Content

{{verbatim_source_content}}

## Ingest Notes

{{only_when_there_is_something_to_record_otherwise_delete_this_section}}
