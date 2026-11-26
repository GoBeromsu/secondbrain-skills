---
name: "onboard"
description: "Sets up a fresh vault through an owner interview that fills template placeholders and writes Core Context plus the wiki index and log, or gives an existing vault a read-only diagnosis and proposal. Also records, after asking once, which folders play the wiki, source and work roles when the vault guideline is silent. Use for first-time setup, resuming an interrupted setup, a zero-diff rerun, or when another skill finds the vault roles missing. Not for moving notes or Sync pairing."
---

# Onboard

Turn a starting vault into the owner's vault in about ten minutes by interviewing them and filling everything in, without requiring or creating a counterpart vault.

## Philosophy

1. **Context-first** — fill *who you are* (Core Context) before ingesting; without it every `ingest` purpose question and every `query` answer is generic.
2. **Answer-1-of-many** — ask a handful per turn; the owner answers only what is relevant. Context accumulates across turns.
3. **Agent-does-the-typing** — the owner speaks in plain words; you write frontmatter, placeholders and Core Context.
4. **Resume-safe** — rerunning detects what is done and continues from the first unfinished step; a finished vault changes nothing.

## Pre-flight

```bash
pwd
rg -l '\{(your-name|Your Name|PATH_TO_YOUR_LLM_WIKI|YYYY-MM-DD)\}' -g '*.{md,json,yml,yaml,sh}' . | wc -l
rg -m1 '^status:' "Core Context.md"
```

Completion means none of the mandatory tokens is left: `{your-name}`, `{Your Name}`, `{PATH_TO_YOUR_LLM_WIKI}`, `{YYYY-MM-DD}`.

- 0 files with mandatory tokens and `status: active`, but a vault-role or record-path mapping is missing → [Vault roles](#vault-roles) only.
- 0 files with mandatory tokens, `status: active` and all role and record-path mappings valid → already onboarded. Say so and ask whether to revisit anything (identity or axis changes belong to `refresh-context`).
- Target missing or empty → scaffold only with the owner's explicit authorization: ask the role (`personal` or `knowledge`) and the template folder and confirm the owner may use its files and plugins. Create the root and copy the template's policy files first without overwriting existing files. Run [Vault roles](#vault-roles) before copying or bootstrapping either record. Copy the remaining non-record scaffold files only where absent, including `Core Context.md` (`status: template`); do not bulk-copy template record files. Then bootstrap the records below and continue to Interview.
- Interrupted authorized scaffold with no owner notes → finish the same scaffold from its first incomplete step. Do not assume an unfamiliar nonempty folder is a scaffold.
- Freshly laid-down or cloned starting vault (placeholders present, Core Context `status: template`, no owner notes) → [Vault roles](#vault-roles), then bootstrap the records below and continue to Interview.
- Existing vault with owner notes → read-only diagnosis and proposal, apart from the one guideline entry [Vault roles](#vault-roles) records: report placeholders left, Core Context status and its §2 axes, whether the resolved wiki index and wiki log exist, whether the vault guideline names the vault roles, and the settings changes you would suggest. A root `index.md` is a legacy file in that report, not the wiki index. Otherwise write nothing: no note, JSON, config or settings change, and no placeholder replacement in existing files. A missing wiki index or wiki log is proposed, not created; `ingest` creates the wiki index on its first run, only at the resolved path.

## Vault roles

Skills never hard-code a vault path; they read from the vault guideline (its AGENTS file or the policy note it names, the live policy) which folders play each role:

- **wiki**: compiled pages (Terms, Concepts, Entities, Guides, Maps, Queries), freely written by skills;
- **source**: Raw captures, written only when the owner hands material over to ingest or save;
- **work**: the owner's own notes, including the permanent-notes folder where a person's impressions are kept.

Inside the wiki the guideline also names a folder per page kind: Terms, Concepts, Guides, Queries and each Entity type in use.

Read the live guideline for the role mappings and the vault-root `AGENTS.md` for `wiki-index` and `wiki-log`. Ask the owner once, in one batch, for missing or invalid mappings needed by onboarding or the calling skill, naming the folders that exist. Ask for record paths relative to the vault root and strictly beneath the declared wiki role. Keep valid mappings and never choose a default. Validate proposed record paths with the resolver, passing the proposed wiki folder for `--wiki` and the owner-supplied paths as `--index` and/or `--log`; do not persist invalid paths. Open [principle-editing](../principle-editing/SKILL.md). Write approved role answers into the guideline's one `Vault roles` section (append it the first time, extend it later; never a second copy) and approved record paths into the `wiki-index` and `wiki-log` lines in vault-root `AGENTS.md`. Change nothing else and read the mappings back. These configuration entries are the only writes onboard makes in an existing vault with owner notes.

**Bootstrap records (fresh targets only).** With the live vault-relative wiki folder, run `python3 "<ingest-scripts>/records.py" --vault "<vault>" --wiki "<wiki-folder>"` as described in [records](../ingest/references/records.md). For each `path` row, keep an existing destination untouched; otherwise create its parent and move the corresponding legacy root record already in this fresh scaffold, copy the corresponding template record directly to the resolved destination, or create the missing record there. If both a legacy root file and its resolved destination exist, leave the root file and report it. Report and skip each `unavailable` row; without a valid wiki role bootstrap neither record. Never create a new root `index.md` or `log.md`.

## Interview — 3 required + 2 optional (answer-1-of-many)

In voice mode one question at a time, in text a batch. After each answer, confirm it back in one or two sentences.

**Q1 — Location & name.** The vault's absolute path comes from `pwd`. Ask the name to use inside the vault (real name, handle, any script — it goes into wikilinks) → `{your-name}` / `{Your Name}`.

**Q2 — Core Context §1 identity (core).** Name, role, field, main activities, and the **continuity statement**: in one to three sentences, which earlier question today's work grew out of.

**Q3 — Core Context §2 reuse axes, 5–9 (core).** Where a source might end up, in the owner's own words; offer examples only as prompts, never a fixed list. Too few and everything piles on one, too many and they stop discriminating. These registered axes are what the owner answers, or `ingest` infers from, when a source's purpose is asked.

**Optional — §3 personal frameworks / §4 philosophy, 3–5.** Fill when given; otherwise skip (`refresh-context` can add them later).

**When stuck (failure mode): passive mode.** If answers do not come, ask for paths to existing writing (blog, essays, the owner's Me note), read them, and propose §1 and §2 for the owner to correct. Nothing in Core Context is invented.

## Fill

**F1 — Placeholder replacement.** Fresh targets only; the wiki index and wiki log carry `{your-name}` and `{YYYY-MM-DD}` too. Show the values (name, vault path, today's date in the owner's timezone). After OK, in the freshly scaffolded or starting-vault files only, replace only the literal tokens across `.md`, `.json`, `.yml`/`.yaml` and `.sh` files, `.git` excluded (`sed -i ''` on macOS): `{your-name}`, `{Your Name}`, `{PATH_TO_YOUR_LLM_WIKI}`, `{YYYY-MM-DD}`.

**F2 — Write Core Context.md.** Draft §1 identity and §2 reuse axes (plus optional §3/§4) from the interview, and §5 listing the files the owner registers as sources, or delete §5 when none. Show the draft and confirm. Then set `status: template` → `active`, `snapshot_date` to today, keep `version: "1.0"`.

**F3 — Verify replacement.** No replaced token is left in the approved files and nothing else in them changed; the pre-flight `rg -l` without `| wc -l` lists any file still holding one.

**Settings for an existing vault.** Proposal only: for `.obsidian/app.json`, `.obsidian/daily-notes.json`, and the `data.json` of the `homepage`, `templater-obsidian` and `obsidian-excalidraw-plugin` plugins, list the exact top-level keys you would change with old and new values. Never write them; the owner applies changes, or authorizes them as a separate task.

## Resume logic

Every run starts at the pre-flight. For a fresh scaffold, resolve the roles and record paths and finish authorized bootstrap writes before filling placeholders (F1) or activating Core Context (F2). An existing vault with owner notes always stays in read-only diagnosis, apart from the approved Vault roles entries.

## Wrap-up

Read back the files written and list them, with each principle that changed a decision and what it changed. Then suggest:

1. `status` — the vault at a glance.
2. A first `ingest <URL>` — when the purpose question comes, answer with one of the §2 reuse axes (a letter to your future self).
3. A first `query <question>`.
4. As it grows: recurring open questions become Research Question cards in the Questions folder the guideline names; a defended claim becomes a Synthesis card.
5. Later: `capture` for collecting before ingesting (`ingest` processes the Inbox), `qmd` for search (`ingest` refreshes it).

Do not install skills, sync, migrate notes, ingest, delete files, or commit as a side effect; the wiki index and wiki log are the vault's records and Git never replaces them. A commit happens only when the owner separately asks.

Tools: `rg`, `sed`, `cp`, `obsidian-cli`.
