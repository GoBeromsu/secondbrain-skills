# Lint report shape

Open with the scope and the link source used (which notes counted as inbound link sources), then:

1. **Stats** — Raw, Wiki by layer and role, Queries, MOCs, Personas, Inbox candidates; whether `index.md` and `log.md` exist.
2. **Orphans** — page and suggested MOC; uncompiled Raw separately.
3. **Broken Links** — source note → missing target → likely fix (rename, create, remove). Only values under the `author` key are excluded and not counted; links under other keys are reported with their key. If PyYAML is unavailable, the section reads Not checked.
4. **Contradictions** — page, possibly resolved by which newer Raw.
5. **Stale Pages** — page, `date_modified` (or git age, marked), why flagged; `explored: false` backlog count.
6. **Index Issues** — per index section (Raw sources, Wiki, Queries, Maps, Personas, Paper hubs, any live section): links with missing or ambiguous targets, files catalogued nowhere, Stats table vs counts recounted per catalogued section, Recent Ingests / Recent Queries targets, `log.md` presence and latest entry vs newest ingest.
7. **MOC Coverage** — uncovered pages with a suggested MOC; page ↔ MOC back-link gaps; MOC links to missing notes; overgrown MOCs; MOCs or hubs that do not describe their collection.
8. **Frontmatter Coverage** — one row per field or section as n/total with failing paths: v2 fields, Exploration Gate, verification fields and the disputed queue, Bias Check, Persona health.
9. **Core Context** — `snapshot_date`, age, mothership drift.
10. **Cross-Vault Integrity** — `mainVaultRelated` vault mismatch, encoding errors and missing targets with up to three candidates each; `mainVaultCmds` values not registered. Omitted when no mothership is configured.
11. **Policy Conformance** — notes in unregistered folders with the registered folder for their kind; `type`/`category`/layer/role values that differ from live policy; retired keys and duplicate property spellings with both values; replaced values not kept where live policy keeps them; bare and backticked URLs with page, line and text as `[name](URL)` candidates; drifted notes grouped by recorded provenance with each group's newest `date_created`.
12. **Not checked** — steps skipped or tools unavailable, with the reason.
13. **Recommendations** — top ten by impact and effort, each naming the fix or the skill to route to.

Preserve every finding. If a list is shortened for display, write `showing n of N` and say where the full list is (an appendix at the end of the same report, or a file the owner approved); never drop the remainder silently.

Counts are observations. Do not combine them into a score. The report is read-only output: producing it writes no note and no `log.md` entry.
