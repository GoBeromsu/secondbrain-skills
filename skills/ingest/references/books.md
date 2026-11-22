# Books

A book is one book Entity plus N chapter Raws, filled progressively as chapters are actually read. The book Entity's `## From Sources` auto zone is the hub: it lists the chapter Raws, reading progress and the pages derived from them. Knowledge is compiled when read, not when scraped; a stub is a navigable future-compile target, never evidence that the chapter was read.

## Steps 1 and 2

Run SKILL Steps 1 and 2 once for the whole book: one purpose covers every chapter and is inherited by each stub's `collectionPurpose`.

## Folder and category

Chapter stubs go into the Books Raw folder with `category: Books`, unless the live policy or the owner's task names another folder and `category` for books.

## B-1 — Fetch TOC and chapter URL pattern

- Detect a multi-page book or docs site (mdBook, VitePress, GitBook, Docusaurus, ReadTheDocs, Nextra) with 5+ chapters in its sidebar or TOC.
- Fetch the preface/readme/index page and extract the full TOC in original order: part, chapter number, title, slug hint and the TOC one-liner when given, all in the original language.
- Test the URL pattern by fetching two chapter URLs directly (for example mdBook `/ch01-00-foo.html`, VitePress/Docusaurus `/ch01-foo/`, GitBook `/book/chapter-1/section-1`). Confirm the pattern matches reality before naming anything; if it fails, stop and report rather than invent URLs.
- A commercial or offline book has no chapter URL to test; its stubs need an obtained locator (file or page range) or stay unpromotable.

## B-2 — Chapter stubs (N Raws)

- Name `YYYY-MM-DD-{authorSlug}-{bookSlug}-ch{NN}-{slug}.md` with [book chapter](../templates/book-chapter.md), one per TOC chapter.
- Frontmatter: `status: stub`, `source` = the direct chapter URL (verified pattern), `book` as a quoted wikilink to the book Entity, integer `chapterNumber`, original-language `chapterPart`, `chapterPrev`/`chapterNext` as quoted wikilinks to the adjacent stubs (`null` at the first and last chapter), `collectionPurpose` inherited from the book, `date_ingested` = scaffold date.
- Body: Reading Status stub callout, Source, TOC Preview (the TOC one-liner verbatim), `## Original Content` holding the non-empty pending-fill placeholder by design (it satisfies the Raw pre-flight; substantiveness checks exempt `status: stub`), Reading Notes.
- Pre-flight per stub: Original Content present, `status: stub`, resolvable chapter URL, `chapterNumber`/`chapterPart`/`book` set, prev/next resolve to existing stubs or are `null`, no chapter Wiki page compiled.

## B-3 — Book-level Wiki only (small set)

Compile only what the TOC and preface support, through SKILL Step 6:

- the book Entity (native title) from [book](../../principle-knowledge-notes/templates/entity/book.md), created or updated by SKILL Step 6's Entity rules; its auto zone lists every chapter stub as `- [[stub filename]] — {TOC one-liner}`, grouped under the source's parts, and the author's reading paths verbatim when given;
- a person Entity for each author whose real name the source confirms, by SKILL Step 6;
- optional Entity for a companion site;
- 1–3 Terms or Concepts the preface names as anchors of the whole book;
- optional 0–1 Guide when the preface itself gives a reusable methodology (for example reading paths);
- the book Entity linked from the relevant Map, created when none exists (Step 8).

Never precompile chapter-specific pages.

## B-4 — Index and log

- Wiki index from [records](records.md): new book-level pages under their sections, Stats recounted, one Recent Ingests row noting `{N} chapters scaffolded, {M} wiki pages`.
- Wiki log from the same record: one appended entry for the whole scaffold, noting the progressive compile plan.

## Promotion — a chapter the owner has read

Trigger: the owner runs ingest on a chapter stub or describes reading that chapter with intent to compile. Never promote an unread or unobtained chapter.

1. Fetch the chapter from the stub's `source`. Only `status: stub` whose Original Content is still exactly the placeholder is promotable.
2. Replace only the placeholder with the verbatim chapter text; set `status: completed` for the full chapter or `reading` when only part was obtained; update `date_modified`. Every other byte stays, including Source, TOC Preview, human Reading Notes and the navigation keys. A later `reading` → `completed` needs the missing text actually obtained.
3. Compile the chapter's Wiki pages by SKILL Step 6, updating existing pages first under its clean-context rule; Steps 7 and 8 apply.
4. In the book Entity's auto zone append `- YYYY-MM-DD chNN reading|completed — [[chapter Raw]]` under `### Reading Progress`, and each page compiled from the chapter under `### Derived`. The owner zone and earlier auto-zone lines stay.
5. Update the wiki index per Step 9 and append to the wiki log: `## [YYYY-MM-DD] promote | {book} ch{NN}`.
6. Read back the chapter, the book Entity and every touched page, then report qmd reindex status (Step 10).

## Bibliographic acquisition

Prefer the URL the user supplied.
Read a Yes24 product page with `defuddle` or the aside browser for title, authors, publication date, ISBN-13, TOC and publisher text.
When the TOC is missing, open `https://www.aladin.co.kr/shop/wproduct.aspx?ISBN=<ISBN13>`; its TOC images are `…/letslook/…_toc<N>.jpg` (`_toc1` is the cover) and count as TOC text only after OCR is actually performed.
For a title or ISBN alone, search Yes24 first and then Aladin.
For classic or historical texts, distinguish the recognized local title, the original-language title, the translator and the edition.

Record ISBN-13, TOC and cover in the book Entity's auto zone. Label every recorded field by origin: observed storefront metadata, OCR or inferred summary, or user-supplied reading context.
A storefront blurb is not a finished summary, and a three-line summary is not catalog fact.
A storefront blurb or empty TOC is unfinished bibliographic work, not a finished book note.

## Work and edition identity

Search for the existing work and edition with verified bibliographic data (ISBN, author, translator, publisher, edition) before creating a note.
A translated or alternate title alone does not establish a different work, and differing editions are never merged silently.
Discovering another title is not a reason to rename an existing note; a requested move needs a supported, link-preserving surface.
The destination vault's registered book template wins for frontmatter keys and owner headings, otherwise the [book](../../principle-knowledge-notes/templates/entity/book.md) Entity template; the live policy decides naming and placement. Never invent a schema beyond either.

## Selected chapters

Obtain only the selected chapters or supplied excerpts.
Retain original page/chapter locations, quotation boundaries, missing pages and conversion provenance.
Write purpose-grounded chapter analysis with links back to the obtained evidence, and reusable Concepts only where their independent information value warrants them.
A complete TOC is not a complete book, and a selected chapter is not whole-book coverage.

## Human reading

The book Entity's owner zone holds the owner's reading: thinking, reactions, dated personal bullets, anecdotes, highlights and next steps. Ingest never writes, reorders or rephrases it.
Quotes stay quotes and first-person notes stay first-person.
Agent suggestions and verified links go only into the auto zone, as appended lines.
