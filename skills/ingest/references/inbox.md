# Inbox batch

For a blank or `all` argument, a lane name, `count`/`status`, or "process the Inbox". Resolve the Inbox root and lanes from the vault guideline (ask once when it names none; never guess a folder). Scanning, previewing and counting write nothing.

## Count or status

Walk the Inbox recursively (skip non-notes such as `.gitkeep`) and report pending counts per lane and in total, plus unreadable notes and notes at the Inbox root. No detail table. Then stop.

## Batch

1. **Preview** each candidate: source locator, kind (lane or Web Clipper `category`; a root note's kind is only a suggestion), fidelity (`captureMode`, `capture_status`, named omissions; a manifest-only note is a list, not text), recorded `collectionPurpose`, size, and two or three topics read from Original Content, not from the capture notes.
2. **Duplicates across the Inbox.** Group candidates by canonical `source`/`source_url`, locator or session id, then compare content; titles and authors never prove sameness. One group becomes one Raw that keeps every distinct excerpt. Also flag a candidate whose source already has a Raw, so Step 5 reuses or extends it. `referenced` entries never prove the original was read.
3. **Present** counts per lane, then one table: `# | Lane | Note | Source | Fidelity | Purpose | Size | Topics | Duplicate`, with problems below it.
4. **Ask** scope and purpose mode in one turn. Scope: all, a lane, or named notes; no answer selects nothing. Purpose: **shared** (one `collectionPurpose` for the whole selection), **per-file** (Step 1 per note) or **auto-infer** (recorded with its reason). A purpose a candidate or the task already carries is reused, not asked again.
5. **Ingest** each selected note in turn through Steps 1–10, reporting `[3/7] Ingesting: {note}`. Never parallelize writes to the same Raw or Map.
6. **Cleanup gate.** A candidate may be deleted only when its Raw exists, the Raw's Original Content passed the verbatim check against the Inbox body, the Raw keeps every source, history and metadata value the candidate held except `date_clipped` (including Source Manifest, Agent Capture Notes and unknown keys), and the index and log were updated. List those that passed and ask "Delete the processed files from the Inbox?". Delete only on an explicit yes, re-reading each file first; anything else leaves the originals in place, reported as awaiting cleanup. Never delete unselected candidates, binaries or failed and partial ingests.

Report pending counts, the scope, Raws and Wiki pages written, files deleted and files left in the Inbox.
