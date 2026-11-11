---
name: "inbox"
description: "Scans, previews and counts recursive Inbox candidates, routes an explicitly selected scope and purpose mode through ingest, and deletes processed originals only on an explicit yes after verbatim preservation passed. Use for review my Inbox, preview these candidates, process this selection, or inspect duplicate sources. Not for capture, automatic RSS compilation, knowledge synthesis, or deleting unprocessed files."
license: MIT
---

# Inbox

Scan `00. Inbox/` for pending candidates, preview them, and route the selected ones through `ingest`. Read Core Context once per session; its §2 reuse axes are the ones offered for purpose. Scanning, previewing and counting write nothing. Ingest owns Raw, Wiki, Maps, `index.md` and `log.md`. The only file action this skill performs itself is the Step 6 cleanup, and only after an explicit yes.

Tools: `obsidian-cli` or plain file reads over the vault; `rg` over frontmatter for counts and locators; `qmd` when a locator is missing and you need a likely existing Raw.

## Input

- Blank or `all`: scan every lane.
- A lane or folder name (e.g. `articles`, `papers`): scan only that lane.
- `count` or `status`: show counts without detail, then stop.
- Named notes: preview those.

## Inbox Structure

Read the destination's actual `00. Inbox/` and the lanes it has; never assume a layout. The usual lanes are Articles, Papers, Transcripts, Clippings and AI Research plus the root; a vault may add `{NN Agent}` session lanes (e.g. `01 Chat`, `04 GJC`) or dated subfolders, which are scanned like any lane.

A note in a lane has its kind assigned by where it sits. A note at the Inbox root is uncategorized: say so rather than guessing a lane; `ingest` settles its placement. A note still in the Inbox is pending. A `capture` note (`type: inbox`, `capture_status`, `captureMode`, dated filename) is a normal candidate; read those keys, never rewrite them.

## Process

### Step 1: Scan

Walk the Inbox recursively; skip non-notes such as `.gitkeep`. If empty everywhere, report "Inbox is empty. Nothing to ingest." and stop. A note that cannot be read, or whose frontmatter does not parse, is reported as a problem, not counted as a candidate.

### Step 2: Preview

For each candidate, read the frontmatter and the start of the body (about the first 100 lines of a long note) and settle:

- **source** — title, `source_url`/`source` or `source_locator`, platform, author when stated, `date_clipped`;
- **kind** — from the lane or the Web Clipper `category`; for a root note, suggest one and mark it as a suggestion;
- **fidelity** — `captureMode` and `capture_status` when present (`transcript`, `curated-excerpts`, `manifest-only`, `mixed`; `captured`, `partial`), plus the omissions the note names. A manifest-only note is a list, not text; never present it as full content;
- **collectionPurpose** — the recorded value, or that none is recorded;
- **size** — rough length of Original Content, language, and for a bundle the number of members;
- **topics** — two or three, read from Original Content, not the capture notes alone. A claim found only in Agent Capture Notes is the capturer's reading.

**Duplicates.** Match by source first: canonical `source`/`source_url` or `source_locator`, or a session id; then compare content. Titles and authors never prove sameness. Check within the Inbox (candidates sharing a source form one group; keep every distinct excerpt, since two clips of one page may hold different passages) and against existing Raw (flag the candidate with the Raw's path so `ingest` reuses or extends it). Entries in `referenced` are earlier captures or originals the note cites; they never prove the original was read.

### Step 3: Present

Lead with counts per lane and a total pending. Then one detail table:

| # | Lane | Note | Source | Fidelity | Purpose | Size | Topics | Duplicate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |

List problems (unreadable notes, missing locators, root-level notes) below it. For `count` or `status`, stop here.

### Step 4: Ask

Ask scope and purpose mode in one turn:

1. **Scope** — 전부 / 카테고리만 / 선택만: all, one lane, or named notes. No answer selects nothing; the whole Inbox is never assumed.
2. **Purpose mode** — 미래의 나에게 보내는 편지:
   - **Shared** — one `collectionPurpose` for the whole selection, applied to every note;
   - **Per-file** — `ingest` asks its Step 1 question per note;
   - **Auto-infer** — "알아서/자동으로": `ingest` infers from the source and Core Context §2, recording the inference and its reason in `collectionPurpose`.

A candidate that already carries `collectionPurpose`, or a purpose the task already states, is reused and not asked again; when every selected note has one, ask scope only. Never attach a purpose the owner did not give, approve or delegate.

### Step 5: Ingest

Compose `ingest` once per selected note with its path, its purpose, and the duplicate flags from Step 2. `ingest` owns Raw placement, preserving the candidate's metadata, the 10–15 Wiki pages, Maps, the `index.md` update and the `log.md` entry, and its Step 6 review including qmd reindex status. Run notes sequentially with progress per note: `[3/7] Ingesting: {note}`; never parallelize writes to the same Raw or Map. A prepared selection is not an executed ingest. Nothing is committed or pushed; a commit happens only when the owner separately asks.

### Step 6: Cleanup

After the batch, check each ingest's report against disk: a Raw exists for each selected candidate, its `## Original Content` passed ingest's verbatim check against the Inbox body, and `index.md` and `log.md` were updated. Then ask "Inbox에서 처리된 파일 삭제할까요?", listing the candidates that passed.

- Delete only on an explicit yes, and only candidates whose verbatim check passed; a failed or partial ingest stays in place and is reported.
- Before deleting a candidate, read it back once more as its before-image and confirm its Raw carries the full body verbatim and every source, history and metadata value the candidate held except `date_clipped` (`source`/`source_url`, `collectionPurpose`, `referenced`, Source Manifest, Agent Capture Notes, unknown keys); anything missing keeps that candidate in place and is reported.
- No answer, or anything but yes, leaves every original in place, reported as awaiting cleanup. Declining cleanup is not an ingest failure.
- Never delete unselected candidates, binary originals, or anything outside the listed set.

Report pending counts, the selected scope, completed Raw sources, Wiki pages created or updated, files deleted, and files left in the Inbox.

## Notes

- Lane and frontmatter are both category signals; when they disagree, report it and let `ingest` decide placement from the destination's live policy.
- Web Clipper and RSS arrivals carry source metadata but no owner purpose; Step 4 is where one is given.
