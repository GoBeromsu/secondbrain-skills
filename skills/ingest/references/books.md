# Books

A book is one book Entity (the hub) plus one chapter Raw per chapter, filled as chapters are actually read. The Entity's `## Chapters`, `## Reading Progress` and `## Derived` list the chapter Raws, progress and derived pages. Knowledge is compiled when read, not when scraped; a stub is a future compile target, never evidence that the chapter was read.

Only a book Entity with `## Reading Progress` carries the owner's reading `status`; ingest preserves it and never sets it. Chapter Raws have no `status`; their `Reading Status` callout (`Stub`, `Reading`, `Completed`) records acquisition.

Run Steps 1 and 2 once for the whole book; each stub inherits its `collectionPurpose`. Chapter Raws go into the Books Raw folder with `category: Books` unless live policy or the task names another.

## B-1 — TOC and chapter URL pattern

- Detect a multi-page book or docs site (mdBook, VitePress, GitBook, Docusaurus, ReadTheDocs, Nextra) with 5+ chapters.
- Fetch the preface or index page and extract the full TOC in original order and language: part, chapter number, title, slug hint, TOC one-liner.
- Fetch two chapter URLs directly to confirm the URL pattern before naming anything; if it fails, stop and report rather than invent URLs. A commercial or offline book needs an obtained locator (file or page range) or its stubs stay unpromotable.

## B-2 — Chapter stubs

- One per TOC chapter from [book chapter](../assets/book-chapter.md), named `YYYY-MM-DD-{authorSlug}-{bookSlug}-ch{NN}-{slug}.md`.
- Frontmatter: `source` (verified chapter URL or locator), `book` (quoted wikilink to the Entity), integer `chapterNumber`, original-language `chapterPart`, `chapterPrev`/`chapterNext` (quoted wikilinks, `null` at the ends), inherited `collectionPurpose`, `date_ingested` = scaffold date.
- Body: `Reading Status: Stub` callout, Source, TOC Preview (the one-liner verbatim), `## Original Content` holding the template's placeholder, Reading Notes. The placeholder passes Raw pre-flight only together with the Stub callout.
- Pre-flight per stub: exact placeholder, Stub callout, `chapterNumber`/`chapterPart`/`book` set, prev/next resolve or are `null`, no chapter Wiki page compiled.

## B-3 — Book-level Wiki only

Compile only what the TOC and preface support, through SKILL Step 6: the book Entity from [book](../../entity/assets/book.md), whose `## Chapters` lists every stub as `- [[stub]] — {TOC one-liner}` grouped by part (plus the author's reading paths verbatim); a person Entity per confirmed author; optionally a companion-site Entity; 1–3 Terms or Concepts the preface names as anchors; at most one Guide when the preface gives a reusable method; the Entity linked from a Map. Never precompile chapter pages.

Index and log per Step 9: one Recent Ingests row noting `{N} chapters scaffolded, {M} wiki pages`, one log entry with the progressive compile plan.

## Promotion — a chapter the owner has read

Trigger: ingest on a chapter stub, or the owner describing reading it with intent to compile. Never promote an unread or unobtained chapter.

1. For a `Stub`, confirm Original Content is still exactly the placeholder and obtain the chapter from `source`; for `Reading`, obtain the missing text. Skip `Completed`.
2. Replace the placeholder with the verbatim text, or fill the missing positions without duplicating saved text. Set the callout to `Completed`, or `Reading` with what was obtained; update `date_modified`; keep everything else, owner Reading Notes included.
3. Compile the chapter's pages by Step 6; Steps 7 and 8 apply.
4. In the book Entity append `- [[YYYY-MM-DD]] chNN reading|completed — [[chapter Raw]]` under `## Reading Progress` and each derived page under `## Derived`.
5. Index per Step 9; log `## [YYYY-MM-DD] promote | {book} ch{NN}`.
6. Read back the chapter, the Entity and every touched page; report the qmd reindex status (SKILL Step 10).

## Bibliographic acquisition

- Prefer the URL the owner supplied. Read a Yes24 product page (`defuddle` or the aside browser) for title, authors, date, ISBN-13, TOC and publisher text. Without a TOC, open `https://www.aladin.co.kr/shop/wproduct.aspx?ISBN=<ISBN13>`; its `…/letslook/…_toc<N>.jpg` images (`_toc1` is the cover) count as TOC only after OCR. For a title or ISBN alone, search Yes24, then Aladin.
- Record ISBN-13, TOC and cover in the Entity's `## Bibliographic Record` and `## Table of Contents`, each field labelled by origin: storefront metadata, OCR or inferred summary, or owner-supplied context. A storefront blurb or empty TOC is unfinished work, not a book note.
- For classic texts distinguish the local title, original title, translator and edition. Search for the existing work and edition (ISBN, author, translator, publisher) before creating; a translated title alone is not a different work, editions are never merged silently, and another title is no reason to rename.
- The vault's registered book template wins for keys and headings (never an append-only zone), otherwise [book](../../entity/assets/book.md).

## Selected chapters

Obtain only the selected chapters or excerpts, keeping page and chapter locations, quotation boundaries, missing pages and conversion provenance. A complete TOC is not a complete book, and a selected chapter is not whole-book coverage. Owner reading notes on the book Entity stay word for word (`principle-writing`).
