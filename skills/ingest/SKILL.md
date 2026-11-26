---
name: "ingest"
description: "Ingests selected sources into the wiki: a URL, file, text, paper, book or Inbox candidate becomes a preserved Raw source plus Wiki pages, Entity updates and Maps, and the qmd search index is refreshed after. A repository becomes a Product Entity about why the owner needs the tool, with no Raw. Use when the owner hands over material to compile: adding a source, ingesting a paper by DOI or citekey, reading a book chapter, adding a book's table of contents, adding source facts to a person, organization, paper, book, media, product or event Entity, attributed Persona updates, reviewing, counting or batch-processing the Inbox, and reindexing qmd search after notes change. Saving without compiling belongs to capture."
---

# Ingest

Execute every step in order. Asking for ingest authorizes, under the vault's live policy, the writes this recipe names: the Raw, Wiki pages, Maps, the Step 6 person-impressions move, and the wiki index and log in [records](references/records.md). It does not authorize deleting an Inbox original or any other file, committing, pushing, or rewriting owner sentences. [Frontmatter](references/frontmatter.md) governs every key.

This recipe decides what is written and where. How a note is formed comes from the principles each step names; read `../<principle>/SKILL.md` at that step. Open `principle-knowledge-notes` and `principle-editing` before the first write.

Read the vault's Core Context once per session; use the reuse axes actually registered in its §2, never a fixed list.

## Input

- URL: fetch it with `defuddle` per [articles](references/articles.md) or [videos](references/videos.md) (YouTube included).
- File path or name: read it from the vault, checking the Inbox and its lanes first.
- Blank, `all`, an Inbox lane, `count`/`status`, or "process the Inbox": the batch in [inbox](references/inbox.md).
- Raw text: the argument is the source.
- Named Term with no material handed over: run [`term`](../term/SKILL.md) instead. With material, preserve it as Raws (Steps 3 and 5), then compile the Term by `term`'s rules.
- Repository: [repositories](references/repositories.md) — a Product Entity, no Raw.
- Paper (DOI, arXiv or journal URL, citekey, or a PDF with Abstract and References): [papers](references/papers.md).
- Book, chapter, or a docs site with 5+ chapters in its sidebar or TOC: [books](references/books.md).
- Mail or conversation export: [mail](references/mail.md), [conversations](references/conversations.md).
- An already-ingested source that changed, or a Raw that needs another pass: [reingest](references/reingest.md).

## Category

Pick the Raw `category` in this order: the Inbox lane the file sits in; a Web Clipper `category`; inference from the content; default `Articles`. Save into the destination's Raw folder for that category.

## Step 1 — Collection purpose

Ask exactly one question, and nothing else:

> When your future self opens this source again — why did you collect it, and where do you plan to use it? Leave one line.
> Reuse axes for reference: {axes registered in Core Context §2}

- Save the answer verbatim as `collectionPurpose`. Skip the question when the task or the capture candidate already states the purpose.
- When the owner says "you decide", infer the most likely axis, and record the inference and its reason.
- Batch: ask once whether all sources share one purpose or each gets its own.

## Step 2 — Connections

Search the vault read-only (`qmd`, keyword fallback) with the source's key concepts and the purpose; keep the 2–5 most relevant existing notes (essays, MOCs, hubs, notes tied to the purpose) plus any the owner names. Confirm each exists and record them in `related` on the Raw and the relevant Wiki pages. Those owner notes stay untouched.

## Step 3 — Format conversion

Skip for `.md`, `.markdown`, `.txt`. Transcribe audio with a transcription tool and leave the audio in place. Convert other documents (`.pdf`, `.pptx`, `.docx`, `.hwp`, `.epub`, `.html`, images) with `markitdown`, `pandoc`, `hwp5txt` or `defuddle`; move the binary into the attachments folder under its original filename, put the converted `.md` where the binary was, and add the conversion keys from [frontmatter](references/frontmatter.md#raw-source-keys). When no converter succeeds, leave the binary, name the missing tool, and stop this input; other inputs continue.

## Step 4 — Analyze

Read the whole source and classify what it holds with `principle-knowledge-notes`: 3–8 terms and concepts, 1–5 entities, 0–3 guides worth writing, key claims, and connections to existing pages.

Look up existing pages first in the wiki index ([records](references/records.md)) and the vault: updating beats creating. Match by `source` URL or reference before title. This lookup fixes identity and targets only; existing page prose stays out of Step 6's writer.

Open `principle-archival` for every claim that reports another creator's work: attribute it to this source's author as a secondary claim and put the original in the Raw's `referenced` (its vault wikilink, else its canonical URL) without fetching it. When the owner selects a Term for research, retrieve originals through their DOI, publisher or author repository, reuse an existing Raw, and otherwise cite `[label](URL)` with no new Raw. Record abstract-only or partial readings and unknown provenance in `## Ingest Notes`. A Concept resting only on secondary claims is at most `confidence: medium`.

## Step 5 — Save the Raw

Open `principle-archival` and `principle-markdown`. Use [raw](assets/raw.md), filename `{Title}.md` (`{Title} (YYYY-MM-DD).md` when taken).

- `## Original Content` holds the source verbatim however long: no summary, no "redacted for brevity". Images stay `![alt](url)` (never downloaded); media URLs, quotes, citations, code and timestamps survive. Follow it with `<!-- end-original-content -->` on its own line.
- Pasted text is preserved from its first line, including any title, byline, date or URL inside the excerpt; the owner's instructions stay outside it.
- OCR every image that contains text into a `>` blockquote directly below it, spelling unchanged; note the method and uncertain readings in `## Ingest Notes`.
- A clipper body already under `## Original Content` is copied as is. Remove only an obvious clipper artifact and say so in `## Ingest Notes`.
- From a Web Clipper or capture candidate carry `source_url` → `source`, `author` → `"[[Name]]"`, `published` → `date_published`, `collectionPurpose` and `referenced`. A capture's Source Manifest and Agent Capture Notes go under `## Ingest Notes` unchanged.

Pre-flight: read the saved Raw back and compare it with the obtained source — pasted text and short clippings in full, an Inbox source on at least 80% of its body lines; media, quotes, citations and code survived; the 7 required keys are present.

Inbox cleanup: delete the Inbox original only when the owner's request or live policy authorizes it, after that read-back and pre-flight; otherwise report it as awaiting cleanup.

## Step 6 — Compile Wiki pages

Open `principle-writing`, `principle-markdown` and `principle-editing` for every page. Compile each extracted term, concept, entity and guide (for a Term request, the selected Term), updating the existing page or creating one from its template: Terms by [`term`](../term/SKILL.md), Concepts by [`concept`](../concept/SKILL.md), Entities by [`entity`](../entity/SKILL.md) with `../entity/assets/{type}.md`, Guides with [guide](assets/guide.md). A template the vault registers wins for keys and headings but never brings back an append-only zone (`## Wiki`, `## From Sources`). Write every page to [conformance](references/conformance.md).

- Title a Concept in the idea's original language, translations in `aliases`; its Overview says what the idea offers for the Raw's `collectionPurpose`.
- Ground facts in the selected source and personal context in the owner notes from Step 2. For a multi-source Term, give the writer each Raw's Original Content with its identity and locators kept distinct.
- Update an existing page by [updating](references/updating.md), in three separate contexts:
	1. Writer — sees only policy, this run's extraction and the Raw's Original Content (for a Term, also owner excerpts with their paths, quoted as the owner's context, never as evidence); never the page's prose. It drafts source-grounded additions.
	2. Reviewer — sees the before-image and the proposal; keeps every valid statement, link and value, reduces the proposal to the minimal patch (additions, the Raw appended to `source`, `date_modified`, template migration) and drops anything the source does not support.
	3. Apply, read back against the before-image. Links come later (Step 8).
	Without separate contexts, skip that page's update and report it; the rest of the run continues.
- Every Raw author whose real name the source confirms is a person Entity: update or create it with this Raw in `source`, linked from the Raw's `author`. Other significant individuals of a required type (person, organization, place, paper, book, media, product, event) are created or updated without asking.
- Title a person with the source-confirmed real name in its original script; handles, channel names and romanizations go in `aliases`. Never infer a real name.
- A new Entity goes into the folder live policy registers for its type, or the folder existing notes of that type (or a synonym: `channel` → media, `people` → person, `program` → event) already use. Only when none exists create one beside the other Entity folders, following their naming, and ask the owner to register it. An optional type (movie, album, …) without a folder: ask first; without approval list the Entities as candidates.
- When the update touches a person page holding owner impressions, perform `entity`'s person migration without asking: move them byte-for-byte to `{date_created} {Name}.md` in the permanent-notes folder (`authorship: user`, `related` both ways), verify the destination before removing the original, never overwrite existing destination content.
- Before creating a Term, search titles and aliases for the same referent; a match is updated. A new Term goes into the registered Term folder, else the Concept folder (reported).
- A Guide keeps a Contradiction callout only for an explicit conflict, and a Bias Check only for `confidence: high` or synthesis-heavy pages. A Guide `secondbrain-mode` sends for a How-to solved in conversation runs only this step and Step 10's read-back and conformance: no Raw, Map, index or log; `source` cites the work note where it was solved (empty when solved only in chat, with the confirmation date in Overview), and its writer takes the confirmed steps as evidence.
- New pages get `explored: false`; set `claimType` and `evidenceScope` when the classification is clear.

Aim for 10–15 pages touched for a substantial source; a thin source reports the shortfall instead of padding.

## Step 7 — Persona

When the author or primary speaker matches an existing Persona card, append to it as [persona](assets/persona.md) shows, with the provenance update in [frontmatter](references/frontmatter.md#existing-notes-and-migration). Never create a Persona.

## Step 8 — Connect

Open `principle-markdown`, `principle-archival` for a Map, and `principle-editing`. Body links go only into wiki pages; the Raw gets only frontmatter Entity links; a work note follows the vault roles' first-mention rule. Link related wiki pages and leave no orphan.

- Map: find the existing topical MOC in the live Map folder (topic search, then a folder listing, then Map links from the index or related notes) before creating one. Add each new page in its scope without duplicates, read the Map back, and report a target discovery could not confirm instead of creating a duplicate. A `related` entry, backlink or index line is not a Map update.
- Entity links: where a page this ingest created or changed names an existing Entity's title or alias with the same referent, link its first eligible prose mention (`[[Entity|original text]]`); frontmatter Entity-reference values link the same way. Original Content, quotes, owner sentences, code and URLs stay; an ambiguous mention is reported, not linked.

## Step 9 — Index and log

Resolve both paths by [records](references/records.md); an unavailable record is skipped and reported, never guessed, and `index.md` is never created at the vault root. In the index add each new page under its section as `- [[Page]] — one-line description`, recount the Stats table from the folders (Terms by `layer: terms` when they share the Concept folder), add one Recent Ingests row at the top (date, Raw link, pages touched), update its modification date, and re-read it. Describe only coverage you verified. Append to the log, never editing earlier entries:

```markdown
## [YYYY-MM-DD] ingest | {source title}

- Source: [[{raw source filename}]]
- **Purpose**: {collectionPurpose verbatim}
- Connections: {related count} — {top 1-2 notes}
- Pages created: [[page1]], [[page2]], ...
- Pages updated: [[page3]], [[page4]], ...
```

Never commit or push; a commit the owner asks for separately follows [git provenance](references/git-provenance.md).

## Step 10 — Review

Check and fix:

- the Raw's Original Content is substantive and verbatim; the Inbox original is deleted only if authorized;
- every new `source`, `related` and body wikilink resolves; every confirmed author has a person Entity; no duplicate page or Term;
- every updated page keeps every valid statement, link and value of its before-image; owner sentences and relocated impressions are byte-identical;
- new Terms, Concepts, Guides and `wiki-page` Entities have `explored: false`; every `confidence: high` page has a Bias Check with `Counter-argument:` and `Data gap:` lines;
- no `obsidian://` link and no raw URL in authored prose;
- the relevant Map links the new pages; the index lists them with recounted Stats; the log entry is appended;
- re-read each touched page for Entity titles and aliases — citations, footnotes, References, attributions and table cells included — and link the first eligible mention; when the only mention is preserved text, link it in the adjacent attribution;
- each Term passage meets the [Term template](../term/assets/term.md), and each page passes [conformance](references/conformance.md), every item recorded present or absent;
- the qmd index is fresh (see Reindex below).

Then run `secondbrain-skills:lint` on the changed Wiki pages and the Raw, and `secondbrain-skills:verify` on the changed Wiki pages.

Run `python3 ../lint/scripts/link-lint.py --checks policy --vault <vault> --scope <each changed wiki file, quoted>`, repeating `--wiki` and `--entity-folder` per registered folder, `--book-type` and `--product-type` per declared type, and `--lifecycle` for other lifecycle types (see [`lint` Step 12](../lint/SKILL.md)). Read its output unfiltered, fix unambiguous `ENTITY-UNLINKED` findings, rerun. A clean check does not replace the read-back above, and an unavailable tool is not a clean result.

**Reindex.** Run `qmd update`, then `qmd embed`, then `qmd status`, over the collections qmd already registers (the Inbox stays out until ingested); confirm the commands with `qmd --help`. Report the document and vector counts and any `Pending: N need embedding` line; a non-zero exit or unreadable status is unfinished, never zero pending. Never run `qmd embed -f`, or change qmd models, collections or configuration, unless the owner approved that change. Without `qmd`, report it and continue. When the owner asks only to reindex, this paragraph is the whole run.

## Output

When routed through secondbrain-mode, return only these fields:

- `findings`: source title and citation, substantive findings relevant to the user, evidence gaps or contradictions; nothing about writes or maintenance.
- `wiki_outcomes`: `created` and `updated` lists of vault-relative paths confirmed by read-back, and `failed` entries (path and reason) for attempted wiki writes that failed. Include changed Maps, index and log in the wiki area; exclude Raw, work notes and unattempted work. Classify each page once by whether it existed at the start.
- `principle_decisions`: decision-changing principles as judgments about the subject, classification or evidence, not accounts of edits.
- `owner_questions`: only questions the owner must answer to finish the task.

Standalone, report the principle decisions, source (title, URL), Raw location, key connections, pages touched against 10–15, originals in `referenced` or provenance unknown, Inbox and binary originals left in place, Term folder fallback, Entity folders created, optional-type candidates, and open questions, gaps and contradictions. End with one line, omitting empty clauses and the line itself when no wiki write happened: `Wiki: created [[X]], updated [[Y]], failed [[Z]] (reason)`.

## Tools

Pages and YouTube transcripts: `defuddle parse "$URL" --md`; other video: `yt-dlp`; pages behind login or JavaScript: the aside browser; search: `qmd`; app operations: `obsidian-cli`.
