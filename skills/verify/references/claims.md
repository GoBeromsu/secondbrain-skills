# Claims — Claim Type Taxonomy, Evidence Scope Levels, primary or secondary

Read this during classification and calibration. `claimType` and `evidenceScope` values are exactly those of `ingest`'s frontmatter reference; `verify` writes them to frontmatter on approved write-back.

## What counts as a claim

A claim is a sentence a reader could be wrong to rely on: it asserts what something is, what happened, what was measured, what works, or what it means. Headings, questions, link lists and plans are not claims. When a paragraph strings several assertions together, split it; one verdict per assertion.

Extract up to **10 major claims** per page. When the page holds more, prefer, in order: claims the owner named; claims the page's description or Overview depends on; concrete claims (numbers, dates, names, quotations, attributions); claims other pages link to for support; the rest. Say in the report how many claims the page holds and which ones were left out.

## Claim Type Taxonomy (6 types + `mixed`)

Name one type per claim. The type decides what evidence would settle it.

| Type | Definition | What settles it |
| --- | --- | --- |
| `definition` | What X *is* | The source that coined or standardised the term, and agreement with how other pages use the same word. |
| `empirical` | Measurable fact | Only the figure, with its unit and conditions, found in the cited source. A rounded or re-derived figure is a finding, not a pass. |
| `theoretical` | Framework, pattern, hypothesis | Locating who proposed it, and checking the page states it as theirs, not as established fact. |
| `historical` | Event, timeline, attribution | A dated, attributable source; a later retelling is weaker than a contemporaneous record. |
| `prescriptive` | How-to, recommendation, norm | Whose advice it is and under what conditions it was given; advice stripped of its conditions is a finding. |
| `interpretive` | Synthesis, opinion, judgment | No source can confirm it; it can only be fairly attributed and bounded. Ask whether it is labelled as interpretation and whether a Bias Check names its strongest counter. |

Use `mixed` for a page whose claims span several types; that is a description, not a defect.

## Primary or secondary (external criticism)

For each claim, judge provenance first: who created it decides what the source can prove.

- **Primary**: the creator of the cited Raw produced the claim — their own measurement, argument or account.
- **Secondary**: the cited Raw reports another creator's work — a newsletter citing a study, a talk quoting a paper, a post summarising a benchmark.
- **User-original**: the claim rests on the owner's own mothership notes; it is confirmable only as "the owner holds this".

For a secondary claim, follow the Raw's `referenced` list to the original. `referenced` names originals and earlier captures; it never proves the original was read and never authorizes fetching it.

- original already in Raw → check the claim against the original, not the retelling, and note where the retelling drifted;
- original linked only as an Inbox candidate, or as a Book Index whose chapter is still unread (no chapter text in Raw) → the claim is unconfirmed at the original; report the candidate and recommend ingesting it; the citing Raw is not proof;
- no `referenced` entry and no locatable original → provenance unknown; the claim can at most be attributed to the secondary author, never confirmed as the original creator's finding.

A quotation inside a secondary source is not the original. Attribution that silently moves a secondary author's interpretation onto the original creator is a Consistency failure, even when both texts exist.

## Evidence Scope Levels (5)

Describe how far the page's support reaches, once for the page and per claim where it differs.

| Scope | Meaning |
| --- | --- |
| `single-source` | One Raw backs the page. |
| `multi-source-primary` | 2+ Raw, all primary, from different creators. |
| `multi-source-mixed` | Primary + secondary (commentary, interpretation). |
| `synthesis-only` | Derived from other Wiki pages, no direct Raw. |
| `user-original` | Sourced from the owner's mothership notes. |

Count lines of evidence, not links: two Raw from the same creator, or a secondary that only repeats one primary, are one line. `multi-source-mixed` means primary **plus** secondary; secondary-only support is never `multi-source-mixed`. When support is secondary only (originals unacquired or unknown): one secondary Raw is `single-source` ("one Raw backs the page"). Two or more secondary Raw with no primary fit none of the five upstream values — `multi-source-primary` needs all primary, `multi-source-mixed` needs a primary. Upstream defines no value for this case and none is invented: leave `evidenceScope` unwritten (unknown stays unknown) and record in the report "secondary-only, originals unacquired; no upstream evidenceScope value fits".

## Confidence calibration

`confidence` keeps its schema meaning: `high` well-sourced, `medium` partial, `low` speculative. Recommend it **independently** — from source count, source type and counter-evidence, without looking at the declared value — using the upstream matrix (Claude `verify.md` Phase 3.3), sources counted as primary per the section above:

| Conditions | Recommended `confidence` |
| --- | --- |
| 3+ primary sources, no counter-evidence, age > 30 days, no unresolved Consistency conflicts | `high` |
| 1-2 primary sources, no counter-evidence | `medium` |
| Single source OR `synthesis-only` OR created < 7 days ago | `low` |
| Counter-evidence present and unresolved | `disputed` |

The `low` row's "created < 7 days ago" reads the page's `date_created`. The `high` row's "age > 30 days" names no field (page creation, last change, or source age are all plausible), so that condition is reported as unknown: a page otherwise meeting `high` is reported as "`high` pending age basis", never promoted to `high` on an assumed clock, and no OVERCLAIM is raised against a declared `high` on age alone. The source-count, source-type and counter-evidence conditions stay usable as stated. The `disputed` row is reported as the page's `disputed` / `verificationStatus` state; the `confidence` field itself stays within high/medium/low (schema).

The bands overlap and leave gaps, and they are kept as written; no resolving threshold is added. Report the overlap to the owner as stated uncertainty, naming which rows apply:

- one primary source matches `medium` (1-2 primary) and `low` (single source);
- a page created < 7 days ago with 1-2 primary sources matches both `medium` and `low`;
- 3+ primary sources with the `high` age condition unknown or unmet match no `high` row — only the `medium` row's source condition, which names 1-2;
- secondary-only support meets no primary-count row; a single secondary Raw is `low` (single source); several secondary Raw match no row.

Compare to the declared value:

- Declared > recommended → **OVERCLAIM** (CLAUDE.md shorthand: high-confidence + single source); propose a downgrade or name the sources that would justify it.
- Declared < recommended → **UNDERCLAIM** (CLAUDE.md shorthand: low-confidence + multi-source). The multiple sources must be **primary**: under the matrix only primary sources raise the recommendation above `low`, so several secondary Raw never make an UNDERCLAIM. Propose an upgrade.
- Otherwise MATCH; when the page falls in an overlap, report MATCH or the flag for each applicable row and leave the choice to the owner.

Any change is a proposal until the owner approves it.

## Bias Check

When the page is, or would be, `high`, or rests mostly on synthesis, it needs a `> [!note] Bias Check` (ingest's Concept template places it under Details). If it is missing or generic, draft one for this page's central claim: the strongest counter-argument a careful critic would make, and the specific data gap — the missing original, the absent replication, the unexamined counter-case. A placeholder sentence does not count.
