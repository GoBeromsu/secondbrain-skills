---
aliases: {existing aliases}
author: {existing author list}
date_created: {existing creation date}
date_modified: {today, YYYY-MM-DD}
description: "{existing description}"
effort: {runtime-reported effort, or default}
model: {existing model ids plus runtime-reported model ids, deduplicated}
personaDomains: {existing domains}
personaMaturity: {existing maturity}
personaOf: "[[{existing Entity}]]"
related: {existing related notes}
source:
  - {each existing source, in order}
  - "[[{this Raw source}]]"
tags: {existing tags}
type: persona
# Update date_modified and runtime provenance and append this Raw to source. Never change personaMaturity (verify- or owner-gated).
---

# {Existing Persona title}

<!-- Append recipe for an EXISTING Persona card only (Step 7). Never create a Persona during ingest; creation is owner-nominated. Keep every existing key, value and section; change only what is listed here. -->

## Quote Bank

<!-- Append 1–3 quotes; each must grep-match this Raw's ## Original Content verbatim. -->
> [!quote] {topic} ({YYYY-MM-DD}, [[{this Raw source}]])
> {verbatim quote}

## Position Timeline

<!-- Append one dated row only when the source states or shifts a position. -->
| Date | Position | Source |
| --- | --- | --- |
| {YYYY-MM-DD} | {attributed position} | [[{this Raw source}]] |

<!-- Only when this source explicitly conflicts with an earlier position; keep both rows. Silence is not a contradiction. -->
> [!warning] Contradiction
> {earlier position with source} / {new position with source}

## Accumulation Log

- {YYYY-MM-DD} · [[{this Raw source}]] → {what was added}
