---
name: "capture"
description: "Captures selected tabs, URLs, files, conversations or agent sessions as Inbox candidates, bundling sessions on one topic into one note. Use for save this conversation, capture these tabs, keep this excerpt or harvest sessions on a topic. Not for automatic backup or Web Clipper templates; compiling belongs to ingest."
license: MIT
---

# Capture

Capture is the pre-ingest capture layer: it preserves evidence in the Inbox and stops at the candidate note unless the owner routes it on. Compiling it is `ingest`; reviewing what waits is `inbox`. Read the destination's Core Context once per session before the first capture.

## Purpose

Use this skill when the owner has a tab group, open tabs, a URL, a file, an AI-chat research session (ChatGPT, Gemini, Grok, Claude, Perplexity) or selected agent sessions and wants it kept as Markdown in `00. Inbox/` before `ingest`.

The default output is one research-bundle note:

`00. Inbox/05. AI Research/YYYY-MM-DD-ai-research-{topic-slug}.md`

Use `00. Inbox/04. Clippings/` only for short excerpts, social posts, or a manifest-only capture without substantial conversation text. When the destination's live policy names different Inbox lanes, use its lane with the same dated naming; never invent a lane.

## Capture Principles

1. Preserve evidence before synthesis.
2. Keep raw copied transcript under `## Original Content`: only text actually acquired, in its original order, with the selected range, speakers, timestamps, turn order, headings, code and media links intact. Mark every gap in place as an explicit omission (`[omitted: {what} — {why}]`); never fill it from memory, a summary or a neighbouring source.
3. Put agent interpretation under `## Agent Capture Notes`, never inside `## Original Content`. A summary, paraphrase or reconstruction is never Original Content.
4. Treat existing `## Codex Capture Notes` sections as legacy-compatible agent notes.
5. Record source URLs, platform names, visible model names, capture method, and capture limitations. Name a browser or runtime as the method only when a tool actually read it; a pasted export is recorded as a paste.
6. Do not create public share links, post messages, upload files, or change account settings unless the owner explicitly asks and confirms at action time. Expanding collapsed answers or scrolling to load history is reading; sending, regenerating or editing a message is not.
7. Capture only the tabs, conversations, sessions or ranges the owner selected; never sweep a window, an unnamed group or every session of the day.

## Tool Choice

Prefer the least lossy available path:

1. Existing tab group or open tabs: the aside browser — list tabs and read titles/URLs non-destructively first, then read each selected tab's text.
2. Normal web page or URL that opens without the owner's session: `defuddle`, then the aside browser. YouTube via `defuddle`; other video or podcast via `yt-dlp`, else manifest-only.
3. Fallback: ask the owner to copy the conversation text or export/download it, then capture the pasted or local file content into the template.

Chat conversations follow [conversations](references/conversations.md); agent sessions follow [sessions](references/sessions.md). Vault reads and writes use `obsidian-cli` or plain files.

## Process

### Step 0: Scope

Resolve from the request or the visible browser session:

- `topic` — the research topic or tab-group name;
- `platforms` — ChatGPT, Gemini, Grok, Claude, Perplexity, and any source sites or runtimes;
- `captureMode` — `transcript`, `manifest-only`, `curated-excerpts`, or `mixed`;
- `nextStep` — `inbox-only`, `run-inbox`, or `ingest-now`;
- `collectionPurpose` — why this is kept and where it will be reused.

Purpose gate: ask one question for the whole bundle only when neither the task nor an earlier candidate states the purpose. Save the answer verbatim. When the owner delegates ("알아서", "자동으로"), infer it from the source and the reuse axes actually registered in Core Context §2, and record both the inference and its reason in `collectionPurpose`. A purpose never triggers compilation.

If the topic or target tab group is ambiguous, ask one concise question before operating the browser.

### Step 1: Read Tab Metadata

Build the manifest, per selected member:

- platform;
- title;
- URL (session id and range for agent sessions);
- visible model / account / workspace if relevant;
- role in research — "question answering", "counterpoint", "source evidence", or "follow-up".

### Step 2: Extract Conversation Or Page Text

For each selected tab:

1. Prefer built-in copy/export controls when they produce local text without creating a public link.
2. Otherwise read the page text through the aside browser or `defuddle`.
3. If UI reading is the only path, read the visible conversation without sending anything.
4. Record gaps, truncation, hidden collapsed answers, failed extraction, and paywalled or auth-only content as omissions and as the member's capture status.

Keep chronology within a conversation and the owner's order across members.

### Step 3: Create Inbox Note

Use the destination's AI Research Capture template as the shape; without one, use the frontmatter and body below. Write a new note; never overwrite or reorder an existing candidate. A later capture on the same topic is a new note that lists the earlier one in `referenced`.

Frontmatter:

```yaml
type: "inbox"
aliases: []
category:
  - "AI Research"
clip_type: "ai-research-tab-group"
source_url:
  - "{primary-url-or-conversation-url}"
platforms:
  - "ChatGPT"
capture_method: "{tool actually used}"
capture_status: "captured"
captureMode: "mixed"
collectionPurpose: "{verbatim answer, or inference + reason}"
referenced: []
description: "English one-sentence description of the captured research bundle."
author:
  - "[[{owner-name}]]"
  - "{Agent}"
model: "{runtime-reported model id}"
effort: "{runtime-reported effort, or default}"
date_created: YYYY-MM-DD
date_modified: YYYY-MM-DD
date_clipped: YYYY-MM-DD
tags:
  - inbox
  - agent-capture
  - ai-research
```

`referenced` lists originals and earlier captures the material cites: a wikilink when already a Raw or Book Index in the vault, else the canonical URL. It never claims the original was read and never authorizes fetching it. `capture_status` is `captured`, `partial` or `manifest-only` truthfully. Body: `## Capture Summary`, `## Source Manifest` (# | Platform | Title | URL | Role | Capture status), `## Original Content` (one `### Source N` block per member with platform, URL, visible model/workspace and capture limitation), `## Agent Capture Notes`, `## Ingest Notes`.

### Step 4: Add Capture Notes

Under `## Agent Capture Notes`, add:

- one-paragraph topic summary;
- key claims by platform;
- source URLs mentioned by the models;
- disagreements between platforms;
- missing evidence or follow-up questions;
- suggested Wiki pages to create/update during `ingest`.

`ingest` carries `source_url` → `source`, `collectionPurpose` and `referenced` into the Raw and places the Source Manifest and Agent Capture Notes under `## Ingest Notes`, unchanged.

### Step 5: Route

- `inbox-only` (default): stop after writing the Inbox note and report the file path.
- `run-inbox`: run `inbox` on the new file.
- `ingest-now`: run `ingest` on the new file; its purpose gate reuses `collectionPurpose`, and its mothership link search (Step 2) runs there.

Route beyond `inbox-only` only when the owner chose it. Never delete or move the Inbox note, and never commit, as part of capture.

## Verification

Read the written note back before reporting:

1. The `.md` file exists at the new dated path in the AI Research or Clippings lane (or the live policy's equivalent).
2. `## Original Content` is non-empty and holds only acquired text, or the note is explicitly `captureMode: manifest-only`.
3. Source URLs are present for every member.
4. Agent synthesis is separated from raw content; omissions are marked where they occur.
5. `collectionPurpose` is set.
6. If the next step was ingest, `ingest` preserved the Raw Source; the Inbox original stays unless the owner separately authorizes its deletion.

Report the path, members with capture status, omissions, the purpose, and the route taken.
