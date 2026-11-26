# Lint report shape

Open with the scope and the link source used (which notes counted as inbound link sources), then one section per step:

1. **Stats** — the Step 1 counts; whether the wiki index and wiki log exist.
2. **Orphans** — page and suggested MOC; uncompiled Raw and `ENTITY-UNLINKED` separately.
3. **Broken Links** — source note → missing target (with its key for frontmatter) → likely fix; which source the frontmatter part came from.
4. **Contradictions** — page, possibly resolved by which newer Raw.
5. **Stale Pages** — page, `date_modified` (or git age, marked), why; `explored: false` backlog count.
6. **Index Issues** — per index section: missing or ambiguous targets, uncatalogued files, Stats vs recount, Recent sections; wiki log presence and latest entry vs newest ingest.
7. **MOC Coverage** — uncovered pages with a suggested MOC, back-link gaps, links to missing notes, overgrown or undescribed MOCs.
8. **Frontmatter Coverage** — one row per field or section as n/total with failing paths, including the disputed queue and Persona health.
9. **Core Context** — `snapshot_date`, age, source drift.
10. **Link Form** — `link-lint.py` findings by rule with path, line and text, all and new since the baseline; then conformance per Wiki page.
11. **Policy Conformance** — the Step 11 gaps, and drifted notes grouped by recorded provenance with each group's newest `date_created`.
12. **Frontmatter and Structure** — findings by rule with path, line and text, all and new; which path ran and the policy flags passed; fixes named for the Obsidian Linter plugin or the owner, never applied.
13. **Not checked** — steps skipped or tools unavailable, with the reason.
14. **Recommendations** — top ten by impact and effort, each naming the fix or routing to `audit`, `verify` or `refresh-context`.

Preserve every finding. A list shortened for display says `showing n of N` and where the full list is (an appendix in the same report, or a file the owner approved). Counts are observations, never combined into a score.
