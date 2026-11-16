# Audit report shape

Use these sections in this order, in conversation and in the saved note. Every count is n of total, the denominator being what was examined; every score covers only the examined scope.

## Vault Health

Composite (arithmetic mean) and the three sub-scores — Eligibility, Consistency, Confirmability — each 0–100, with the weights used.

## Scope and coverage

- Requested scope and how it was resolved (`--full`, `--moc`, `--recent`, `--confidence high`).
- Phase 0 inventory: Wiki pages, Maps, Raw notes, query notes, pages in at least one Map, audit-orphan pages.
- Phase C sample: size of each group, total sampled, total in scope, stratification used.
- Not examined: clusters, groups or pages skipped, with the reason.

## Phase A — Eligibility Sweep

Coverage table per dimension: `claimType`, `evidenceScope`, `confidence`, `explored`, `verificationStatus`, `source`, `related`; Raw `collectionPurpose`; H1, Sources, Related; Bias Check on high-confidence pages. Undeclared synthesis-only pages and policy violations as counts. Up to twenty failing paths per dimension; the rest counted.

## Phase B — Map-Cluster Consistency

Grouped by Map. Per conflict: pages involved, quoted claim lines, kind (different definition, contradicting empirical claims, contradicting prescriptions, divergent interpretations of one Raw), proposed action (`verify --resolve`, queued only). Then cross-Map conflicts, hallucination suspects, audit-orphan pages with a recommended Map, and how oversized clusters were split.

## Phase C — Confirmability Calibration

Table of page, declared confidence, recommended confidence, verdict. Overclaim and underclaim lists. Bias Check coverage on high-confidence pages.

## Top 10 Recommended Actions

At most ten `verify [[Page]] — reason` lines in priority order; `STALE FLAG` repeats first. A count of further candidates and any `lint`/`ingest` follow-ups.

## Drift Since Last Audit

When `--compare` was given or a prior audit report exists: score deltas, per-criterion count changes, pages flagged both times. Otherwise state that no prior audit was found.

## Limits

What the sample cannot show, Raw notes not opened, and any tool that was unavailable.
