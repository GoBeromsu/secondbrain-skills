---
type: paper-analysis
aliases:
  - "{{surname}} {{year}} S{{NN}}"
description: "{{english_one_line_on_the_single_question_this_atom_answers}}"
author:
  - "{{live_policy_author_or_agent_role}}"
model: {{runtime_model}}
effort: {{runtime_effort_or_default}}
date_created: {{today}}
date_modified: {{today}}
tags:
  - paper-analysis
  - "{{paperType}}"
paperType: {{paper_type}}
citekey: "{{citekey}}"
analysisStep: {{integer_2_to_12}}
analysisStepName: "{{step_name_exactly_as_in_papers_md}}"
paperHub: "[[{{surname}} {{year}} - S00 Hub]]"
source:
  - "[[{{raw_source}}]]"
related:
  - "[[{{sibling_atom}}]]"
status: {{completed|stub}}
explored: false
verificationStatus: unverified
---

# {{surname}} {{year}} - S{{NN}} {{atom_title}}

> [!info] Analysis Context
> **Paper**: {{authors}} ({{year}}), *{{paper_title}}* — [[{{surname}} {{year}} - S00 Hub|hub]] · [[{{raw_source}}|Original]]
> **Collection context**: "{{collectionPurpose_gist}}" → {{RQ_link_or_collection only}}
> **Position**: Step {{N}} / 12 — {{step_name}} ({{paperType}}) · Original §{{section}}
> **This atom**: {{the_one_question}}. Neighbours: [[{{neighbour}}]]

<!-- A stub (progressive) keeps only the Analysis Context and one line under Plain Introduction stating the question. -->

---

## Plain Introduction

{{one_or_two_paragraphs_for_a_reader_new_to_the_idea}}

---

## Close Reading

{{the_authors_definition_and_argument_with_mechanisms_and_distinctions}}

---

## Examples

- {{example_from_the_original}}
- [Analyst note] {{analyst_example_marked_as_not_the_authors}}

---

## Source Evidence

<!-- Guidance: two to six quotes per atom, not a quota. Hard: verbatim from the Raw's Original Content and a page-first locator in every header. -->

> [!quote] Original (p.{{page}}, §{{section}})
> "{{verbatim_from_raw_original_content}}"

---

## Concept Relations

- Role in the argument: {{what_breaks_without_this_atom}}
- [[{{sibling_atom}}]]: {{distinction_or_link}}
- Wiki: [[{{promoted_page}}]]

---

## My Manuscript Context

{{optional_reading_against_targetManuscript}}

---

## Open Questions

> [!question] Open Question
> {{point_to_recheck_in_the_original}}
