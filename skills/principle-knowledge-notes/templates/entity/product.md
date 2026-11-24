# Product Entity

Use for named software, services, libraries, agents, models and datasets. The product is the Entity; its README or release snapshot is source evidence.

Follow [Entity maintenance](../entity.md#maintenance) within the requested write scope and the destination's live frontmatter schema. Fill known values, preserve existing provenance, and report unknown required fields. A new template alone does not authorize converting an existing note.

Write without first-person framing. Link existing canonical notes where the relationship matters; keep an unconfirmed target as plain text. Use readable date labels such as `[[2026-09-04|2026년 9월 4일]]`, retaining the full filename when citing a longer dated note. Calendar links follow the vault's date policy.

## Scaffold

```markdown
---
type: {{live_policy_product_type}}
aliases: []
description: "{{short_english_description}}"
author:
  - "{{known_note_writer_under_live_policy}}"
model: "{{runtime_reported_name_or_id}}"
effort: {{runtime_effort_or_default}}
date_created: {{original_creation_date_or_today_for_new_note}}
date_modified: {{today}}
tags: []
source:
  - "{{existing_source_wikilink_or_labeled_external_link}}"
related: []
# Apply the live schema's full wiki-page fields when it uses that type.
# Add maker, url and repository only when sourced; use [] for unavailable lists.
---

# {{product_name}}

> [!abstract] TL;DR
> {{What it is, the problem it solves, and its relevance to the recorded work.}}

## Origin

{{Who made it, their relevant background, and the problem they said prompted it. Cite the creator's account; distinguish unknown motivation from the product's stated purpose.}}[^origin]

## Explanation

{{Explain the mechanism through a concrete example and its limits. Link relevant Terms or Concepts without redefining them. Scope changing features or prices to the inspected date/version; for repository evidence, name the commit and files read.}}

## Personal Insights

{{Connect actual use, friction, reconsideration and project decisions to their original records. Preserve changes of view; identify new interpretation. Explain what makes the product useful or unsuitable without a chronological mentions list.}}

## References

- {{External work or archived Raw: author/publisher, title, available date and source link. List each work once; cite personal records beside the experience they support.}}

[^origin]: {{Precise locator, quotation or evidence qualification. Keep supporting detail here; a recent edit does not verify other claims.}}
```
