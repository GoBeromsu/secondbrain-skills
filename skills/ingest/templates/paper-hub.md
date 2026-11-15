---
type: paper-hub
aliases:
  - "{{surname}} {{year}} Hub"
description: "{{english_summary_of_the_paper_and_its_twelve_axis_scope}}"
author:
  - "{{live_policy_author_or_agent_role}}"
model: {{runtime_model}}
effort: {{runtime_effort_or_default}}
date_created: {{today}}
date_modified: {{today}}
tags:
  - paper-hub
  - "{{paperType}}"
paperType: {{quantitative|qualitative|theory-concept|mixed-methods|scale-development|meta-analysis}}
citekey: "{{registered_or_authYearShorttitle}}"
doi: "{{doi_or_omit}}"
targetManuscript: "{{[[RQ-slug]]_or_none}}"
collectionPurpose: "{{owner_answer_verbatim_or_stated_inference_and_reason}}"
source:
  - "[[{{raw_source}}]]"
related: []
explored: false
verificationStatus: unverified
status: active
---

# {{surname}} {{year}} - S00 Hub

> [!info] Paper Hub
> **{{authors}} ({{year}})**, *{{paper_title}}* — twelve-axis analysis anchor; atoms in the Atom Catalog, axes in the Step Map.
> **Collection context**: "{{collectionPurpose_gist}}" → {{RQ_link_or_collection only}}

<!-- Only when citekeyProvisional: true. -->
> [!warning] Provisional citekey
> `{{citekey}}` is locally generated; on registration pin the registered key to this value, never rename notes or folder.

<!-- Only when the Raw was converted with quality issues. -->
> [!warning] Conversion quality
> Conversion: {{tool_and_fidelity}}. Check: {{lost_formulas_tables_footnotes}}. Page locators: {{restored_or_section_only}}.

---

## S01 Citation

- **Full citation**: {{full_reference_as_printed}}
- **citekey**: {{citekey}}
- **DOI**: {{doi_or_none}}
- **Raw Source**: [[{{raw_source}}]]

---

## Abstract Summary

{{three_to_five_line_compression; the verbatim abstract stays in the Raw}}

---

## Coverage Map

| Source section | Knowledge atom |
| --- | --- |
| Abstract | (hub Abstract Summary) |
| §{{section}} | [[{{atom}}]] · [[{{atom}}]] |
| References | (kept in the Raw) |

---

## Step Map

| S | Step name | Atoms | Status |
| --- | --- | --- | --- |
| 1 | CITATION | (hub) | compiled |
| 2 | {{step_name}} | {{n}} | {{planned|compiled|stub M|skipped (reason)}} |
| 3 | {{step_name}} | {{n}} | {{status}} |
| 4 | {{step_name}} | {{n}} | {{status}} |
| 5 | {{step_name}} | {{n}} | {{status}} |
| 6 | {{step_name}} | {{n}} | {{status}} |
| 7 | {{step_name}} | {{n}} | {{status}} |
| 8 | {{step_name}} | {{n}} | {{status}} |
| 9 | {{step_name}} | {{n}} | {{status}} |
| 10 | CONCLUSIONS | {{n}} | {{status}} |
| 11 | {{step_name}} | {{n}} | {{status}} |
| 12 | DISCUSSION / WRITING VALUE | {{n}} | {{status}} |

---

## Atom Catalog

### S{{NN}} — {{step_name}} ({{n}} atoms)

- [[{{surname}} {{year}} - S{{NN}} {{atom_title}}]] — {{the_one_question_it_answers}}
	- [[{{surname}} {{year}} - S{{NN}} {{sub_atom_title}}]] — {{the_one_question_it_answers}}

---

## Target Manuscript

- {{[[RQ-slug]] — what the paper contributes there (cites / evidenceFor / evidenceAgainst)}} or `none` — collection only (12-axis analysis only)

---

## Wiki Promotions

- [[{{promoted_page}}]] ({{layer}})

---

## Related

- [[{{related_hub_or_page}}]]

---

> [!note] Compile Plan
> Temporary P-3a output; delete when the hub is finished.
> Mining points: {{section_to_atom_draft}}
> Sibling links: {{atom_to_atom_link_plan}}
> Strategy and batches: {{fan_out|importance_order|progressive_stub}}
