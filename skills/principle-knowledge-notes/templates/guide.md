---
type: wiki-page
aliases:
  - "{{alternative_name}}"
description: "{{english_one_or_two_sentences}}"
author:
  - "{{live_policy_author_or_agent_role}}"
model: {{runtime_model}}
effort: {{runtime_effort_or_default}}
date_created: {{today}}
date_modified: {{today}}
tags: []
source:
  - "[[{{raw_source}}]]"
related: []
confidence: {{high|medium|low}}
layer: guides
explored: false
verificationStatus: unverified
status: active
# Fill slots as YAML-serialized values: lists stay lists (one item per existing source); a value containing " or \ is escaped by YAML double-quoted rules.
---

# {{guide}}

> [!tip] Key Insight
> {{what_this_method_achieves_in_one_line}}

---

## Overview

{{purpose_scope_and_limits_from_this_source}}

---

## Details

### Procedure

1. {{source_supported_step}}

### When to Use / When Not

- {{source_stated_condition}}

<!-- Only when this source explicitly conflicts with an existing claim; keep both, attributed, uncertainty stated. Silence is not a contradiction. -->
> [!warning] Contradiction
> {{claim_a_with_source}} / {{claim_b_with_source}}

<!-- Only for confidence: high or synthesis-heavy pages. -->
> [!note] Bias Check
> Counter-argument: {{counter_argument}}
> Data gap: {{data_gap}}

---

## Related

- [[{{related_page}}]]

---

## Sources

- [[{{raw_source}}]]

---

## Open Questions

> [!question] Open Question
> {{unresolved_question}}
