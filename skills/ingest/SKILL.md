---
name: "ingest"
description: "Ingests one selected source into the wiki: a URL, file, text, paper, book or Inbox candidate becomes a preserved Raw source plus Wiki pages, Entity updates and Maps. Use for creating or updating a Term note, adding a source, ingesting a paper by DOI or citekey, reading a book chapter, adding a book's table of contents, adding source facts to a person, organization, paper, book, media or product Entity, and attributed Persona updates. Saving without compiling belongs to capture."
---

# Ingest

Execute every step in order. Asking for ingest authorizes the writes this recipe names in the destination vault — Raw, Wiki pages, Maps, and the wiki index and log in [records](references/records.md) — under the vault's live policy. It does not authorize deleting an Inbox original or any other file, committing, pushing, or editing owner content outside Step 6's Entity maintenance scope. [Frontmatter](references/frontmatter.md) governs every key; YAML uses 2 spaces, the body tabs, YAML wikilinks are quoted.

This recipe decides what is written and where, not how a note is formed. Before the first write, load every available skill whose description covers note formatting, prose, or source description, and write the Raw source, Wiki pages and Maps by them.

Read the vault's Core Context once per session before the first ingest. Use the reuse axes actually registered in its §2 (normally 5–9), never a fixed list.

## Input

- URL: fetch the content, then process.
- File path or name: read it from the vault, checking the Inbox and its lanes first.
- Blank or `all`: delegate selection to `inbox`.
- Named Term request: resolve the term and its sources with the [Term template](../principle-knowledge-notes/templates/term.md); compile that Term from the preserved evidence.
- Raw text: the argument is the source.
- Academic paper (DOI, arXiv or journal URL, citekey, or a PDF with Abstract and References): the Steps below with [papers](references/papers.md). For a Term request, preserve papers used as evidence through Steps 3 and 5 and compile the requested Term.
- Book, book chapter, or multi-page docs site (5+ chapters in its sidebar or TOC): the Steps below with [books](references/books.md).
- Binary or non-Markdown file: Step 3 after Steps 1 and 2.

Per-material acquisition detail: [articles](references/articles.md), [videos](references/videos.md), [repositories](references/repositories.md), [mail](references/mail.md), [conversations](references/conversations.md).

## Category detection

Pick the Raw `category` in this order: the Inbox lane the file sits in; a `category` in Web Clipper frontmatter; inference from the content; default `Articles`. Save into the destination's Raw folder for that category.

## Step 1 — Collection purpose (a letter to your future self)

Ask exactly one collection-purpose question before ingest, and nothing else:

> When your future self opens this source again — why did you collect it, and where do you plan to use it? Leave one line.
> Reuse axes for reference: {axes registered in Core Context §2}

- Save the answer verbatim as `collectionPurpose`.
- Do not ask when the task already states a valid purpose, or the capture candidate carries `collectionPurpose`; use it.
- When the owner says "you decide" or "automatically", infer the most likely axis from the source and Core Context §2, state the inference and its reason, and record that in `collectionPurpose`.
- Batch: ask once up front — "{N} sources came in today. Should they all share one purpose, or should I ask for each one?" — and follow the choice.

## Step 2 — Connections in this vault

Search the vault read-only with the source's key concepts and the purpose (`qmd`, keyword fallback) and keep the 2–5 most relevant existing notes (the owner's essays, MOC or hub notes, category pages, recent teaching or consulting notes when the purpose is teaching or consulting). Confirm each file exists, drop any that does not, and record the rest as quoted wikilinks `"[[Note Name]]"` in `related` on the Raw and the relevant Wiki pages, adding a folder path only when the basename collides. Notes the owner names in the task join the list after the same check. Ask no further question here. Related owner notes stay untouched; only the Wiki targets selected for compilation are updated under Step 6.

## Step 3 — Format conversion

Skip for `.md`, `.markdown`, `.txt`. Transcribe audio (`.mp3`, `.wav`, `.m4a`) with a transcription tool; leave the audio file where it is and report it. Convert any other document (`.pdf`, `.pptx`, `.docx`, `.hwp`, `.epub`, `.html`, images, …) with an available converter (`markitdown`, `pandoc`, `hwp5txt`, `defuddle`). Move the original binary into the vault's attachments folder under its original filename, place the converted `.md` beside where the binary was, and carry the conversion keys [raw](templates/raw.md) lists into the Raw. `## Original Content` then holds the converted Markdown; the binary stays preserved as the attachment. When no available converter succeeds, leave the binary where it is, name the missing tool or ask the owner to convert, and stop this input; other inputs in the run continue.

## Step 4 — Analyze

Read the whole source and use `principle-knowledge-notes` to classify the extracted knowledge.

Extract:

- terms and concepts (3–8 together), candidates that may land on existing pages;
- entities (1–5);
- practical guidance (0–3) worth a Guide;
- key claims to track;
- connections to existing Wiki pages.

Read the wiki index in [records](references/records.md) and search the vault (`qmd`) for existing pages first; updating an existing page beats creating a new one. Match a source by `source` URL or reference before title. This lookup establishes identity and targets from titles, aliases, paths, `source` and index lines; existing page prose stays out of Step 6's Term, Concept and Guide writer.

When a claim reports another creator's work, attribute it to this source's author as a secondary claim and put the original in the Raw's `referenced`: its Raw or Entity wikilink when already in the vault, otherwise its canonical URL. For single-source ingest, record that link without fetching or ingesting the original. When the owner selects a Term for creation or research, retrieve the original through its DOI, publisher or author repository, and reuse its Raw or preserve it as a distinct Raw; for a Term extracted from one source, attribute secondary claims to the selected source. Record what was actually inspected, including an abstract-only or partial reading, and record provenance unknown in `## Ingest Notes` when it cannot be located. A Concept resting only on secondary claims is at most `confidence: medium`. Each claim stays with its creator and the source it arrived through; never merge claims from different creators into one unattributed statement.

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

For a named Term request, compile the selected Term. For a source ingest, compile each extracted term, concept, entity and guide. In either case, update the existing page or create one: Terms with [term](../principle-knowledge-notes/templates/term.md), Concepts with [concept](../principle-knowledge-notes/templates/concept.md), Guides with [guide](../principle-knowledge-notes/templates/guide.md), Entities of a required type with `../principle-knowledge-notes/templates/entity/{type}.md` (person, organization, place, paper, book, media, product) and Entities of an optional type with [entity](../principle-knowledge-notes/templates/entity.md). A template the vault registers for a kind or type wins for frontmatter keys and owner headings.

Title a Concept `{Topic Name}` in the idea's original language, whichever language that is, with translations in `aliases`.
Explain in its Overview what the idea offers for the Raw's `collectionPurpose`.

- For single-source ingest, ground factual claims in the selected source and personal context in the inspected owner records from Step 2. For a selected Term with multiple sources, give the writer the inspected Original Content of each Raw used, with source identity, access scope and locators kept distinct.
- An existing Term, Concept or Guide is updated in three separate contexts, in this order (Entities follow their template's maintenance mode below):
	1. Writer — a fresh context given only the vault's approved policy, this run's extraction and the relevant Raw source text under `## Original Content`. It never sees the existing page's prose or examples; the page's path, title, aliases, `type`, `layer` and `source` list may be passed to fix identity and target. For a Term it also receives excerpts of the owner's notes and earlier queries that vault search returns for the term, each with its path. It drafts only source-grounded additions for that page; an owner excerpt is quoted as the owner's own context, never as evidence for a fact.
	2. Preservation reviewer — a separate context given the page's before-image and the writer's proposal. It first checks that every valid existing statement, link and frontmatter value survives, then reduces the proposal to the minimal patch: additions under the relevant sections, each newly used Raw appended to `source`, `date_modified` updated. It drops anything the source does not support, except a connection quoting an owner excerpt by its path, and never regenerates the page.
	3. Apply the reviewed patch, read the page back and compare it with the before-image. Links to and from the page are added only after this validation (Step 8).
- When the runtime cannot provide separate contexts, stop the update of that existing page and report it; new pages and the rest of the run continue.
- The existing Wiki is not ground truth, and neither is one source. An existing statement changes only when the correction rests on verified evidence (a `verify` result or the owner's confirmation) and the reviewer accepted it. When this source explicitly conflicts with an existing claim, keep both, attributed, with `> [!warning] Contradiction` and the uncertainty stated. A source that is silent on a claim does not contradict it.
- An Entity exists because the analysis found it significant. Every Raw author whose real name the source confirms is also a person Entity: update the existing one or create it with this Raw in `source`, and link it from the Raw's `author`. A significant named individual of a required type (person, organization, place, paper, book, media, product) is likewise created or updated without asking for approval.
- Update an Entity through its selected type template and [maintenance mode](../principle-knowledge-notes/templates/entity.md#maintenance). Draft from the inspected evidence, apply the required preservation review, and read back the result before adding links.
- Title a person Entity with their source-confirmed real name in its original language and script; put handles, channel names, localized names and romanizations in `aliases`. Never infer a real name; if unconfirmed, report it without presenting an alias as a real name. An explicit live-policy naming exception wins and is reported.
- A new Entity goes into the folder the live policy registers for its type; an existing Entity is not moved. Before creating a required type's folder, map the type to the folder existing notes of that type, or a synonym (`channel` → media, `people` → person), already use. Only when none exists, create one beside the existing Entity type folders, following their naming and numbering, without asking; the report names it and asks the owner to register it in the live policy. For an optional type (event, movie, album, game, …) with no folder yet, ask the owner before creating it, naming the type, the proposed folder and the Entities; without approval create nothing and list them as candidates in the report. A kind, such as a species or a genre, is never an Entity.
- Before creating a Term, search titles and aliases for the same referent; a match is updated, never duplicated, and a new related sense is incorporated into the existing page.
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

Where a Wiki page this ingest created or changed, or one mentioning an Entity it created, names an existing Entity's title or alias in plain text and context confirms the same referent, link the first mention (`[[Entity|original text]]`) unless the page already links that Entity, then read the page back. In an Entity, link only the editable area its template defines. In those pages and this ingest's Raw, a frontmatter value under a key the schema or live policy defines as an Entity reference likewise links to the existing same-vault Entity it names, only when identity is confirmed and the key's meaning stays unchanged. Raw `## Original Content`, quotes, code, URLs, other frontmatter and existing links stay unchanged; an ambiguous mention or value is reported as a candidate, not linked.

## Step 9 — Update index and log

Update the wiki index in [records](references/records.md), completing all four:

- each new Wiki page under its section (Terms, Concepts, Entities, Guides, Maps) as `- [[Page Name]] — one-line description`;
- the Stats table recounted from the folders (Raw Sources, Wiki Pages, Terms, Concepts, Entities, Guides, MOCs, Queries; Terms counted by `layer: terms` when they share the Concept folder), never incremented by guess;
- one Recent Ingests row at the top: date, Raw link, pages touched;
- the index's modification date.

Re-read that index and confirm every new page appears. When the resolved index is missing, create it only at the resolved path, including its parent directory, and say so. When that path is the vault root, stop and report it. Never create `index.md` at the vault root.

Append to the wiki log in [records](references/records.md), never editing earlier entries:

```markdown
## [YYYY-MM-DD] ingest | {source title}

- Source: [[{raw source filename}]]
- **Purpose**: {collectionPurpose verbatim}
- Connections: {related count} — {top 1-2 notes}
- Pages created: [[page1]], [[page2]], ...
- Pages updated: [[page3]], [[page4]], ...
```

Git history does not replace the wiki index or log. Ingest never commits or pushes; when the owner separately asks for a commit, its subject is `ingest: {source title}`.

## Step 10 — Review

Check every item and fix failures:

- the Raw has `## Original Content` with a substantive verbatim body (compared against the Inbox body before any deletion);
- the Inbox original is deleted when deletion was authorized, otherwise reported as awaiting cleanup;
- every new `source`, `related` and body wikilink resolves or is an intentional placeholder allowed by the live policy or selected template; every confirmed author has a person Entity; no duplicate page was created, and no new Term duplicates an existing title or alias for the same referent;
- every touched Entity follows its selected template's structure and [maintenance rules](../principle-knowledge-notes/templates/entity.md#maintenance), with protected content unchanged;
- every updated existing page still holds every valid statement, link and frontmatter value of its before-image, apart from reviewed corrections;
- every new Term, Concept and Guide, and every new Entity the live policy types `wiki-page`, has `explored: false`; every `confidence: high` page has a Bias Check with `Counter-argument:` and `Data gap:` lines;
- every `related` link from Step 2 resolves to an existing note and no literal placeholder remains; external URLs in bodies are `[label](URL)` and no `obsidian://` link is written;
- each new or revised Term passage meets the [Term template](../principle-knowledge-notes/templates/term.md), including its claim locators and source access records;
- every touched Wiki page passes [conformance](references/conformance.md), each item recorded present or absent in the run report;
- every new page appears in the wiki index and the Stats counts match the folders;
- the wiki log entry is appended;
- the qmd index status is known: when `reindex` reports pending or failed work, run it and report the result.

Then invoke `secondbrain-skills:lint` and `secondbrain-skills:verify` on the Wiki pages this ingest created or changed, plus the new Raw for lint; each keeps its own contract.

## Output

Report: the source (title, URL); where the Raw was saved; pages created, each with one line; pages updated and what changed; key connections added; the touched count against 10–15; originals in `referenced` or provenance unknown; Inbox and binary originals left in place; Terms placed in the Concept folder for lack of a registered Terms folder; Entity folders created for required types and optional-type candidates awaiting the owner's approval; open questions, gaps and contradictions.

## Papers

Follow [papers](references/papers.md): the ordinary Steps, with the original retrieved through its DOI, `citekey` and `doi` resolved against the actual paper, and the paper Entity's auto zone as the paper's hub.

## Books

Follow [books](references/books.md): Steps 1 and 2 once for the whole book; bibliographic acquisition and the TOC; one chapter Raw per chapter with [book chapter](templates/book-chapter.md); the book Entity's auto zone as the hub listing chapter Raws, reading progress and derived pages. Never compile unread chapter content. Chapter Raws go into the Books Raw folder with `category: Books`, unless the live policy or the owner's task names another folder and `category` for books.

## Tools

Pages: `defuddle`; transcripts: `defuddle`, `yt-dlp`; pages behind login or JavaScript: the aside browser; search: `qmd`; app operations: `obsidian-cli`.
