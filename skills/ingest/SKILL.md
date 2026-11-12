---
name: "ingest"
description: "Ingests one selected source into the wiki: a URL, file, text, paper, book (책 노트, 독서 노트, 목차 넣어줘) or Inbox candidate becomes a preserved Raw source plus Wiki pages and Maps. Use for adding a source, paper analysis (12-axis), book notes, chapter promotion and attributed Persona updates. Saving without compiling belongs to capture."
---

# Ingest

Execute every step in order. Asking for ingest authorizes the writes this recipe names in the destination vault — Raw, Wiki pages, Maps, `index.md`, `log.md` — under the vault's live policy. It does not authorize deleting an Inbox original or any other file, committing, pushing, or writing into a mothership. [Frontmatter](references/frontmatter.md) governs every key; YAML uses 2 spaces, the body tabs, YAML wikilinks are quoted.

Read the vault's Core Context once per session before the first ingest. Use the reuse axes actually registered in its §2 (normally 5–9), never a fixed list.

## Input

- URL: fetch the content, then process.
- File path or name: read it from the vault, checking the Inbox and its lanes first.
- Blank or `all`: delegate selection to `inbox`.
- Raw text: the argument is the source.
- Academic paper (DOI, arXiv or journal URL, a document with Abstract and References, a file from the papers lane): Paper Mode.
- Multi-page book or docs site (5+ chapters in its sidebar or TOC): Book Mode.
- Binary or non-Markdown file: Step 3 after Steps 1 and 2.

Per-material acquisition detail: [articles](references/articles.md), [videos](references/videos.md), [repositories](references/repositories.md), [mail](references/mail.md), [conversations](references/conversations.md).

## Category detection

Pick the Raw `category` in this order: the Inbox lane the file sits in; a `category` in Web Clipper frontmatter; inference from the content; default `Articles`. Save into the destination's Raw folder for that category.

## Step 1 — Collection purpose (미래의 나에게 보내는 편지)

Ask exactly one collection-purpose question before ingest, and nothing else:

> 미래의 내가 이 자료를 다시 볼 때 — 왜 수집했고, 어디에 쓸 예정인지 한 줄 남겨주세요.
> 재활용 축 참고: {Core Context §2 에 등록된 축}

- Save the answer verbatim as `collectionPurpose`.
- Do not ask when the task already states a valid purpose, or the capture candidate carries `collectionPurpose`; use it.
- When the owner says "알아서 판단해줘" or "자동으로", infer the most likely axis from the source and Core Context §2, state the inference and its reason, and record that in `collectionPurpose`.
- Batch: ask once up front — "오늘 들어온 {N}개 소스, 전체를 하나의 목적으로 묶으시겠어요, 아니면 개별로 물을까요?" — and follow the choice.

## Step 2 — Mothership connections

Skip when Core Context registers no mothership. Otherwise search it read-only with the source's key concepts and the purpose (`qmd`, keyword fallback), keep the 2–5 most relevant notes (essays, MOC or hub notes, category pages, recent teaching or consulting notes when the purpose is teaching or consulting), and for each:

1. use the exact path the search returned;
2. confirm the file exists before using it, dropping any that does not;
3. percent-encode both URI components separately: the vault name with `urllib.parse.quote(vault, safe='')` and the path with `urllib.parse.quote(path, safe='')`;
4. write it in the `mainVaultRelated` form [raw](templates/raw.md) shows, labelled with the filename without `.md`.

Notes the owner names in the task or explicitly confirms go through the same four checks and join the list. Fill `mainVaultCmds` only with a category or command reference the Core Context or mothership actually registers, copied exactly in its registered form and with the cardinality the live policy defines; leave it empty when none fits. Never invent or impose a classification. Record the stat-verified list in `mainVaultRelated` on the Raw and the relevant Wiki pages, and list it in the report. Ask no further question here. Never write into the mothership.

Use `obsidian://open` unless the live policy names another form such as `obsidian://advanced-uri`.

## Step 3 — Format conversion

Skip for `.md`, `.markdown`, `.txt`. Transcribe audio (`.mp3`, `.wav`, `.m4a`) with a transcription tool; leave the audio file where it is and report it. Convert any other document (`.pdf`, `.pptx`, `.docx`, `.hwp`, `.epub`, `.html`, images, …) with an available converter (`markitdown`, `pandoc`, `hwp5txt`, `defuddle`). Move the original binary into the vault's attachments folder under its original filename, place the converted `.md` beside where the binary was, and carry the conversion keys [raw](templates/raw.md) lists into the Raw. `## Original Content` then holds the converted Markdown; the binary stays preserved as the attachment. When no available converter succeeds, leave the binary where it is, name the missing tool or ask the owner to convert, and stop this input; other inputs in the run continue.

## Step 4 — Analyze

Read the whole source and use `principle-wiki-types` to classify the extracted knowledge.

Extract:

- terms and concepts (3–8 together), candidates that may land on existing pages;
- entities (1–5);
- practical guidance (0–3) worth a Guide;
- key claims to track;
- connections to existing Wiki pages.

Read `index.md` and search the vault (`qmd`) for existing pages first; updating an existing page beats creating a new one. Match a source by `source` URL or reference before title. This lookup establishes identity and targets from titles, aliases, paths, `source` and index lines; existing page prose stays out of Step 6's writer.

When a claim reports another creator's work, attribute it to this source's author as a secondary claim and put the original in the Raw's `referenced`: its Raw or Book Index wikilink when already in the vault, otherwise its canonical URL. Never fetch or ingest the original for this; record provenance unknown in `## Ingest Notes` when it cannot be located. A Concept resting only on secondary claims is at most `confidence: medium`. Each claim stays with its creator and the source it arrived through; never merge claims from different creators into one unattributed statement.

## Step 5 — Save Raw Source

Use [raw](templates/raw.md), filename `{Title}.md` (`{Title} (YYYY-MM-DD).md` when that name is taken); an Inbox candidate keeps its existing name so links to it resolve. The Raw keeps the source's own order and structure; nothing is reordered, regrouped or normalized.

- Preserve the original verbatim under `## Original Content` — no summaries, no "redacted for brevity", however long. Keep image lines `![alt](url)`, video and media URLs, quote blocks, citation lists and code blocks.
- Keep each image as its original `![alt](url)`; do not download it.
- OCR every image that contains text and put the text, as Markdown with spelling unchanged, in a `>` blockquote directly below the image. Record the OCR method and any uncertain reading in `## Ingest Notes`.
- A clipper body already wrapped in `## Original Content` is copied verbatim. A fetched URL keeps the fetched content.
- Remove only obvious clipper artifacts (a block repeated by a clipper bug) and say so in `## Ingest Notes`.
- From a Web Clipper or capture candidate carry over `source_url` → `source`, `author` → `author` as `"[[Name]]"`, `published` → `date_published`, `collectionPurpose` and `referenced`. A capture's Source Manifest and Agent Capture Notes go under `## Ingest Notes`, unchanged; they guide Step 6 and never enter Original Content.
- Never rewrite an existing Raw body. When an already-ingested source changed, ask the owner first: a minor change keeps the Raw; a major change becomes `{Title}-v2.md` with `supersedes`, the earlier Raw gains `superseded-by`, and both stay. See [source update and reprocessing](references/reingest.md).

Pre-flight before moving on:

- `## Original Content` is present;
- its body matches the obtained source: for an Inbox source at least 80% of the Inbox body's lines, a short clipping in full;
- images, media URLs, quotes, citations and code blocks survived;
- the 7 required properties are present.

Inbox cleanup: delete the Inbox original only when the owner's request or the vault's live policy authorizes removing it, and only after the pre-flight passes; when several Inbox files went into one Raw, the same applies to each and `## Ingest Notes` lists them. Without that authorization leave the original in place and report it as awaiting cleanup. A URL, an external file or raw text leaves nothing to delete.

## Step 6 — Compile Wiki pages

For each extracted term, concept, entity and guide, update the existing page or create one: Terms with [term](templates/term.md), Concepts with [concept](templates/concept.md), Entities with [entity](templates/entity.md), Guides with [guide](templates/guide.md).

Title a Concept `{Topic Name}` in the idea's original language, whichever language that is, with translations in `aliases`.
Explain in its Overview what the idea offers for the Raw's `collectionPurpose`.

- New writing comes only from this source and is attributed to it.
- An existing page is updated in three separate contexts, in this order:
	1. Writer — a fresh context given only the vault's approved policy, this run's extraction and the Raw's `## Original Content`. It never sees the existing page's prose or examples; the page's path, title, aliases, `type`, `layer` and `source` list may be passed to fix identity and target. For a Term it also receives excerpts of the owner's notes and earlier queries that vault search returns for the term, each with its path. It drafts only source-grounded additions for that page; an owner excerpt is quoted as the owner's own context, never as evidence for a fact.
	2. Preservation reviewer — a separate context given the page's before-image and the writer's proposal. It first checks that every valid existing statement, link and frontmatter value survives, then reduces the proposal to the minimal patch: additions under the relevant sections, the Raw appended to `source`, `date_modified` updated. It drops anything the source does not support, except a connection quoting an owner excerpt by its path, and never regenerates the page.
	3. Apply the reviewed patch, read the page back and compare it with the before-image. Links to and from the page are added only after this validation (Step 8).
- When the runtime cannot provide separate contexts, stop the update of that existing page and report it; new pages and the rest of the run continue.
- The existing Wiki is not ground truth, and neither is one source. An existing statement changes only when the correction rests on verified evidence (a `verify` result or the owner's confirmation) and the reviewer accepted it. When this source explicitly conflicts with an existing claim, keep both, attributed, with `> [!warning] Contradiction` and the uncertainty stated. A source that is silent on a claim does not contradict it.
- An Entity exists because the analysis found it significant. Every Raw author whose real name the source confirms is also a person Entity: update the existing one or create it with this Raw in `source`, and link it from the Raw's `author`.
- Title a person Entity with their source-confirmed real name in its original language and script; put handles, channel names, localized names and romanizations in `aliases`. Never infer a real name; if unconfirmed, report it without presenting an alias as a real name. An explicit live-policy naming exception wins and is reported.
- A new Entity goes into the folder the live policy registers for its subtype, otherwise the Entity folder; an existing Entity is not moved.
- Title and structure a Term by [terms](references/terms.md).
- Before creating a Term, search titles and aliases for the same referent; a match is updated, never duplicated, and a new sense becomes a section of the existing page.
- A new Term goes into the folder the live policy registers for Terms; when none is registered, it goes into the Concept folder and the report says so. Ingest never moves or retypes an existing page.
Write every Wiki page to [conformance](references/conformance.md).

- Set `explored: true` only after a human or agent completed the Exploration Gate check and documented it in the page body.
- When the classification is clear, set `claimType` and `evidenceScope` for later `verify`.

Target: 10–15 Wiki pages touched per ingest when the source is substantial, created or updated. It is not a creation quota; a thin source reports the shortfall instead of padding.

## Step 7 — Persona accumulation

When the source's author or primary speaker matches an existing Persona card, append to it as [persona](templates/persona.md) shows. Never create a Persona during ingest.

For a GitHub file, `## Original Content` comes from the raw file at a pinned commit (`raw.githubusercontent.com/{owner}/{repo}/{sha}/…`), never a rendered-page scrape.

## Step 8 — Connect

After Step 6's readback, add `[[wikilinks]]` between all related pages, create or update the relevant Map (MOC), and leave no orphan: every new page is linked from at least one other page.

Where a Wiki page this ingest created or changed, or one mentioning an Entity it created, names an existing Entity's title or alias in plain text and context confirms the same referent, link the first mention (`[[Entity|original text]]`) unless the page already links that Entity, then read the page back. In those pages and this ingest's Raw, a frontmatter value under a key the schema or live policy defines as an Entity reference likewise links to the existing same-vault Entity it names, only when identity is confirmed and the key's meaning stays unchanged. Raw `## Original Content`, quotes, code, URLs, other frontmatter and existing links stay unchanged; an ambiguous mention or value is reported as a candidate, not linked.

## Step 9 — Update index and log

Update `index.md`, completing all four:

- each new Wiki page under its section (Terms, Concepts, Entities, Guides, Maps) as `- [[Page Name]] — one-line description`;
- the Stats table recounted from the folders (Raw Sources, Wiki Pages, Terms, Concepts, Entities, Guides, MOCs, Queries; Terms counted by `layer: terms` when they share the Concept folder), never incremented by guess;
- one Recent Ingests row at the top: date, Raw link, pages touched;
- the index's modification date.

Re-read `index.md` and confirm every new page appears. When the vault has no `index.md`, create it with those sections and say so in the report.

Append to `log.md`, never editing earlier entries:

```markdown
## [YYYY-MM-DD] ingest | {source title}

- Source: [[{raw source filename}]]
- **Purpose**: {collectionPurpose verbatim}
- Mothership links: {mainVaultRelated count} — {top 1-2 paths}
- Pages created: [[page1]], [[page2]], ...
- Pages updated: [[page3]], [[page4]], ...
```

Git history does not replace `index.md` or `log.md`. Ingest never commits or pushes; when the owner separately asks for a commit, its subject is `ingest: {source title}`.

## Step 10 — Review

Check every item and fix failures:

- the Raw has `## Original Content` with a substantive verbatim body (compared against the Inbox body before any deletion);
- the Inbox original is deleted when deletion was authorized, otherwise reported as awaiting cleanup;
- every new `source`, `related` and body wikilink resolves, except `author` links to a person whose real name the source does not confirm; every confirmed author has a person Entity; no duplicate page was created, and no new Term duplicates an existing title or alias for the same referent;
- every updated existing page still holds every valid statement, link and frontmatter value of its before-image, apart from reviewed corrections;
- every new Wiki page has `explored: false`; every `confidence: high` page has a Bias Check with `Counter-argument:` and `Data gap:` lines;
- every `mainVaultRelated` link resolves on the mothership filesystem with both `vault` and `file` percent-encoded, no literal placeholder remains, `mainVaultCmds` holds only a reference the mothership actually registers, copied exactly;
- every touched Wiki page passes [conformance](references/conformance.md), each item recorded present or absent in the run report;
- every new page appears in `index.md` and the Stats counts match the folders;
- the `log.md` entry is appended;
- the qmd index status is known: when `reindex` reports pending or failed work, run it and report the result.

Then invoke `secondbrain-skills:lint` and `secondbrain-skills:verify` on the Wiki pages this ingest created or changed, plus the new Raw for lint; each keeps its own contract.

## Output

Report: the source (title, URL); where the Raw was saved; pages created, each with one line; pages updated and what changed; key connections added; the touched count against 10–15; originals in `referenced` or provenance unknown; Inbox and binary originals left in place; Terms placed in the Concept folder for lack of a registered Terms folder; open questions, gaps and contradictions.

## Paper Mode

Follow [papers](references/papers.md) with [paper hub](templates/paper-hub.md) and [paper atom](templates/paper-atom.md): P-0 purpose and target RQ, P-1 paper type, P-2 Raw, P-3 hub and knowledge atoms across the twelve axes, P-4 Wiki promotion, P-5 RQ sync for an owner-designated RQ only, P-6 `index.md` (hub only) and `log.md` (`ingest-paper`), P-7 verification with `scripts/verify_paper.py` plus a read-back (a PASS is necessary, not proof of fidelity). The question budget is exactly two, P-0 and P-1: P-0 carries the Step 1 purpose question, a purpose the task already states is used without asking, and Step 2 runs without a question, recording stat-verified and owner-confirmed links only. Promote only what the paper supports, updating existing pages before creating; a shortfall against P-4's target is reported, never padded. There is no blanket Scale, RQ or Persona promotion.

## Book Mode

Follow [books](references/books.md): Steps 1 and 2 once for the whole book, B-1 TOC and chapter URL pattern, B-2 Book Index, B-3 chapter stubs, B-4 a small set of book-level pages, B-5 `index.md` and one `log.md` entry; on Promotion append `## [YYYY-MM-DD] promote | {book} ch{NN}`. Never compile unread chapter content.

The Book Index and chapter stubs go into the Books Raw folder with `category: Books`, unless the live policy or the owner's task names another folder and `category` for books.

## Tools

Pages: `defuddle`; transcripts: `defuddle`, `yt-dlp`; pages behind login or JavaScript: the aside browser; search: `qmd`; app operations: `obsidian-cli`.
