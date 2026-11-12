---
name: "audit"
description: "Audits Wiki quality read-only: samples pages per Map cluster for eligibility, consistency and confirmability, scores them and queues verify follow-ups. Use for a vault health audit, periodic knowledge review or picking pages to verify next. Link and frontmatter health belongs to lint, one page's claims to verify."
license: MIT
---

# Audit

Whole-vault knowledge integrity audit. Audit applies the same three criteria as `verify` — 지식요건해당성 (Eligibility), 정합성 (Consistency), 확증가능성 (Confirmability) — at scale, through Map clusters and prioritized sampling. It does not verify every page; it scores the sampled scope, surfaces drift patterns and ranks the next `verify` calls. Audit is the planner; `verify` is the worker.

Audit is a read-only diagnostic on the vault. It never regenerates the Wiki, rewrites a page, or sets a page property; follow-ups route to `verify`, `lint` or `ingest`. An owner goal to improve the entire Wiki becomes a ranked queue of single-page follow-ups, never blanket regeneration. The only writes are the report note and its `log.md` entry, both only after the owner approves saving. A `--no-save` or unapproved run writes nothing — no report, no log entry, no index change. Never commit or push; commit only when the owner separately asks.

Every finding is stated against what was actually read. Unread pages are "not examined", never "clean"; a score covers only the examined scope and says so.

Tools: `rg` for the deterministic sweep, `qmd query` for semantic counter-evidence, `obsidian-cli` for backlinks when Obsidian runs.

## Input

Read the Core Context once per session (reuse it if already read this session) and the destination's live policy for where Raw, Wiki, Map and query notes live; do not assume folder names. The owner names the scope:

- empty or `--full`: every Wiki page;
- `--moc {Map}`: one Map cluster;
- `--recent {N}`: pages whose `date_modified` falls within N days (fall back to the file modification time when the field is absent, and say so);
- `--confidence high`: `confidence: high` pages only;
- `--no-save`: report in conversation only;
- `--compare {report}`: an earlier audit report to diff against; when absent, use the most recent saved audit report if one exists.

Never widen a cluster or folder into the whole vault unasked. The criteria, Claim Type Taxonomy and Evidence Scope Levels are owned by `verify`; field names follow `ingest`'s frontmatter reference.

## Scaling Strategy

| Criterion | At single page (`verify`) | At vault scale (audit) |
| --- | --- | --- |
| **Eligibility** | full per-claim check | deterministic sweep — coverage and gaps |
| **Consistency** | full cross-page search | Map-cluster batched — each Map is one semantic cluster |
| **Confirmability** | full calibration | prioritized sampling — every `high`, every stale `explored: false`, every `disputed: true`, a stratified tenth of the rest |

## Process

### Phase 0 — Inventory

Count Wiki pages, Maps, Raw notes and query notes in scope, then build cluster membership from Map bodies: each Map's outgoing wikilinks to Wiki pages is one cluster. A Map is the parent context of its pages; read a page through the Map that holds it.

Record pages in at least one Map, **audit-orphan pages** (in zero Maps), and the largest and smallest clusters. Audit-orphans enter Phase A and cannot be cluster-reviewed in Phase B. Print the inventory before Phase A.

### Phase A — Eligibility Sweep (deterministic)

Pure search, no judgment. Report each check as n/total plus at most twenty failing paths.

- **A.1 Frontmatter coverage.** Wiki: `claimType`, `evidenceScope`, `confidence`, `explored`, `mainVaultRelated`, `verificationStatus`, plus `source` and `related`. A `source` wikilink that does not resolve is recorded for Phase D. `explored: false` is review backlog, not a failure. Raw: `collectionPurpose` presence.
- **A.2 SPO structure.** H1, `## Sources`, `## Related` present; every `confidence: high` page carries a Bias Check.
- **A.3 Source citation density.** Pages citing no Raw note are synthesis-only; they must declare `evidenceScope: synthesis-only`. An undeclared one is a finding.
- **A.4 Policy violations.** Count the mechanical rules the live policy states (YAML indent, body indent, unquoted wikilinks in YAML other than intentional `author` wikilinks, unquoted Mermaid labels, a page whose `layer` mismatches its folder). Repair belongs to `lint`.

Output: coverage table per dimension, failing paths (top twenty per dimension), and the **Eligibility score** — weighted percentage of pages passing frontmatter coverage, SPO presence and claim type assignability.

### Phase B — Consistency Clusters (batched)

Each Map cluster is reviewed on its own; clusters are independent, so when the scope is too large to review in one context, split clusters across parallel sub-tasks — pass paths, receive one line per finding, never page bodies.

For each cluster:

1. **Load cluster** — read the Map and every page it links.
2. **Extract claims** — from each page its three to five central claims (Subject · Predicate · Object).
3. **Cross-compare** within the cluster:
   - same concept, **different definition** — the commonest drift;
   - **contradicting empirical claims** — different numbers, dates or attributions for the same fact;
   - **contradicting prescriptions** — "always X" on one page, "avoid X" on another;
   - **same Raw Source, divergent interpretations**.
4. **Report conflicts** — the pages involved, the quoted claim lines, the kind, and the proposed action.

**Conflict action default:** queue `verify --resolve` on both pages; `verify`, the only producer of page `disputed`, then marks both `disputed: true` with the owner's authorization and adds cross-linked `> [!warning] Contradiction` callouts keeping both sides attributed. Audit itself never writes `disputed` or a callout; it queues the action. Silence on a point is not a contradiction. A secondary page restating a primary study is not independent corroboration of it, and a page attributing a secondary author's interpretation to the original creator is itself a finding.

**Audit-orphan handling:** group Map-less pages into per-tag pseudo-clusters by their top three tags, or list them as unclusterable with a recommended Map assignment.

Output: per-Map conflict list, cross-Map conflicts (same claim contested in two Maps), **hallucination suspects** (numbers, dates or quotations not found in any cited Raw — sampled here, confirmed only by `verify`), and the **Consistency score** `100 − (5 × Map conflicts) − (10 × hallucination suspects) − (2 × policy violations)`, floored at 0.

### Phase C — Confirmability Sampling (prioritized)

The target population is the union of, in priority order:

1. **All `confidence: high` pages** — read in full, not sampled.
2. **Stale unexplored backlog** — `explored: false` and `date_modified` more than 30 days ago.
3. **Disputed pages** — `disputed: true` or `verificationStatus: disputed`, even if previously verified.
4. **Random 10% stratified sample of the remainder** — stratified by `layer` (terms, concepts, entities, guides, and the vault's other layers) and Maps; never plain random.

State each group's size and the total sampled against the total in scope.

For each target, an abbreviated `verify` Confirmability read:

- count primary, secondary and user-original sources;
- search the Wiki for counter-evidence by exact term (`rg`) and by meaning (`qmd query`);
- compute the recommended `confidence` with `verify`'s matrix;
- flag **overclaim** (`high` on a single source) and **underclaim** (`low` despite strong evidence);
- check Bias Check presence on high-confidence pages.

Audit proposes `confidence`; it never writes it, nor `verificationStatus` or `disputed`. Partition targets into batches of about twenty; run batches in parallel only when the target set is too large to read in one context.

Output: confidence calibration table (page, declared, recommended, verdict), overclaim list, underclaim list, Bias Check coverage on high-confidence pages, and the **Confirmability score** — weighted average of calibration alignment and high-confidence Bias Check coverage.

### Phase D — Synthesis

Compute three scores 0–100 and the **composite Vault Health**:

| Score | Formula |
| --- | --- |
| **Eligibility** | weighted avg of frontmatter coverage + SPO presence + claim type assignability |
| **Consistency** | `100 − (5 × Map conflicts) − (10 × hallucination suspects) − (2 × policy violations)`, floored at 0 |
| **Confirmability** | weighted avg of calibration alignment + Bias Check coverage (high-confidence only) |
| **Composite** | arithmetic mean of the three |

State weights used and that every score covers only the examined scope. Then the **Top 10 actions**, each `verify [[Page]] — reason`, ranked by:

- pages involved in multiple conflicts (Phase B);
- overclaim pages with declared `confidence: high` (Phase C);
- pages with broken `source` wikilinks (Phase A);
- high-traffic pages (referenced from many `related`) with low confirmability.

`STALE FLAG` repeats (Failure Mode 3) go first. Mechanical findings route to `lint`; missing source material routes to `ingest`.

### Phase E — Save report (on approval)

Report in the conversation first, using [report](references/report.md). Unless `--no-save`, ask whether to save; only on approval:

1. Save `YYYY-MM-DD-Q-vault-audit.md` at the live policy's query location, with the vault's query-result template and frontmatter (`date_created`, `date_modified` snake_case; other fields as live policy defines). Body sections follow [report](references/report.md), including `## Vault Health` and `## Drift Since Last Audit`.
2. Append to `log.md` (append-only, never rewrite earlier entries):

```markdown
## [YYYY-MM-DD] audit | {scope}

- Health: {composite}/100 (E:{eligibility} C:{consistency} K:{confirmability})
- Conflicts: {N} | Overclaim: {N} | Coverage gaps: {N}
- Report: [[YYYY-MM-DD-Q-vault-audit]]
```

Without approval, or with `--no-save`, write nothing.

## Output

Print the summary following [report](references/report.md): Vault Health composite, then 1. Eligibility (지식요건해당성), 2. Consistency (정합성), 3. Confirmability (확증가능성) each with its score and key counts, the Top 10 `verify` queue, the report path when saved, and drift versus the last audit.

## Failure Modes

1. **Map out of sync** — a page names a Map in `related` but the Map does not link it, or the reverse. Leave it out of the cluster; flag it as a Map sync gap for `lint`.
2. **Oversized cluster** — a Map with 50+ linked pages. Subdivide by tag intersection and audit each sub-cluster separately; say how it was split.
3. **Audit storm** — the same pages flagged in two consecutive audits with no `verify` since become a `STALE FLAG` at the top of the action list.
4. **Concurrency safety** — audit is read-only on Wiki pages; the report and `log.md` writes happen only in Phase E, serialized, after approval. Page changes wait for the `verify` the owner starts.
5. **Confirmability vs source ground truth** — Phase C reads cited Raw only partly. A flagged page is a candidate; the definitive source check is `verify` on that page.
6. **Action list explosion** — cap the list at ten and say how many more are in the report.
7. **Silent coverage loss** — a cluster or group skipped for time is reported as not examined, with the reason.

## Integration

Audit consumes the keys `verify` writes (`claimType`, `evidenceScope`, `verificationStatus`, `disputed`); a first audit after they are introduced shows low coverage — that is the backfill baseline. `lint` owns mechanical health: broken links, orphans, frontmatter presence, `mainVaultRelated` resolution. `verify` owns per-claim review and any change to `confidence`, `explored`, `verificationStatus` or `disputed`. Run `lint` before an audit so mechanical noise does not crowd the epistemic findings; after a large `ingest`, audit only the touched Map clusters with `--moc`. The owner sets the cadence.
