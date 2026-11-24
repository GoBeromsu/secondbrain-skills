# Term

Use this scaffold for a named domain term the reader wants to understand and reuse. Follow the [shared frontmatter contract](../../ingest/references/frontmatter.md) and the destination’s live policy.

- Search titles, aliases and linked uses for the same referent. Title it with the full original-language name, followed by the acronym in parentheses when one is in common use (`Work Breakdown Structure (WBS)`); never title it with the acronym or a translation alone. Keep the acronym, translated, former and variant names in aliases. Group related senses; qualify unrelated homonyms by field. Link to the whole Term and preserve a superseded definition with its date and source.
- Before writing, look the Term up in the vault with `obsidian-cli`, which matches what Obsidian itself resolves: `obsidian search query=<name>` for each title, alias, translation and spelling variant, `obsidian unresolved verbose` filtered to those names, and `obsidian backlinks` for an existing page.
	- Retarget every unresolved link to the same referent at the Term, keeping its display text (`[[이키가이]]` → `[[Ikigai|이키가이]]`). An alias alone does not resolve a link. Inside a Raw's `## Original Content`, change only the link target.
	- Fold an empty or stub note for the same referent into the Term: carry over its content and properties, retarget its links with `obsidian rename` or `obsidian move` so Obsidian rewrites them, and report the emptied note for the owner to delete.
	- Link the owner's notes that mention the referent from Personal Insights or `related`, quoting the passage; when the owner asks to link the mentions themselves, link the first mention in each note (`[[Term|original text]]`); plain text in a Raw's `## Original Content` stays unlinked.
- Give a new Term at least five distinct subject tags and list its domains as quoted English field wikilinks. For an external address in `source` or an existing `source_url` field, use a quoted `[label](URL)`; keep existing vault sources as wikilinks.
- Start with a definition and the finding or boundary that matters most. Explain it with a concrete example and distinguish the closest confusable idea. Keep the section order below, using only the roles the term needs. Merge overlapping material. Use a table or formula for a worked numerical comparison.
- Visualize the relationship a reader would otherwise have to reconstruct. Use `obsidian-visualize` for an inline Pele diagram beside its explanation: nest regions for containment, show transitions for changing state, or branch where paths diverge. Ground the relationships in the cited model or example. When a source defines the term with a diagram, draw that diagram's own structure, such as four overlapping circles as a Venn, rather than a flow of boxes. Leave a calculation in prose or a table when boxes would only repeat its steps.
- Compare studies by the question they answer. Explain what was done, who or what was measured, the unit and denominator, the result and its limits. Keep different outcomes distinct. Label hypotheses and separate original observations from replications and pooled estimates.
- Cite empirical, quantitative and historical claims at the passage, table or figure that supports them. Link the first author's surname and year directly to that location. Cite a group of related sentences or a table once when the scope is clear.
- Use native footnotes only for a quotation, method detail or caveat that interrupts the explanation. Let Obsidian number the matching `[^key]` reference and definition. Check quoted wording against the original; a paraphrase in the reader’s language can point to the original wording in the footnote.
- Use Personal Insights only for context found in the owner's actual notes. Quote accurately and link the note; distinguish their observation from the study outcome. Suggest a separate insight only if it stands on its own.
- In Related Terms, aim for three named links with a nested explanation under each. Check titles and aliases: list up to two existing notes, then one relevant term still missing, as a named wikilink without creating its page. Omit ungrounded slots. Keep frontmatter `related` for existing notes.
- List each cited work once in unnumbered References. Follow the owner's research style where known. Link an existing source note by wikilink or the first author and year to the full text; preserve coauthors, title, venue, DOI, available Raw and inspected scope. Keep the precise locator beside the claim.

## Scaffold

```markdown
---
type: wiki-page
aliases:
  - "{{translation_variant_or_former_form}}"
description: "{{english_one_or_two_sentences}}"
author:
  - "{{live_policy_author_or_agent_role}}"
model: {{runtime_model}}
effort: {{runtime_effort_or_default}}
date_created: {{today}}
date_modified: {{today}}
tags: ["{{tag_1}}", "{{tag_2}}", "{{tag_3}}", "{{tag_4}}", "{{tag_5}}"]
domain:
  - "[[{{english_field_name}}]]"
source:
  - "[[{{raw_source}}]]"
related: []
confidence: {{high|medium|low}}
definitionStatus: {{consensus|contested|emerging}}
layer: terms
explored: false
verificationStatus: unverified
status: active
---

# {{original_term_name}}

> [!abstract] TL;DR
> {{definition_and_key_finding_or_limit}}

## Explanation

{{how_it_works_with_a_concrete_example}}

## Where It Is Used

{{where_the_term_is_used_and_what_it_means_there}}

## Origin

{{history_that_clarifies_the_term}}

## Senses

{{distinct_meanings_with_field_and_example}}

## Literature Review

### {{question_the_evidence_answers}}

{{method_result_and_limit_with_claim_level_citation}}[^method]

## Personal Insights

{{owner_observation_and_link_to_its_context}}

## Related Terms

- [[{{existing_note}}]]
	- {{specific_relationship}}
- [[{{second_existing_note}}]]
	- {{specific_relationship}}
- [[{{named_missing_term}}]]
	- {{specific_relationship}}

## References

- {{linked_source_and_full_citation}} · {{inspected_scope}}

[^method]: {{optional_detail_and_precise_source_locator}}
```
