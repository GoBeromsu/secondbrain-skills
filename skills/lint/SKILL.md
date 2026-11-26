---
name: "lint"
description: "Lints a bounded vault scope for mechanical health and reports without editing: broken or orphan links, placement drift, missing frontmatter, wiki index and log sync, MOC coverage, stale pages, link form, frontmatter key order, misplaced URLs, retired keys, stray `status`, unlinked Entity names, horizontal rules and auto zones in wiki pages. Also gives a counts-only status snapshot: page counts, Inbox backlog, recent wiki log entries, property coverage and Core Context age. Use for vault lint, note health, link or frontmatter checks, vault status, stats or a health overview, even when the owner only asks what is broken, how big the backlog is or how far notes drift from the guideline. Quality review belongs to audit, per-claim checks to verify, applying fixes to the Obsidian Linter plugin."
license: MIT
---

# Lint

Lint reads structure, not meaning: whether a claim is true is `verify`, whether a cluster agrees with itself is `audit`.

Lint only reports. A run writes nothing (no note, wiki index edit or wiki log entry) and applies no fix, even when the owner asks it to fix what it found; each finding names who fixes it (see [Who fixes what](#who-fixes-what)).

Scripts, each printing `RULE<TAB>path<TAB>line<TAB>text` lines and `# violations=N`, accepting `--baseline` (the previous report's output), and reported verbatim — they decide, not judgment:

- `scripts/link-lint.py` — body link form and body links to missing notes (Step 10); with `--checks policy`, frontmatter `BROKEN` (Step 3) and Step 12, plus `ORPHAN` (Step 2) with `--orphans`. Offline: it reads files, never the Obsidian app.
- `scripts/marksman-lint.py` — `BROKEN-HEADING` and `AMBIGUOUS-LINK` (two notes answer one name).

Never open or switch a vault to run a check. A script or step that cannot run goes under Not checked with its reason, never dropped. Recipes for the rest are in [checks](references/checks.md).

## Scope and policy

Pin the scope: a folder, a Map cluster, named notes, or the whole vault only when asked. Run every step unless the owner named a subset. Orphan and MOC checks use the whole vault as the link source even for a folder scope; say which link source was used.

Read the destination's live policy (root `AGENTS.md` or the guideline it names): wiki, source, work and Entity folders, roles and required properties, lifecycle and book Entity types, product Entity types, placement and Persona boundaries. Where it defines a field, value or placement it wins; field names follow `ingest`'s [frontmatter](../ingest/references/frontmatter.md). When it names no roles, report Step 12 as Not checked and route to `onboard`. Read Core Context once (Step 9).

## Process

### Step 1: Inventory

From the wiki index ([records](../ingest/references/records.md)) and the files: Raw, Wiki by layer and role, Queries, MOCs, Personas, Inbox candidates; whether the wiki index and wiki log exist.

### Step 2: Orphans

Step 12's `ORPHAN`: a Wiki page no other note wikilinks to (body or frontmatter, outside code and comments; `type: moc` pages and the wiki index and log named in the vault-root `AGENTS.md` are exempt), with the MOC or page that should hold it. A Raw no Wiki page cites is reported separately as uncompiled evidence. List Step 12's `ENTITY-UNLINKED` here too; a partial name the script cannot match (a first name alone) is an ambiguous candidate.

### Step 3: Broken links

Body links come from Step 10's `BROKEN`, frontmatter links from Step 12's `BROKEN` (on the key's line; `author` and a Term's `domain` are skipped). `marksman-lint.py` adds `BROKEN-HEADING` and `AMBIGUOUS-LINK`. Name each likely fix: a renamed target (search for it with `qmd query` or `rg`), a page to create, or a link to remove.

Not broken: a link to an existing Inbox candidate; unresolved `author` values and Term `domain` vocabulary; the Term template's final Related Terms candidate (Step 10); and a missing daily note linked by a valid calendar date when live policy declares the optional `daily-notes` role (a row such as `` | daily-notes | `Journal/` | `YYYY-MM-DD` filenames. ``), by basename or declared path. Other folders, invalid dates, embeds and links with fragments are still broken. Never create the target.

### Step 4: Contradictions

Every `> [!warning] Contradiction` callout with its page; if a newer Raw on the subject has appeared, mark it possibly resolved and route to `verify`.

### Step 5: Staleness

`confidence: low` pages whose `date_modified` is 30+ days old (`git log` age only when it is absent, marked as such), plus the `explored: false` backlog count. A prompt to revisit, not an error.

### Step 6: Index sync

Resolve every `[[...]]` in every section of the wiki index against actual files (missing or ambiguous per section), list files catalogued nowhere, compare each section with its folder, recount the Stats table from folders (never from the old table), and check Recent Ingests / Recent Queries targets. Check the wiki log: present, append-only `## [YYYY-MM-DD] op | title` entries, and its latest date against the newest Raw `date_ingested`; a newer ingest with no entry is a gap. A missing index or log is a finding; git history does not replace either.

### Step 7: MOC coverage

Wiki pages reachable from no MOC (with the likely MOC), MOC links to missing notes, page ↔ MOC back-link gaps, overgrown MOCs, and MOCs that are bare lists without saying what the collection covers and lacks. A chapter Raw is listed in its book Entity.

### Step 8: Frontmatter coverage

Each row as n/total with every failing path:

- **Raw:** `collectionPurpose` (missing → "pre-v2 raw source — consider backfill"); a secondary Raw reporting another creator's work carries `referenced`.
- **Wiki:** `confidence` in `high|medium|low`; `source` and `related` present; embeds outside the vault's attachments location.
- **Exploration Gate:** `explored` on every Wiki page (missing → "add `explored: false` on next touch"; `false` is backlog); `explored: true` without `exploredBy` or `exploredDate` is incomplete.
- **Status:** on lifecycle notes live policy names, missing values and values outside its allowed set. A book reading-progress note qualifies only in a registered Entity folder, with the book type, and a real `## Reading Progress` heading; check its values against live policy. Never suggest adding `status` elsewhere (Step 12 lists stray ones). Skip templates and owner-only folders.
- **Verification:** `claimType`, `evidenceScope`, `verificationStatus` on every Wiki page (missing → `verify` on next touch); a status outside `verified|partial|unverified|disputed`, or `verified`/`partial` without `verifiedAt` and `verifiedBy`, is a finding; `disputed` (either form) is a high-priority `verify` queue.
- **Bias Check:** every `confidence: high` or synthesis-heavy page carries `> [!note] Bias Check` with `Counter-argument:` and `Data gap:`.
- **Persona health:** `personaOf` resolves to an Entity; `personaMaturity` valid per policy; Simulation Boundary and Accumulation Log present; no Persona content in shared Entity, Term or Concept pages; no Raw in the Entity's `source` the Persona has not absorbed. Spot-check one Quote Bank quote per Persona against the cited Raw's `## Original Content`; a mismatch is a fabrication-level finding.

### Step 9: Core Context

If the system files Core Context was built from changed after its `snapshot_date`, or the snapshot is over 30 days old, recommend `refresh-context`.

### Step 10: Link form

Run `scripts/link-lint.py --vault <vault> --scope <scope>` (offline). Rules: external links are `[label](URL)` (`BARE-URL`, `AUTOLINK`, `EMAIL`, `FLIPPED`, `LABEL-SPACE`, `EMPTY-LINK`), internal links are wikilinks (`MD-INTERNAL`), no `obsidian://` note links (`DEEPLINK`), folder paths in wikilinks only for colliding basenames (`PATH-WIKILINK`), and body wikilinks resolve (`BROKEN`). Report all findings and, with a previous report as `--baseline`, the new ones separately (say when there is none). Then check every Wiki page against `ingest`'s [conformance](../ingest/references/conformance.md) list, with items present and their lines.

### Step 11: Live policy conformance

Notes written under an older policy drift from it. Compare each note with what live policy registers today and with the format `ingest` requires for its kind; report every gap with its path:

- **Placement:** a note in a folder the live tree does not register, or an Entity outside the folder registered for its recorded subtype (never inferred from the name); name the registered folder. A required-type Entity folder `ingest` created is "unregistered, pending owner registration"; its notes are never moved.
- **Kind values:** `type`, `category`, layer or role missing or differing from what policy assigns.
- **Retired keys and duplicates:** keys policy retires, and one property in two spellings (`date modified` beside `date_modified`) with both values.
- **Old values as tags:** where policy keeps a replaced value as a tag (`reference/<old type>`), notes that dropped it.
- **Terms and Concepts:** classification by [principle-knowledge-notes](../principle-knowledge-notes/SKILL.md), titles and sections by the [Term template](../term/assets/term.md): Term or Entity candidates and bad Term titles with the target title and folder, links to a heading inside a Term, empty scaffold sections, tags and `domain` outside the template, missing source links or claim locators. Accept equivalent and legacy headings. A sentence-style Concept title is a claim candidate, named with the Term or Concept it is about. Decide from the note and its sources only; an empty or unsourced note is undecided.
- **Entities:** against the [entity template](../entity/assets/) for its type (`entity` Step 1). Protected owner content is not a finding; route content gaps to `ingest` or `verify`.
- **Backticked URLs:** each with line and text as a `[name](URL)` candidate, skipping code, commands, quotations, frontmatter and a Raw's `## Original Content`.

Group drifted notes by recorded provenance (`source_extraction`, `ingest_kind`, `store`, `source_kind`, `source_locator` host or session) with each group's newest `date_created`; a group still growing means a writer still produces the old shape. Name only the recorded provenance — never infer a producer from mtime, counts or names — and where its instructions live, as a finding for the owner.

### Step 12: Frontmatter and structure

Pass live policy as flags: `--wiki` per wiki folder, `--entity-folder` per registered Entity folder (vault-relative), `--book-type` per book Entity type, `--product-type` per product Entity type, and other lifecycle types as `--lifecycle a,b`. Omit flags the policy does not declare; never put book types in `--lifecycle`, which would exempt books without reading progress. Run `link-lint.py --vault <vault> --scope <scope> --checks policy --orphans` with them; `--orphans` reads the whole vault as link source.

| Rule | Notes | Finding |
| --- | --- | --- |
| `FM-INVALID` | all | frontmatter that is not valid YAML; other frontmatter rules skip the note |
| `FM-KEY-ORDER` | all | a key sorting before the one above it, lowercased, as the Obsidian Linter's YAML key sort does |
| `FM-URL-KEY` | wiki | a URL under a key other than `url` or `*_url` (Raw provenance keys are exempt) |
| `FM-URL-FORM` | all | a `url` or `*_url` value that is not a plain URL |
| `FM-PRODUCT-URL` | wiki/entity | a bare `url` on a product Entity (registered folder or `layer: entities`), starting with `github_url` or `website_url` |
| `FM-LEGACY-KEY` | all | the retired `youtube` or `x` key |
| `STATUS-NOT-LIFECYCLE` | all | `status` outside lifecycle types and reading-progress books (Step 8) |
| `DUP-HEADING` | all | a heading text the note already used |
| `ENTITY-UNLINKED` | wiki | a frontmatter value or first body mention (outside code, quotes, links, URLs and headings) matching an Entity title or alias the note does not wikilink; a shared name is `ambiguous` |
| `HR-IN-WIKI` | wiki | a thematic break in the body |
| `AUTO-ZONE` | wiki | a `Wiki` or `From Sources` heading, the retired auto zone |

The same run prints `ORPHAN` (Step 2) and frontmatter `BROKEN` (Step 3).

## Status mode

When the owner asks for status, stats or an overview rather than problems, report counts only, no findings: Step 1 (each folder as a count, `absent` when the vault lacks it, `unknown` when it could not be counted, never folded into another), the Step 6 Stats-table drift, the Step 8 coverage rows as n/N with the `confidence` and `verificationStatus` breakdowns (values outside the four counted as invalid), the `obsidian://` note count, how many notes carry `status`, `youtube` and `x` (recipe in [checks](references/checks.md)), and Step 9's `snapshot_date` with its age in days. Add the last five wiki log entries (newest at the bottom; git history is no proxy) and how many Inbox items are older than 30 days. Name the roots counted, route each gap in one line (as in [Who fixes what](#who-fixes-what), large or old Inbox to `ingest`, unfinished onboarding to `onboard`), and never combine counts into a score.

## Output

Report in the conversation using [report](references/report.md).

## Who fixes what

- **Frontmatter** (key order, URL keys, retired keys and duplicate spellings, stray `status`, a known value): the owner, through the Obsidian Linter plugin; name the Linter rule or the key to change.
- **Body and links** (link form, unlinked Entity names, horizontal rules, auto-zone headings, broken links): the owner, or the skill that writes that page (`ingest` and the page-writing skills) when it next touches it. A bare URL becomes `[label](URL)` with a label from the surrounding text or note title, never fetched; a `BROKEN` link is repaired only to a confirmed renamed target.
- **Catalog and placement** (MOCs, wiki index and log, unregistered folders, kind values, Term retitles and reclassifications): the owner, with the registered folder or title from live policy; content gaps to `ingest`.
- **Claims and verification fields** (`confidence`, `verificationStatus`, Contradiction callouts, `explored`): `verify`.

A writer still producing the old shape keeps doing so until its owner changes its instructions: report it again rather than chase it, and never edit another tool's configuration.
