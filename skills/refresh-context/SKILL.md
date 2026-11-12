---
name: "refresh-context"
description: "Refreshes the Core Context snapshot, agent context about the owner: re-reads its registered sources, diffs them and applies changes on the owner's yes. Use when the owner's role, reuse axes, philosophy or mothership sources changed, or status or lint reports the snapshot stale. Not for editing Me or vault policy; reporting its age belongs to status."
license: MIT
---

# Refresh Context

[[Core Context]] is the owner's **시점 snapshot** — who they are at a point in time: §1 identity and continuity statement, §2 reuse axes, §3 frameworks, §4 philosophy, §5 mothership references. When the owner's thinking develops, or the (optional) mothership changes, the snapshot must follow. Every `ingest` purpose question and every `query` answer is tailored to it, so a stale snapshot quietly bends all later work. The sources stay the truth; this skill brings the snapshot back in line with them and nothing more.

The note is usually `Core Context.md`, sometimes a derived file such as `90. Settings/Derived/agent-context.md`; use the one the vault's AGENTS file names.

## When to Run

- `lint` or `status` flags "Core Context > 30 days old", or a later change to a source it lists, or mothership drift.
- (with a mothership) a mothership system file changed version, precedence, folders or roles.
- The owner published a new essay or manifesto — §4 philosophy may need updating.
- A reuse axis (§2) was added, dropped or renamed, or the owner's role changed.
- The continuity statement (§1) needs updating, or the owner asks.

A snapshot that is old but whose sources have not changed needs only its date checked, not a rewrite; say so.

## Step 1: Load Current Core Context

Read the note in full: `snapshot_date`, `version`, the `source` list, and §1–§5. This is the "before" side of the diff.

## Step 2: (optional) Re-Read Mothership System Files

Read, read-only, each mothership system file the Core Context actually registers (§5 table and `source`); there is no fixed list or file count. For each, capture:

- `version` — bumped?
- date modified — newer than the snapshot? With Git: `git -C "$MOTHERSHIP" log --since="$SNAPSHOT_DATE" --oneline -- <files>`.
- the first changelog entry — what changed?
- whether the change touches the §5 table: precedence, audience, focus, memory type.

No mothership registered: skip and say so. A registered file missing on disk is reported and the run carries on with this vault.

## Step 3: (optional) Re-Read Personal Essays

Re-read every essay in the frontmatter `source` list in full. Then scan for **new** essays from the last 60 days in the essay location §5 names (`find "$ESSAYS" -name '*.md' -mtime -60`, or `qmd` for recent writing). New essays are candidates, not sources: summarize each in one line and let the owner decide. Do not add sources by guessing from folder names; if none can be identified, ask.

## Step 3-b: (optional, with a mothership) Scan Recent Permanent Notes

Scan, read-only, the mothership's Permanent Notes folder — the one Core Context registers (usually `30. Permanent Notes/`) — for notes modified in the last 60 days (`find "$PERMANENT" -name '*.md' -mtime -60`, or `git -C "$MOTHERSHIP" log --since="60 days ago" --name-only -- "$PERMANENT"`). They are evidence of philosophy drift for §3/§4, not new `source` entries: quote the line behind each proposed change in Step 4. No Permanent Notes folder registered: skip and say so; never guess one from folder names.

## Step 4: Diff & Propose

Show side by side, section by section:

- **Current Core Context** (§1–§4 core sections, §5 when touched);
- **Proposed updates**, each with the source line behind it;
- **New essays** discovered, one-line summary each, asking whether to promote them into §4 philosophy and `source`;
- **Permanent Notes drift** from Step 3-b, one line per note with the claim it supports.

Owner judgment on top:

- Every proposed claim traces to a source just read; anything untraceable stays out. Never fill a section from names, paths or an older snapshot.
- Keep the owner's own wording where it still holds. Refreshing is not rephrasing.
- Reuse axes are the ones registered in §2 (normally 5–9, never a fixed list) and the owner's to define; propose a change only when a source states it, and flag that later `ingest` purposes and `query` answers will shift.

Ask: **"Apply this diff? (전체 / 부분 / 거부)"** — in the owner's language. 거부, or no answer, writes nothing, including no log entry.

## Step 5: Apply

If approved, edit only the approved sections and leave the rest of the file byte-for-byte. Set `snapshot_date` and `date_modified` to today, add approved essays to `source`, bump `version` (minor for §2/§4/§5 changes, major for a restructure). A later proposal needs its own OK. Read the note back.

## Step 6: Log

When writes were approved, append to `log.md` (append-only; never rewrite earlier entries):

```markdown
## [YYYY-MM-DD] update | Core Context refreshed (v<old> → v<new>)

- Mothership drift: <files changed since the last snapshot, or none>
- New essays incorporated: <titles, or none>
- Updated sections: <§2 / §4 / §5 …>
- Why: <one line>
```

Git history does not replace this entry. Do not commit or push; commit only when the owner asks separately.

## Output

1. **Snapshot age**: was N days, now 0 (or unchanged, and why).
2. **Changes applied**: one line per section changed; sections left as they were.
3. **Mothership drift**: files changed since the last snapshot and recent Permanent Notes used as evidence, or not configured.
4. **New essays added to source**: count and titles.
5. **Version bump**: old → new.

Never edit Me, AGENTS, policy notes, user instructions, the mothership or another vault, qmd configuration or runtime profiles from here; if a source looks wrong, tell the owner. Do not publish the snapshot.

Tools: `rg`, `qmd`, `git` (read-only).
