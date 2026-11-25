---
name: "lint"
description: "Lints a bounded vault scope for mechanical health and reports without editing: broken or orphan links, placement drift, missing frontmatter, wiki index and log sync, MOC coverage, stale pages, link form (`[label](URL)` for external, wikilinks for internal, no bare URLs or `obsidian://` note links), frontmatter keys out of alphabetical order, external URLs outside `*_url` keys, retired `youtube`/`x` keys, `status` outside lifecycle notes, Entity names left unlinked, horizontal rules and `## Wiki`/`## From Sources` auto zones in wiki pages. Use for vault lint, note health, link or frontmatter checks, even when the owner only asks what is broken or how far notes drift from the guideline. Quality review belongs to audit, per-claim checks to verify, applying fixes to the Obsidian Linter plugin."
license: MIT
---

# Lint

LLM Wiki lint / health check: inventory against the wiki index in [records](../ingest/references/records.md), orphans, broken links, contradictions, stale pages, index sync, MOC coverage, frontmatter coverage (collectionPurpose, Exploration Gate, verification fields, Bias Check, Persona health), Core Context freshness, link form, and frontmatter and structure rules (Step 12). Lint reads structure, not meaning — whether a claim is true is `verify`, whether a cluster agrees with itself is `audit`.

Lint only reports. A lint run writes nothing — no note, no wiki index edit, no wiki log entry — and applies no fix; every finding comes back as a report with who fixes it (see Fixes are not lint's).

Tools, each printing the same report lines (`RULE<TAB>path<TAB>line<TAB>text`, then `# violations=N`):

- `scripts/link-lint.py` — link form in the body, including bare URLs, which metadataCache does not track, and body links to missing notes (Step 10). With `--checks policy` it is also the Step 12 path when Obsidian is not running.
- `scripts/obsidian-lint.py` — Step 12 through the running Obsidian app, only when it already has this vault open: `obsidian eval` over `app.metadataCache` (frontmatter, headings, thematic breaks, links), `obsidian aliases` for Entity names, `obsidian unresolved` for frontmatter links to missing notes, `obsidian properties` for vault-wide counts of `status` and the retired keys.
- `scripts/marksman-lint.py` — the marksman language server: links to missing headings, ambiguous links (two notes answer one name) and duplicate headings.

Also `obsidian-cli` for backlinks, `rg` otherwise; `qmd query` for a renamed target; `git log` only as a fallback age when `date_modified` is absent. Never open or switch a vault to run a check: a script that cannot run (exit 3) goes under Not checked with its reason. Null-safe recipes are in [checks](references/checks.md).

## Scope and policy

Pin the scope: a folder, a Map cluster, named notes, or the whole vault only when asked. Read Core Context once per session (Step 9 needs it). Read the destination's live policy for placement, required properties per role and Persona boundaries, the folders of the wiki, source and work roles, and which note types are lifecycle notes (Step 12 needs both; when the policy names no roles, report Step 12 as Not checked and route to `onboard`, which asks once and records them); where live policy defines a field, value or placement, it wins. Field names follow `ingest`'s frontmatter reference.

Orphan and MOC checks use the whole vault as the link source even when the scope is one folder: a note is not orphaned just because nothing inside the folder links to it. Say which link source was used.

Run every step unless the owner named a subset; a step that could not run is listed under Not checked, not dropped.

## Process

### Step 1: Inventory

Read the wiki index for the current catalog, then count actual files: Raw notes, Wiki pages by layer and role, Queries, MOCs, Personas, Inbox candidates. Note whether the wiki index and wiki log exist. Compare index entries with actual files (detail in Step 6).

### Step 2: Orphan Check

A Wiki page with no inbound wikilink from any other note. Suggest the MOC or related page that should hold it. A Raw note linked only from its own Wiki pages is fine; a Raw no Wiki page cites is reported separately as uncompiled evidence.

Unlinked Entity mentions in wiki pages, in the body and in frontmatter values, are Step 12's `ENTITY-UNLINKED`; list them here too. The script marks a title or alias two Entities share as ambiguous; a partial name it cannot match (a first name alone) is listed as an ambiguous candidate when spotted. Report Entity reference frontmatter that ingest Step 8 would link as metadata candidates.

### Step 3: Broken Link Check

Wikilinks in body, `source`, `related` and other link fields whose target does not exist. For each, name the likely fix: a renamed target (search for it), a page that should be created, or a link to remove. A link to an Inbox candidate is not broken while the candidate exists.

Body links to missing notes are Step 10's `BROKEN`. Frontmatter links come from `obsidian-lint.py`'s `BROKEN` when it ran; otherwise check them with the PyYAML recipe in [checks](references/checks.md), and report frontmatter links as Not checked if PyYAML is unavailable. `marksman-lint.py` adds `BROKEN-HEADING` for links to a heading the target lacks and `AMBIGUOUS-LINK` for a link more than one note answers (usually two notes sharing an H1 title). Allow unresolved `author` names and Term `domain` vocabulary; report all unresolved `source` and `related` targets. Use Step 10's body results, which allow the Term template's final named Related Terms candidate with a nested relationship. Keep that target uncreated; links to the same target elsewhere are still checked.

### Step 4: Contradiction Check

List every `> [!warning] Contradiction` callout with its page. Check whether a newer Raw on the same subject has appeared since; if so, mark it possibly resolved and route to `verify`. Lint never removes a callout.

### Step 5: Staleness Check

Pages with `confidence: low` whose `date_modified` is 30 or more days old (use `git log` age only when `date_modified` is absent, and say so). Count `explored: false` pages as review backlog alongside. Staleness is a prompt to revisit, not an error.

### Step 6: Index Sync

Verify the wiki index matches the actual structure:
- every `[[...]]` in the wiki index, in every section the live index has (Raw sources, Wiki, Queries, Maps, Personas, …), resolved against actual vault files by basename or path; missing or ambiguous targets reported per section;
- files present on disk but catalogued in no section;
- each catalog section against its folder;
- the Stats table against counts recounted per catalogued section from folders, never from the old table;
- Recent Ingests / Recent Queries pointing at existing notes.

Check the wiki log: present, append-only shape (`## [YYYY-MM-DD] op | title` entries), and its latest entry date versus the newest Raw `date_ingested` — a newer ingest with no log entry is a gap. A missing wiki index or wiki log is a finding; git history does not replace either. Report the gaps for the owner to fix.

### Step 7: MOC Coverage

Every Wiki page should be reachable from at least one MOC. List uncovered pages with the MOC they most likely belong to, MOC links to notes that no longer exist, page ↔ MOC back-link gaps, and MOCs whose lists have grown past easy reading. Judge placement by hierarchy: a page is read through its parent MOC, Raw evidence and compiled knowledge are different roles, a chapter Raw is listed in its book Entity. A MOC that is a bare list without saying what its collection covers and lacks is a finding. Suggest placement from live policy; moving a note is the owner's.

### Step 8: Frontmatter Coverage

A letter to your future self — the fields that tell a later reader why a note exists — plus the Exploration Gate, verification fields, Bias Check and Persona health. Report each as n/total with the complete failing path list:

- **Raw:** `collectionPurpose` (missing → "pre-v2 raw source — consider backfill"); a secondary Raw that reports another creator's work carries `referenced` (originals and earlier captures; never evidence that the original was read).
- **Wiki:** `confidence` only `high|medium|low`; `source` and `related` present.
- **Attachment location:** embeds pointing outside the vault's attachments location.
- **Exploration Gate:** `explored` on every Wiki page — missing → "add `explored: false` on next touch"; `false` is backlog, not an error; `explored: true` without `exploredBy` or `exploredDate` → incomplete review metadata.
- **Status:** On lifecycle notes the live policy names, such as projects, tasks and drafts in progress, report missing required values and values outside the policy's allowed set (`todo|inprogress|done|stop` where applicable). Every other note, Raw included, carries no `status`; Step 12's `STATUS-NOT-LIFECYCLE` lists them. Never suggest inserting `status` outside lifecycle notes. Skip templates and owner-only folders.
- **Verification fields:** `claimType`, `evidenceScope`, `verificationStatus` on every Wiki page; missing → route through `verify` when touched; `verificationStatus` outside `verified|partial|unverified|disputed`, or `verified`/`partial` without `verifiedAt` and `verifiedBy` → finding; `verificationStatus: disputed` or `disputed: true` → high-priority `verify` queue.
- **Bias Check:** every `confidence: high` page and synthesis-heavy guide carries `> [!note] Bias Check` with both `Counter-argument:` and `Data gap:`; missing → quality-control gap.
- **Persona health:** `personaOf` resolves to an existing Entity; `personaMaturity` valid per live policy; Simulation Boundary and Accumulation Log present; Persona content does not leak into shared Entity, Term or Concept pages; the Entity's `source` holds no Raw the Persona has not absorbed (accumulation backlog). Spot-check one Quote Bank quote per Persona against the cited Raw's `## Original Content`; a mismatch is a fabrication-level finding.

### Step 9: Core Context Freshness

Read Core Context `snapshot_date`. Compare it with the latest modification of the system files it was built from. If they changed after the snapshot, or the snapshot is over 30 days old, recommend `refresh-context`.

### Step 10: Link Form

Run `scripts/link-lint.py --vault <vault> --scope <scope>` (offline, no reachability checks) and report its findings verbatim — it, not judgment, decides. The rules: external links are `[label](URL)` (`BARE-URL`, `AUTOLINK`, `EMAIL`, `FLIPPED`, `LABEL-SPACE`, `EMPTY-LINK` fail), internal links are wikilinks (`MD-INTERNAL`), no `obsidian://` link to a note (`DEEPLINK`), a folder path inside a wikilink only when the basename collides (`PATH-WIKILINK`), and body wikilinks resolve (`BROKEN`, except the planned Term link in Step 3). Code, frontmatter and HTML comments are skipped.

Report the full list and, using the previous report's output as `--baseline`, the new findings separately; without a previous report say so. `markdownlint` limited to MD011, MD034, MD039 and MD042 may run beside it; the script already covers those rules.

Then check every Wiki page against `ingest`'s conformance list and report each page with the items present and their lines.

### Step 11: Live Policy Conformance

Notes written before the current policy, or by a writer still following an older one, drift from it. Compare each note in scope with what the destination's live policy registers today, and with the saved-note format and structure `ingest` requires for its kind, live policy winning where they differ; whether its content is true belongs to `verify`. Report every gap with its path:

- **Placement:** a Raw or Wiki note in a folder the live policy's tree does not register (a retired, renumbered or recreated lane), or an Entity outside the folder the live policy registers for its recorded subtype, never inferred from the name alone. Name the registered folder for the same kind. A required-type Entity folder `ingest` created beside the registered Entity folders is reported as "unregistered, pending owner registration"; its notes are never moved.
- **Kind values:** `type`, `category`, layer or role values that differ from the value live policy assigns to that folder or kind, or are missing.
- **Retired keys and duplicates:** keys the live policy says not to use (for example removed provenance keys), and the same property written twice in different spellings (`date modified` beside `date_modified`), with both values.
- **Old values carried as tags:** where live policy keeps a replaced value as a tag (for example `reference/<old type>`), a note whose replaced value is not kept.
- **Terms:** judge each Term and Concept by `principle-note-kinds` for classification and the [Term template](../term/assets/term.md) for title rules and report Term candidates, Entity candidates and Term titles that break them, each with its target title and folder, plus links to a heading inside a Term, empty scaffold sections, tags and domain formatting outside the template contract, and missing source links or claim locators required by the template. Accept equivalent and legacy headings; route judgments about evidentiary support to `verify`. A Concept titled as a sentence-style claim is reported as a claim candidate with the Term or Concept it is about when one exists. Decide only from evidence in the note and its sources; an empty or unsourced note is reported as undecided.
- **Entities:** check each Entity against the template `principle-entity-types` selects for its type, under [entity assets](../entity/assets/). Protected owner content is not a finding. Route content gaps to `ingest` or `verify`.
- **Backticked URLs:** every backticked URL in a note body, with its line and text, as a candidate for `[name](URL)`. Skip code fences, commands, quotations, frontmatter and captured source text under a Raw note's `## Original Content`.

Then group the drifted notes by the provenance fields they record (`source_extraction`, `ingest_kind`, `store`, `source_kind`, `source_locator` host or session) and report each group with its newest `date_created`. A group still gaining notes means a writer is still producing the old shape. Name it as the recorded provenance only: never infer a producer from mtime, counts or file names. Report where that writer's instructions live when a recorded field points to them, as a finding for the owner. Lint does not edit another tool's configuration.

### Step 12: Frontmatter and Structure

Pass the live policy's wiki folder (`--wiki`, repeatable) and lifecycle `type` values (`--lifecycle`, comma-separated). If Obsidian is running with this vault already open, run `scripts/obsidian-lint.py --vault <vault> --scope <scope> --wiki <folder> --lifecycle <types>`; it exits 3 rather than open or switch a vault. Otherwise, or after exit 3, run `scripts/link-lint.py --checks policy` with the same flags. Say which path ran. Both print the same lines, `RULE<TAB>path<TAB>line<TAB>text`, and accept `--baseline`; report them verbatim.

| Rule | Notes | Finding |
| --- | --- | --- |
| `FM-INVALID` | all | frontmatter that is not valid YAML (a repeated key, a broken quoted value); Obsidian reads no properties from it, so the other frontmatter rules skip the note |
| `FM-KEY-ORDER` | all | a key sorts before the key above it, compared lowercased as the Obsidian Linter's YAML key sort does |
| `FM-URL-KEY` | wiki | a URL in any form under a key that is neither `url` (the canonical homepage) nor `*_url`; a web citation belongs in the body as `[label](URL)`. Raw notes keep the provenance keys their ingest schema defines |
| `FM-URL-FORM` | all | a `url` or `*_url` value that is not a plain URL |
| `FM-LEGACY-KEY` | all | the retired `youtube` or `x` key; its value belongs in `youtube_url` or `x_url` |
| `STATUS-NOT-LIFECYCLE` | all | `status` on a note whose `type` is not a lifecycle type |
| `DUP-HEADING` | all | a heading text the note already used |
| `ENTITY-UNLINKED` | wiki | a frontmatter value that is exactly, or the first body mention outside code, quotes, links, URLs and headings that is, the title or an alias of a `layer: entities` page the note does not wikilink; a name two Entities share is marked `ambiguous` with both |
| `HR-IN-WIKI` | wiki | a thematic break (`---`, `***`, `___`) in the body |
| `AUTO-ZONE` | wiki | a `Wiki` or `From Sources` heading, the retired append-only auto zone |

`obsidian-lint.py` also prints `BROKEN` for frontmatter links (Step 3) and a `# properties` line with vault-wide counts of `status`, `youtube` and `x`. `marksman-lint.py` reports `DUP-HEADING` too; merge identical lines. Bare URLs in the body come from Step 10. A Step 12 finding is fixed by the Obsidian Linter plugin (frontmatter) or by the owner or the writing skill (body), never by lint.

## Output

Report in the conversation using [report](references/report.md):

1. **Stats**
2. **Orphans**
3. **Broken Links**
4. **Contradictions**
5. **Stale Pages**
6. **Index Issues** — catalog, Stats, Recent sections, wiki log
7. **MOC Coverage**
8. **Frontmatter Coverage** — v2 fields, Exploration Gate, verification fields, Bias Check, Persona health
9. **Core Context**
10. **Link Form** — `link-lint.py` findings, all and new
11. **Policy Conformance** — placement, kind values, retired keys and duplicates, old values kept as tags, Term and claim candidates, backticked URLs, and writer groups still producing the old shape
12. **Frontmatter and Structure** — Step 12 findings by rule, all and new, and which path ran
13. **Not checked**
14. **Recommendations** — top ten by impact and effort, routed to `audit`, `verify` or `refresh-context` by name where larger

Keep the full finding list. When a section is shortened for display, state the total count, how many are shown, and where the complete list is (later in the report or an owner-approved file); never silently drop the remainder. Counts are observations; do not combine them into a score.

## Fixes are not lint's

Lint only reports; it never edits a note, the wiki index or the wiki log, even when asked to fix what it found. Each recommendation names who fixes it:

- **Frontmatter** (key order, URL keys, retired keys and duplicate spellings, `status` outside lifecycle notes, a property whose value is known): the owner runs the Obsidian Linter plugin, whose YAML key sort orders keys; name the Linter rule or the key to change.
- **Body and links** (bare URLs and other link form, unlinked Entity names, horizontal rules, auto-zone headings, broken links): the owner, or the skill that writes that page (`ingest` and the page-writing skills) when it next touches it. A bare URL becomes `[label](URL)` with a label from the surrounding text or the note title, never fetched; a `BROKEN` link is repaired only to a confirmed renamed target.
- **Catalog and placement** (MOC coverage, wiki index and log, unregistered folders, kind values, Term retitles and reclassifications): the owner, with the registered folder or title from live policy; route content gaps to `ingest`.
- **Claims and verification fields** (`confidence`, `verificationStatus`, Contradiction callouts, `explored`): `verify`.

Report again rather than chase a writer that still produces the old shape: it keeps doing so until its owner changes its instructions.
