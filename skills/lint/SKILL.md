---
name: "lint"
description: "Lints a bounded vault scope for mechanical health: broken or orphan links, placement drift, missing frontmatter, index.md and log.md sync, MOC coverage, stale pages and cross-vault links. Use for vault lint, note health or link checks. Quality review belongs to audit, per-claim checks to verify."
license: MIT
---

# Lint

LLM Wiki lint / health check: inventory against `index.md`, orphans, broken links, contradictions, stale pages, index sync, MOC coverage, frontmatter coverage (collectionPurpose, Exploration Gate, verification fields, Bias Check, Persona health), Core Context freshness and cross-vault link integrity. Lint reads structure, not meaning — whether a claim is true is `verify`, whether a cluster agrees with itself is `audit`.

Lint is report-first. A lint run writes nothing — no note, no `index.md` edit, no `log.md` entry. Every finding comes back as a report, and the owner picks which fixes to apply.

Tools: `obsidian-cli` for unresolved links and backlinks when Obsidian is running, `rg` otherwise; `qmd query` for a renamed target; `git log` only as a fallback age when `date_modified` is absent. Null-safe recipes are in [checks](references/checks.md).

## Scope and policy

Pin the scope: a folder, a Map cluster, named notes, or the whole vault only when asked. Read Core Context once per session (Step 9 needs it). Read the destination's live policy for placement, required properties per role and Persona boundaries; where live policy defines a field, value or placement, it wins. Field names follow `ingest`'s frontmatter reference.

Orphan and MOC checks use the whole vault as the link source even when the scope is one folder: a note is not orphaned just because nothing inside the folder links to it. Say which link source was used.

Run every step unless the owner named a subset; a step that could not run is listed under Not checked, not dropped.

## Process

### Step 1: Inventory

Read `index.md` for the current catalog, then count actual files: Raw notes, Wiki pages by layer and role, Queries, MOCs, Personas, Paper hubs, Inbox candidates. Note whether `index.md` and `log.md` exist. Compare index entries with actual files (detail in Step 6).

### Step 2: Orphan Check

A Wiki page with no inbound wikilink from any other note. Suggest the MOC or related page that should hold it. A Raw note linked only from its own Wiki pages is fine; a Raw no Wiki page cites is reported separately as uncompiled evidence.

Report plain-text mentions of an Entity's title or alias in Wiki pages in scope as unlinked mention candidates (page, line, text), skipping quotes, code, URLs, frontmatter, existing links, the Entity's own page and pages already linking it; mark shared or partial names ambiguous. Report Entity reference frontmatter that ingest Step 8 would link as metadata candidates.

### Step 3: Broken Link Check

Wikilinks in body, `source`, `related` and other link fields whose target does not exist. For each, name the likely fix: a renamed target (search for it), a page that should be created, or a link to remove. A link to an Inbox candidate is not broken while the candidate exists.

Exempt only intentional author wikilinks, decided by frontmatter key, not by quoting shape: values under `author` (scalar or list) may stay unresolved and are not reported as broken; never suggest creating an Entity or author note to resolve it. Quoted wikilinks under every other key (`source`, `related`, `bookIndex`, `chapterPrev`/`chapterNext`, `paperHub`, `personaOf`, …) and all body links are still checked. Parse frontmatter with the PyYAML recipe in [checks](references/checks.md); if PyYAML is unavailable, report Broken Links as Not checked rather than approximating with a regex.

### Step 4: Contradiction Check

List every `> [!warning] Contradiction` callout with its page. Check whether a newer Raw on the same subject has appeared since; if so, mark it possibly resolved and route to `verify`. Lint never removes a callout.

### Step 5: Staleness Check

Pages with `confidence: low` whose `date_modified` is 30 or more days old (use `git log` age only when `date_modified` is absent, and say so). Count `explored: false` pages as review backlog alongside. Staleness is a prompt to revisit, not an error.

### Step 6: Index Sync

Verify `index.md` matches the actual structure:
- every `[[...]]` in `index.md`, in every section the live index has (Raw sources, Wiki, Queries, Maps, Personas, Paper hubs, …), resolved against actual vault files by basename or path; missing or ambiguous targets reported per section;
- files present on disk but catalogued in no section;
- each catalog section against its folder;
- the Stats table against counts recounted per catalogued section from folders, never from the old table;
- Recent Ingests / Recent Queries pointing at existing notes.

Check `log.md`: present, append-only shape (`## [YYYY-MM-DD] op | title` entries), and its latest entry date versus the newest Raw `date_ingested` — a newer ingest with no log entry is a gap. A missing `index.md` or `log.md` is a finding; git history does not replace either. Report the gaps; fixing them is an owner-picked fix.

### Step 7: MOC Coverage

Every Wiki page should be reachable from at least one MOC. List uncovered pages with the MOC they most likely belong to, MOC links to notes that no longer exist, page ↔ MOC back-link gaps, and MOCs whose lists have grown past easy reading. Judge placement by hierarchy: a page is read through its parent MOC, Raw evidence and compiled knowledge are different roles, a chapter belongs under its Book Index. A MOC or Paper hub that is a bare list without saying what its collection covers and lacks is a finding. Suggest placement from live policy; moves happen only as a policy conformance fix.

### Step 8: Frontmatter Coverage

미래의 나에게 보내는 편지 — the fields that tell a later reader why a note exists — plus the Exploration Gate, verification fields, Bias Check and Persona health. Report each as n/total with the complete failing path list:

- **Raw:** `collectionPurpose` (missing → "pre-v2 raw source — consider backfill"), `mainVaultRelated`, `mainVaultCmds`; a secondary Raw that reports another creator's work carries `referenced` (originals and earlier captures; never evidence that the original was read).
- **Wiki:** `mainVaultRelated`, `mainVaultCmds` where live policy expects them; `confidence` only `high|medium|low`; `source` and `related` present.
- **Attachment location:** embeds pointing outside the vault's attachments location.
- **Exploration Gate:** `explored` on every Wiki page — missing → "add `explored: false` on next touch"; `false` is backlog, not an error; `explored: true` without `exploredBy` or `exploredDate` → incomplete review metadata.
- **Verification fields:** `claimType`, `evidenceScope`, `verificationStatus` on every Wiki page; missing → route through `verify` when touched; `verificationStatus` outside `verified|partial|unverified|disputed`, or `verified`/`partial` without `verifiedAt` and `verifiedBy` → finding; `verificationStatus: disputed` or `disputed: true` → high-priority `verify` queue.
- **Bias Check:** every `confidence: high` page and synthesis-heavy guide carries `> [!note] Bias Check` with both `Counter-argument:` and `Data gap:`; missing → quality-control gap.
- **Persona health:** `personaOf` resolves to an existing Entity; `personaMaturity` valid per live policy; Simulation Boundary and Accumulation Log present; Persona content does not leak into shared Entity, Term or Concept pages; the Entity's `source` holds no Raw the Persona has not absorbed (accumulation backlog). Spot-check one Quote Bank quote per Persona against the cited Raw's `## Original Content`; a mismatch is a fabrication-level finding.

### Step 9: Core Context Freshness

Read Core Context `snapshot_date`. Compare it with the latest modification of the mothership system files it was built from. If they changed after the snapshot, or the snapshot is over 30 days old, recommend `refresh-context`.

### Step 10: Cross-Vault Link Check (mothership only)

Skipped when no mothership is configured. Ignore links inside code spans and fenced blocks — those are examples.

- **Writing conformance:** check every Wiki page against `ingest`'s conformance list and report each page with the items present and their lines.

- **`mainVaultRelated`:** each entry must be `[label](obsidian://open?vault=<vault>&file=<path>)` with both components encoded by `urllib.parse.quote(value, safe='')`. Flag a wrong vault name, unencoded or double-encoded components. Decode `file` and stat it under the mothership root, with and without `.md`. Report source note → missing target.
- **`mainVaultCmds`:** each value must exactly match a reference the Core Context or mothership actually registers (compare after stripping a pipe alias). Flag unregistered, invented or reformatted values; never suggest a guessed code.

For each broken one, `qmd query` the mothership read-only for a renamed equivalent and offer one to three candidates. The mothership is never written.

### Step 11: Live Policy Conformance

Notes written before the current policy, or by a writer still following an older one, drift from it. Compare each note in scope with what the destination's live policy registers today, and with the saved-note format and structure `ingest` requires for its kind, live policy winning where they differ; whether its content is true belongs to `verify`. Report every gap with its path:

- **Placement:** a Raw or Wiki note in a folder the live policy's tree does not register (a retired, renumbered or recreated lane), or an Entity outside the folder the live policy registers for its recorded subtype, never inferred from the name alone. Name the registered folder for the same kind.
- **Kind values:** `type`, `category`, layer or role values that differ from the value live policy assigns to that folder or kind, or are missing.
- **Retired keys and duplicates:** keys the live policy says not to use (for example removed provenance keys), and the same property written twice in different spellings (`date modified` beside `date_modified`), with both values.
- **Old values carried as tags:** where live policy keeps a replaced value as a tag (for example `reference/<old type>`), a note whose replaced value is not kept.
- **Terms:** judge each Term and Concept by `ingest`'s Term rules and report Term candidates, Entity candidates and Term titles that break them, each with its target title and folder, plus links to a heading inside a Term and missing Term sections. A Concept titled as a sentence-style claim is reported as a claim candidate with the Term or Concept it is about when one exists. Decide only from evidence in the note and its sources; an empty or unsourced note is reported as undecided.

Then group the drifted notes by the provenance fields they record (`source_extraction`, `ingest_kind`, `store`, `source_kind`, `source_locator` host or session) and report each group with its newest `date_created`. A group still gaining notes means a writer is still producing the old shape. Name it as the recorded provenance only: never infer a producer from mtime, counts or file names. Report where that writer's instructions live when a recorded field points to them, as a finding for the owner. Lint does not edit another tool's configuration.

## Output

Report in the conversation using [report](references/report.md):

1. **Stats**
2. **Orphans**
3. **Broken Links**
4. **Contradictions**
5. **Stale Pages**
6. **Index Issues** — catalog, Stats, Recent sections, log.md
7. **MOC Coverage**
8. **Frontmatter Coverage** — v2 fields, Exploration Gate, verification fields, Bias Check, Persona health
9. **Core Context**
10. **Cross-Vault Integrity** (mothership only)
11. **Policy Conformance** — placement, kind values, retired keys and duplicates, old values kept as tags, Term and claim candidates, and writer groups still producing the old shape
12. **Not checked**
13. **Recommendations** — top ten by impact and effort, routed to `audit`, `verify` or `refresh-context` by name where larger

Keep the full finding list. When a section is shortened for display, state the total count, how many are shown, and where the complete list is (later in the report or an owner-approved file); never silently drop the remainder. Counts are observations; do not combine them into a score.

## Fixes, on request only

Apply only the fixes the owner picks — add a page to a MOC, add an `index.md` catalog entry or recount Stats from folders, add a missing property whose value is known, repair a link to a confirmed renamed target, or a policy conformance fix from Step 11. Show the diff and get OK per batch of at most ten changes; read each changed note back. Existing notes keep all unrelated keys, values and formatting. After applied fixes, append one `log.md` entry (`## [YYYY-MM-DD] lint | <summary>`). Do not commit unless the owner separately asks.

**Policy conformance fixes** change only what the live policy states, with the owner's pick per group:

- set `type`, `category`, layer or role to the live-policy value, keeping the replaced value where live policy says it is kept (for example the `reference/<old type>` tag, added only when absent and in the note's existing list style);
- move a note from an unregistered folder to the registered folder for its kind without overwriting: stop on a name collision or an existing note for the same source, never merge, then update every link to the old path, as in a confirmed rename;
- drop a duplicate spelling of a property only when both copies are in the note and live policy names the spelling that stays; record the dropped value in the fix report;
- drop a retired key only when live policy says to remove it from existing notes, not only from new ones;
- retitle a Term in place: rename it to the reported title and add the old title to `aliases`, keeping its folder and `layer`;
- reclassify a Term or Entity candidate: set `layer`, move it to the folder the live policy registers for that kind and retitle it as above; stop when the live policy registers no folder for the kind.

For both, stop on a title collision or on an existing note for the same referent, and never merge. Then change only these body parts: the H1, an incorrect or former form named in `## Origin`, and every link to the old title or path in this vault, keeping display text and anchors. Report inbound references from other vaults and from Raw `## Original Content` as unrepaired, with paths, and never rewrite them.

Approving a group approves its batches; show each batch's diff before applying it and read it back before the next. Missing Term sections are filled by `ingest`, not by lint: by reprocessing the Term's existing Raws, or, when it cites only external sources, by ingesting a cited source the owner selects as a new Raw first; with neither, the sections stay missing and are reported.

Before each batch, keep a copy of every note it changes outside the vault and check that the note still matches what the report read; if it changed, re-read it and re-show the diff. Bodies stay byte-for-byte unchanged, including Raw `## Original Content`, apart from the body parts a Term or Entity reclassification names. A writer still producing the old shape keeps producing it until its owner changes its instructions, so report it again rather than re-running the fix in a loop.

**Cross-vault fix mode** requires explicit opt-in for that run. It patches only `mainVaultRelated` / `mainVaultCmds` in this vault's Raw and Wiki notes, using a stat-verified target or an exactly registered reference; it never writes mothership originals. Show the diff and ask OK per batch of at most ten.

Never as a lint fix: delete a note, rename a note's file name or move a note other than by a policy conformance fix, remove a Contradiction callout, set `explored: true`, change `confidence` or `verificationStatus` (those belong to `verify`), invent a `collectionPurpose`, `mainVaultCmds` or other unknown value, create an author note, or migrate metadata not explicitly authorized.
