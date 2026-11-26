---
name: "capture"
description: "Captures selected tabs, URLs, files, conversations or agent sessions as Inbox candidates, bundling sessions on one topic into one note. Use for save this conversation, capture these tabs, keep this excerpt or harvest sessions on a topic. Not for automatic backup or Web Clipper templates; compiling belongs to ingest."
license: MIT
---

# Capture

Capture preserves evidence in the Inbox and stops at the candidate note unless the owner routes it on. Compiling, and reviewing what waits, is `ingest`.

Read the destination's Core Context once per session and its guideline (live policy) for the Inbox root and lanes. When the guideline leaves out a mapping this run needs, ask the owner once before writing; never guess a folder or invent a lane. Open `principle-knowledge-notes`, `principle-archival`, `principle-markdown` and `principle-editing` (each at `../<principle>/SKILL.md`) before writing.

Default output: one `YYYY-MM-DD-ai-research-{topic-slug}.md` bundle in the AI Research lane. The Clippings lane, same naming, is for short excerpts, social posts, a single web page, or a manifest-only capture without substantial conversation text.

## Rules

1. `## Original Content` holds only text actually acquired, in original order, with range, speakers, timestamps, headings, code and media links intact. Mark each gap in place as `[omitted: {what} — {why}]`; never fill it from memory, a summary or a neighbouring source.
2. Interpretation goes under `## Agent Capture Notes` (legacy `## Codex Capture Notes` counts). A summary or reconstruction is never Original Content.
3. Record each member's URL, platform, visible model, capture method and limitations. Name a tool as the method only when it actually read the text; a paste is recorded as a paste.
4. Capture only the tabs, conversations, sessions or ranges the owner selected; never sweep a window, an unnamed group or a day's sessions.
5. No share links, posts, uploads or account changes unless the owner asks and confirms at action time. Expanding or scrolling is reading; sending, regenerating or editing a message is not allowed.

## Fetching

1. URL, including YouTube: `defuddle parse "$URL" --md`. It returns the clean body as Markdown; for YouTube, the full timestamped transcript under `## Transcript`. Add `-f` for title/author/published hints (check them against the page). Without `--md` it prints HTML, which never goes into a note.
2. Open tabs, tab groups, and pages behind login or JavaScript: the aside browser — list tabs and URLs non-destructively, then read each selected tab.
3. Other video or podcast hosts: `yt-dlp` for captions, else manifest-only.
4. Fallback: ask the owner to paste or export the text.

Chat conversations follow [conversations](references/conversations.md); agent sessions follow [sessions](references/sessions.md). Vault reads and writes use `obsidian-cli` or plain files.

## Process

1. **Scope.** Resolve `topic`, `platforms`, `captureMode` (`transcript`, `manifest-only`, `curated-excerpts` or `mixed`), `nextStep` (`inbox-only`, `run-inbox` or `ingest-now`) and `collectionPurpose`. Ask one question for the whole bundle only when neither the task nor an earlier candidate states the purpose; save the answer verbatim. When the owner delegates, infer it from the source and the reuse axes in Core Context §2 and record the inference with its reason. A purpose never triggers compilation. If the topic or tab group is ambiguous, ask before operating the browser.
2. **Manifest.** Per member: platform, title, URL (session id and range for agent sessions), visible model/workspace, role (question answering, counterpoint, source evidence, follow-up).
3. **Extract.** Prefer built-in copy/export that creates no public link, else the Fetching order. Record gaps, truncation, collapsed answers, failed extraction and paywalled or auth-only content as omissions and in the member's status. Keep chronology within a conversation and the owner's order across members.
4. **Write.** Use the destination's AI Research Capture template; without one, the shape below. Always a new note; never overwrite or reorder an existing candidate. A later capture on the same topic lists the earlier one in `referenced`.
5. **Capture notes.** Under `## Agent Capture Notes`: a one-paragraph summary, key claims by platform, source URLs the models cited, disagreements, missing evidence or follow-ups, Wiki pages to create or update at ingest.
6. **Route.** `inbox-only` (default) stops and reports the path; `run-inbox` runs `ingest`'s [Inbox batch](../ingest/references/inbox.md) on the file; `ingest-now` runs `ingest`, whose purpose gate reuses `collectionPurpose`. Route beyond `inbox-only` only when the owner chose it. Capture never deletes or moves the Inbox note and never commits.

```yaml
aliases: []
author:
  - "[[{owner-name}]]"
  - "{Agent}"
capture_method: "{tool actually used}"
capture_status: "captured"
captureMode: "mixed"
category:
  - "AI Research"
clip_type: "ai-research-tab-group"
collectionPurpose: "{verbatim answer, or inference + reason}"
date_clipped: YYYY-MM-DD
date_created: YYYY-MM-DD
date_modified: YYYY-MM-DD
description: "English one-sentence description of the captured bundle."
effort: "{runtime-reported effort, or default}"
model: "{runtime-reported model id}"
platforms:
  - "ChatGPT"
referenced: []
source_url:
  - "{primary-url-or-conversation-url}"
tags:
  - inbox
  - agent-capture
  - ai-research
type: "inbox"
```

`capture_status` is truthfully `captured`, `partial` or `manifest-only`. `referenced` lists originals and earlier captures the material cites (a wikilink when already in the vault, else the canonical URL); it never claims the original was read and never authorizes fetching it. Body: `## Capture Summary`, `## Source Manifest` (# | Platform | Title | URL as `[title](URL)` | Role | Capture status), `## Original Content` (one `### Source N` block per member with platform, URL, visible model and limitation; the source's own headings shift below level 3 so none closes the section), `## Agent Capture Notes`, `## Ingest Notes`.

`ingest` later carries `source_url` → `source`, `collectionPurpose` and `referenced` into the Raw and moves the Source Manifest and Agent Capture Notes unchanged under `## Ingest Notes`.

## Verification

Read the note back before reporting: it exists at the new dated path in the resolved lane; Original Content is non-empty and holds only acquired text (or `captureMode: manifest-only`); every member has a URL; synthesis is separate and omissions are marked in place; `collectionPurpose` is set; after `ingest-now`, the Raw exists and the Inbox original stays.

Report the path, members with capture status, omissions, the purpose, the route taken, and each principle that changed a decision and what it changed.
