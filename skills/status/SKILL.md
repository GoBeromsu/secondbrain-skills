---
name: "status"
description: "Reports read-only vault counts, index drift, recent log.md history, property coverage, verificationStatus and confidence breakdowns, Inbox backlog, and Core Context age. Use for a management snapshot or backlog check. Not for judging purpose fulfillment, knowledge quality, search freshness, process health, or making any vault change."
license: MIT
---

# Status

Show the current state of the wiki at a glance.

Status is read-only and points at the skill that would act. Run from the vault root, use the folder names the vault's AGENTS file declares (the ones below are the usual defaults), and report the roots you actually counted; a missing folder is reported missing, not zero.

## Process

1. **Stats and catalog.** Read the `index.md` Stats table and catalog. Missing `index.md` is reported as missing; the counts in step 3 still stand.
2. **Recent history.** Read the last five relevant entries from `log.md` (append-only, newest at the bottom). Git history is not a proxy for `log.md`; a missing `log.md` is reported as missing, not filled from commits.
3. **Count actual files:**
   - `10. Raw Sources/**/*.md` → raw sources
   - the Terms folder the vault registers → terms, plus `layer: terms` pages in the Concept folder
   - `20. Wiki/21. Concepts/*.md` → concepts, excluding `layer: terms` pages
   - `20. Wiki/22. Entities/*.md` → entities
   - `20. Wiki/23. Guides/*.md` → guides
   - `20. Wiki/24. Maps/*.md` → Maps (MOCs)
   - `20. Wiki/25. Questions/*.md` → research questions
   - `30. Queries/*.md` → queries
   - `40. Paper Analyses/*/` → paper hubs (one citekey folder each), and `40. Paper Analyses/**/*.md` → paper files; report both
   - `00. Inbox/**/*.md` → pending inbox items, all subfolders, plus how many are older than 30 days. Inbox location is the state; there is no queue field.
   A folder this vault lacks (often Questions or Paper Analyses) is reported `absent` with that reason, never as 0 and never folded into another count; a folder present but empty is 0; a count you could not take is `unknown`.
4. **Coverage check**: `rg -l '^collectionPurpose:'` across `10. Raw Sources` → n/N (미래의 나에게 보내는 편지). Also count purposes recorded as a delegated inference with its reason; where existing notes still carry `purpose_origin`, report its values as they are.
5. **Cross-vault check**: `rg -l '^mainVaultRelated:'` across `20. Wiki` → n/N. Without a mothership registered in Core Context, report "not applicable", not 0%.
6. **Exploration Gate check**: `explored` across Wiki pages → n/N present, plus the `explored: false` count as backlog and the explored ratio `true/N`. Denominator: Terms, Concepts, Entities, Guides; a Map without `explored` is missing nothing. Count pages with a Bias Check too.
7. **Verification check**: `verificationStatus` across Wiki pages → n/N present, and the breakdown `verified`/`partial`/`unverified`/`disputed`; values outside these four are counted as invalid, not coerced. Alongside, the `confidence` breakdown `high`/`medium`/`low`/missing. Both use the same Wiki denominator as step 6.
8. **Core Context age**: `snapshot_date` from `Core Context.md` frontmatter → date and days since. Missing date is `unknown`. Over 30 days is stale. A missing note or `status: template` means onboarding never finished.
9. **Index drift**: report every count from step 3 that differs from the `index.md` Stats table, and Recent Ingests/Queries entries naming files that no longer exist.

Status writes nothing — no index update, no `log.md` entry, no repair, no reindex. Counts are presence, never quality. When the owner wants names, list the files in scope whose frontmatter lacks the field. Tools: `rg`, `find`.

## Output

```
LLM Wiki Status — <vault>  (<date>)
──────────────────────────
Raw Sources:  <n>   (collectionPurpose: <n/N> = <p>%; inferred/unknown <n>)
Wiki Pages:   <n>   (Terms <n>, Concepts <n>, Entities <n>, Guides <n>, Questions <n>|absent)
MOCs:         <n>
Queries:      <n>
Papers:       <hubs> hubs · <files> files | absent
Inbox:        <n> pending  (>30 days: <n>)

mainVaultRelated:   <n/N> = <p>%  | not applicable
explored:           <n/N> present · true <n/N> = <p>% · false <n>
verificationStatus: <n/N> present · verified <n> · partial <n> · unverified <n> · disputed <n> · invalid <n>
confidence:         high <n> · medium <n> · low <n> · missing <n>
Bias Check:         <n> pages

Core Context: snapshot <date> (<d> days ago) | unknown
──────────────────────────
Recent Activity (last 5 log.md entries) | log.md missing
- <date> <operation> <target>
──────────────────────────
Issues (if any)
- <finding> → <skill that handles it>
Roots counted: <list>; absent: <list>
```

Route each issue: index drift → `lint`; large or old Inbox → `inbox`; collectionPurpose, mainVaultRelated, explored or Bias Check gaps → `lint`; `disputed` or `unverified` pages → `verify`; Core Context > 30 days → `refresh-context`; unfinished onboarding → `onboard`; search missing known pages → `reindex`. Do not rank the vault or turn the percentages into a score.
