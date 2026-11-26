---
name: "status"
description: "Reports a read-only vault snapshot: page counts, Inbox backlog, Core Context age, index drift, recent wiki log history, property coverage, verificationStatus and confidence breakdowns. Use for vault status or a backlog check. Knowledge quality belongs to audit, link and index checks to lint."
license: MIT
---

# Status

Show the current state of the wiki at a glance.

Status is read-only and points at the skill that would act. Run from the vault root. Read the vault guideline (live policy) for the folders that play the wiki and source roles, for the folders the wiki page kinds go into, and for the Inbox root. Open [principle-vault-roles](../principle-vault-roles/SKILL.md). Use the [records resolver](../ingest/references/records.md) with `--wiki` set to the vault-relative wiki folder from the live guideline. Only `path` rows name files to read; report `unavailable` rows with their reasons and continue independently. With no configured wiki role, report both records unavailable without resolving them. Report the roots you actually counted. Never guess a folder or register a missing mapping during this read-only check.

## Process

1. **Stats and catalog.** Read the wiki index Stats table and catalog. Report an unconfigured or out-of-role index as unavailable with the reason, and a valid path with no file as missing. Either way, the counts in step 3 still stand.
2. **Recent history.** Read the last five relevant entries from the wiki log (append-only, newest at the bottom). Report an unconfigured or out-of-role log as unavailable with the reason, and a valid path with no file as missing. Git history is not a proxy for the wiki log.
3. **Count actual files:**
   - the source role, recursively → raw sources
   - the Terms folder the vault registers → terms, plus `layer: terms` pages in the Concept folder
   - the Concept folder → concepts, excluding `layer: terms` pages
   - the registered Entity folders → entities
   - the Guide folder → guides
   - the Map folder → Maps (MOCs)
   - the Questions folder → research questions
   - the Queries folder → queries
   - the Inbox root, recursively → pending inbox items, plus how many are older than 30 days. Inbox location is the state; there is no queue field.
   A folder this vault lacks (often Questions) is reported `absent` with that reason, never as 0 and never folded into another count; a folder present but empty is 0; a count you could not take is `unknown`.
4. **Coverage check**: `rg -l '^collectionPurpose:'` across the resolved source folder → n/N (a letter to your future self). Also count purposes recorded as a delegated inference with its reason; where existing notes still carry `purpose_origin`, report its values as they are.
5. **Deep-link check**: `rg -l 'obsidian://'` across the vault, matches inside code excluded → count of notes; the target is 0.
6. **Exploration Gate check**: `explored` across Wiki pages → n/N present, plus the `explored: false` count as backlog and the explored ratio `true/N`. Denominator: Terms, Concepts, Entities, Guides; a Map without `explored` is missing nothing. Count pages with a Bias Check too.
7. **Verification check**: `verificationStatus` across Wiki pages → n/N present, and the breakdown `verified`/`partial`/`unverified`/`disputed`; values outside these four are counted as invalid, not coerced. Alongside, the `confidence` breakdown `high`/`medium`/`low`/missing. Both use the same Wiki denominator as step 6.
8. **Core Context age**: `snapshot_date` from `Core Context.md` frontmatter → date and days since. Missing date is `unknown`. Over 30 days is stale. A missing note or `status: template` means onboarding never finished.
9. **Index drift**: when the wiki index was read, report every count from step 3 that differs from its Stats table, and Recent Ingests/Queries entries naming files that no longer exist.

Status writes nothing — no index update, no wiki log entry, no repair, no reindex. Counts are presence, never quality. When the owner wants names, list the files in scope whose frontmatter lacks the field. Tools: `rg`, `find`.

## Output

```
LLM Wiki Status — <vault>  (<date>)
──────────────────────────
Raw Sources:  <n>   (collectionPurpose: <n/N> = <p>%; inferred/unknown <n>)
Wiki Pages:   <n>   (Terms <n>, Concepts <n>, Entities <n>, Guides <n>, Questions <n>|absent)
MOCs:         <n>
Queries:      <n>
Inbox:        <n> pending  (>30 days: <n>)

obsidian:// links:  <n> notes
explored:           <n/N> present · true <n/N> = <p>% · false <n>
verificationStatus: <n/N> present · verified <n> · partial <n> · unverified <n> · disputed <n> · invalid <n>
confidence:         high <n> · medium <n> · low <n> · missing <n>
Bias Check:         <n> pages

Core Context: snapshot <date> (<d> days ago) | unknown
──────────────────────────
Recent Activity (last 5 wiki log entries) | wiki log missing or unavailable
- <date> <operation> <target>
──────────────────────────
Issues (if any)
- <finding> → <skill that handles it>
Roots counted: <list>; absent: <list>
```

Route each issue: index drift → `lint`; large or old Inbox → `inbox`; collectionPurpose, deep links, explored or Bias Check gaps → `lint`; `disputed` or `unverified` pages → `verify`; Core Context > 30 days → `refresh-context`; unfinished onboarding → `onboard`; search missing known pages → `reindex`. Do not rank the vault or turn the percentages into a score.
