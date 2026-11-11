---
name: "onboard"
description: "Initializes a fresh personal or knowledge vault through a short owner interview that fills template placeholders and writes Core Context, index.md and log.md, gives an existing vault a read-only diagnosis and proposal, and resumes an interrupted setup by detecting what is already done. Use for fresh vault setup, existing-vault onboarding diagnosis, or a zero-diff rerun. Not for moving existing notes, installing skills, Sync pairing, source ingestion, or editing vault policy."
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
# Mode A mandatory tokens
rg -l '\{(your-name|Your Name|PATH_TO_YOUR_LLM_WIKI|YYYY-MM-DD)\}' -g '*.{md,json,yml,yaml,sh}' . | wc -l
# Mode B mothership tokens (mandatory only in Mode B)
rg -l '\{(PATH_TO_YOUR_MOTHERSHIP_VAULT|PATH_TO_YOUR_MOTHERSHIP|your-mothership-vault-name)\}' -g '*.{md,json,yml,yaml,sh}' . | wc -l
rg -m1 '^status:' "Core Context.md"
```

Completion is judged per mode. Mode A mandatory: `{your-name}`, `{Your Name}`, `{PATH_TO_YOUR_LLM_WIKI}`, `{YYYY-MM-DD}`. Mode B adds `{PATH_TO_YOUR_MOTHERSHIP_VAULT}`, `{PATH_TO_YOUR_MOTHERSHIP}`, `{your-mothership-vault-name}`. The mode is Mode B only when the owner chose it (Q2) or Core Context registers a concrete mothership: a real path that exists and a vault name, no `{…}` token. A §5 heading alone proves nothing, because the template ships one; without either signal the mode is Mode A, and when the owner's choice is not recorded say the mode was inferred. A Mode A vault with only mothership tokens left is complete; any Mode A mandatory token left is incomplete in either mode.

- 0 files with the mode's mandatory tokens and `status: active` → already onboarded. Say so and ask whether to revisit anything (identity or axis changes belong to `refresh-context`).
- Target missing or empty → scaffold only with the owner's explicit authorization: ask the role (`personal` or `knowledge`) and the template folder, confirm the owner may use its files and plugins, then copy only files the target lacks (`cp -R -n "$TEMPLATE/." "$VAULT"`), leaving any file already there byte-for-byte. The scaffold includes `Core Context.md` (`status: template`), `index.md` (catalog sections and Stats) and append-only `log.md`; create any of the three still missing from the template's shape. Then → Interview.
- Freshly laid-down or cloned starting vault (placeholders present, Core Context `status: template`, no owner notes) → Interview.
- Existing vault with owner notes → read-only diagnosis and proposal: report placeholders left, Core Context status and its §2 axes, whether `index.md` and `log.md` exist, and the settings changes you would suggest. Write nothing: no note, JSON, config or settings change, and no placeholder replacement in existing files. A missing `index.md` or `log.md` is proposed, not created; `ingest` creates `index.md` on its first run.

## Interview — 필수 5 + 옵션 2 (answer-1-of-many)

In voice mode one question at a time, in text a batch. After each answer, confirm it back in one or two sentences.

**Q1 — Location & name.** The vault's absolute path comes from `pwd`. Ask the name to use inside the vault (real name, handle, any script — it goes into wikilinks) → `{your-name}` / `{Your Name}`.

**Q2 — Operating mode.**
- **Mode A (standalone)**: this vault only; mothership placeholders are ignored.
- **Mode B (mothership)**: an existing main vault is the mothership and this one a satellite. The mothership is read-only from here, always.

**Q3 — (Mode B only) Mothership path & name.** Its absolute path, checked to exist, and its registered Obsidian vault name — the folder name used in `obsidian://open?vault=`, not the path. Confirm the registration with `obsidian-cli`.

**Q4 — Core Context §1 identity (core).** Name, role, field, main activities, and the **continuity statement**: in one to three sentences, which earlier question today's work grew out of.

**Q5 — Core Context §2 reuse axes, 5–9 (core).** Where a source might end up, in the owner's own words; offer examples only as prompts, never a fixed list. Too few and everything piles on one, too many and they stop discriminating. These registered axes are what the owner answers, or `ingest` infers from, when a source's purpose is asked.

**Optional — §3 personal frameworks / §4 philosophy, 3–5.** Fill when given; otherwise skip (`refresh-context` can add them later).

**When stuck (failure mode): passive mode.** If answers do not come, ask for paths to existing writing (blog, essays, the mothership's Me note), read them, and propose §1 and §2 for the owner to correct. Nothing in Core Context is invented.

## Fill

**F1 — Placeholder replacement.** Fresh targets only; `index.md` and `log.md` carry `{your-name}` and `{YYYY-MM-DD}` too. Show the values (name, vault path, today's date in the owner's timezone, and in Mode B mothership path and name). After OK, in the freshly scaffolded or starting-vault files only, replace only the literal tokens across `.md`, `.json`, `.yml`/`.yaml` and `.sh` files, `.git` excluded (`sed -i ''` on macOS): `{your-name}`, `{Your Name}`, `{PATH_TO_YOUR_LLM_WIKI}`, `{YYYY-MM-DD}`; in Mode B also `{PATH_TO_YOUR_MOTHERSHIP_VAULT}`, `{PATH_TO_YOUR_MOTHERSHIP}`, `{your-mothership-vault-name}`.

**F2 — Write Core Context.md.** Draft §1 identity and §2 reuse axes (plus optional §3/§4) from the interview, and §5 listing the mothership's system files in Mode B; in Mode A delete §5. Show the draft and confirm. Then set `status: template` → `active`, `snapshot_date` to today, keep `version: "1.0"`.

**F3 — Verify replacement.** No replaced token is left in the approved files and nothing else in them changed; the pre-flight `rg -l` without `| wc -l` lists any file still holding one. In Mode A the unused mothership placeholders may remain harmlessly.

**Settings for an existing vault.** Proposal only: for `.obsidian/app.json`, `.obsidian/daily-notes.json`, and the `data.json` of the `homepage`, `templater-obsidian` and `obsidian-excalidraw-plugin` plugins, list the exact top-level keys you would change with old and new values. Never write them; the owner applies changes, or authorizes them as a separate task.

## Resume logic

Every run starts at the pre-flight and continues at the first unfinished step: the mode's mandatory placeholders remain → F1; Core Context still `status: template` → F2; both done → already onboarded. An existing vault with owner notes always stays in read-only diagnosis.

## Wrap-up

Read back the files written and list them. Then suggest:

1. `status` — the vault at a glance.
2. A first `ingest <URL>` — when the purpose question comes, answer with one of the §2 reuse axes ("미래의 나에게 보내는 편지", a letter to your future self).
3. A first `query <question>`.
4. As it grows: recurring open questions become Research Question cards in `20. Wiki/25. Questions/`; a defended claim becomes a Synthesis card.
5. Later: `capture` and `inbox` for collecting before ingesting, `qmd` for search (`reindex`).

Do not install skills, sync, migrate notes, ingest, delete files, or commit as a side effect; `log.md` and `index.md` are the vault's records and Git never replaces them. A commit happens only when the owner separately asks.

Tools: `rg`, `sed`, `cp`, `obsidian-cli`.
