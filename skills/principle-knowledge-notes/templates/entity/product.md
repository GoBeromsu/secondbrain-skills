# Product Entity

Use for named software, services, libraries, repositories, agents, models and datasets. The product is the Entity; its README, documentation or release notes are source evidence, not the note.

Follow [Entity maintenance](../entity.md#maintenance) within the requested write scope and the destination's live frontmatter schema. Fill known values, preserve existing provenance, and report unknown required fields. A new template alone does not authorize converting an existing note.

## What the page is for

The owner opens a Product page to answer what a README cannot: why this product matters to them, where it came from, how it really works, and what they concluded from using it. A page that restates one source's feature list fails that reader even when every sentence is true. The owner's reason for keeping the product is the spine of the page: it shapes the TL;DR, decides which mechanism the Explanation follows, and anchors Personal Insights.

## Gather before writing

One source rarely carries all of that, so collect the evidence first and write second.

- **The maker's account.** Beyond the source that triggered the page, read the maker's own pages for origin and mechanism: an about or history page, the documentation of the feature the owner cares about, and the changelog or release notes for what changed. For a repository, read the README and the files that carry the claim at one commit. Every page actually read goes in `source` as a labeled link or its existing Raw. Aim for three or more distinct sources; when fewer could be read, say which were sought and not found instead of stretching one.
- **The owner's record.** Search the whole vault for the product's name and aliases with the available search tool and a keyword pass, not only the notes the request names: daily and periodic notes, project notes, essays, meeting notes, issues. Read each hit in its context and note its date. Mentions scattered over years are where the change of view lives; the three most recent hits miss it.
- **The limits.** For each claim, note what its evidence does not establish: a maker's retrospective is not independent research, a documented rule is not a measured effect, a note about an investigation is not a re-run of it.

When the vault holds no owner record, or the maker states no origin, write that in one sentence in the section concerned. A short honest section beats a padded one.

## Writing

Write without first-person framing, in the language the live policy sets for pages. Link existing canonical notes where the relationship matters; keep an unconfirmed target as plain text. Give links readable labels: a date as `[[2026-09-04|the date written out in the page's language]]`, a long dated note by a label that says what it is. Calendar links follow the vault's date policy.

- **TL;DR** says what the product is and, in bold, why it matters to the owner's work. Footnote the claims it rests on.
- **Origin** names who made it, when, their relevant background and the problem they said prompted it, then separates that account from what the product is today.
- **Explanation** opens with one concrete worked example and follows the mechanism the owner depends on. Bold the one reading a newcomer usually gets wrong. Scope changing features, prices and versions to the date or commit inspected, and point to the vault's own investigation notes with their stated limits.
- **Personal Insights** is organised under `###` headings named for a theme or judgment, never as a dated list of mentions. Each paragraph cites the records it draws on, quotes the owner's own sentence where that sentence carries the judgment, and keeps an earlier view beside the later one that replaced it. A conclusion the page draws that no record states is labelled as interpretation.
- **Footnotes** carry each sourced claim's locator (section title, file and commit, heading in a vault note) and the limit of that evidence. Use one named footnote per source passage and reuse it.
- **References** lists each external work once with a nested line giving its publication date, or that none is shown, and what was confirmed in it. Close with one paragraph: when the external sources were read, what was reviewed, and what was not re-verified.

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
  - "{{labeled_external_link_or_existing_raw_wikilink_for_each_source_read}}"
  - "{{wikilink_for_each_owner_record_used}}"
related: []
# Apply the live schema's full wiki-page fields when it uses that type.
# Add maker, url and repository only when sourced; use [] for unavailable lists.
---

# {{product_name}}

> [!abstract] TL;DR
> {{What it is and the problem it solves.}} **{{Why it matters to the owner's work.}}**[^mechanism][^use]

## Origin

{{Maker, date, background and the problem they said prompted it.}}[^origin]

{{How the product's present scope differs from that account, or that the maker states no origin.}}

## Explanation

{{A concrete worked example, then the mechanism the owner depends on and its limits, scoped to the inspected date, version or commit.}}[^mechanism]

## Personal Insights

### {{Theme or judgment}}

{{What the owner's records show about use, friction and reconsideration, each linked to its record. Keep changes of view; label new interpretation.}}[^use]

## References

- {{Author or publisher}}. [{{Title}}]({{url}}).
	- {{Publication date or that none is shown. What was confirmed there.}}

{{When the external sources were read, what was reviewed, and what was not re-verified.}}

[^origin]: {{Locator. What this evidence does not establish.}}
[^mechanism]: {{Locator. What this evidence does not establish.}}
[^use]: {{Vault note and heading. What the record alone does not confirm.}}
```
