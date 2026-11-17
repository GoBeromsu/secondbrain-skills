# Books

Book Mode: one Book Index plus N chapter stubs, filled progressively as chapters are actually read. Knowledge is compiled when read, not when scraped; a stub is a navigable future-compile target, never evidence that the chapter was read.

## Steps 1 and 2

Run SKILL Steps 1 and 2 once for the whole book: one purpose covers every chapter and is inherited by each stub's `collectionPurpose`.

## Folder and category

The Index and stubs go into the Books Raw folder with `category: Books`, unless the live policy or the owner's task names another folder and `category` for books.

## B-1 — Fetch TOC and chapter URL pattern

- Detect a multi-page book or docs site (mdBook, VitePress, GitBook, Docusaurus, ReadTheDocs, Nextra) with 5+ chapters in its sidebar or TOC.
- Fetch the preface/readme/index page and extract the full TOC in original order: part, chapter number, title, slug hint and the TOC one-liner when given, all in the original language.
- Test the URL pattern by fetching two chapter URLs directly (for example mdBook `/ch01-00-foo.html`, VitePress/Docusaurus `/ch01-foo/`, GitBook `/book/chapter-1/section-1`). Confirm the pattern matches reality before naming anything; if it fails, stop and report rather than invent URLs.
- A commercial or offline book has no chapter URL to test; its stubs need an obtained locator (file or page range) or stay unpromotable.

## B-2 — Book Index (one Raw)

- Name `YYYY-MM-DD-{authorSlug}-{bookSlug}-book-index.md` with [book index](../templates/book-index.md); `type: raw-source`, `status: ingested`, no chapter keys.
- `## Original Content` holds the preface verbatim.
- `## TOC` lists every chapter as `- [ ] [[stub filename]] — {TOC one-liner}`, grouped under `### {Part}` headings when the source has parts.
- `## Reading Paths` keeps the author's reading paths verbatim when provided; omit the section otherwise, never infer paths.
- `## Progress Tracking` is a table `| Ch | Title | Status | Read on |`, one row per chapter, starting `stub`.

## B-3 — Chapter stubs (N Raws)

- Name `YYYY-MM-DD-{authorSlug}-{bookSlug}-ch{NN}-{slug}.md` with [book chapter](../templates/book-chapter.md), one per TOC chapter.
- Frontmatter: `status: stub`, `source` = the direct chapter URL (verified pattern), `bookIndex`, integer `chapterNumber`, original-language `chapterPart`, `chapterPrev`/`chapterNext` as quoted wikilinks to the adjacent stubs (`null` at the first and last chapter), `collectionPurpose` inherited from the book, `date_ingested` = scaffold date.
- Body: Reading Status stub callout, Source, TOC Preview (the TOC one-liner verbatim), `## Original Content` holding the non-empty pending-fill placeholder by design (it satisfies the Raw pre-flight; substantiveness checks exempt `status: stub`), Reading Notes.
- Pre-flight per stub: Original Content present, `status: stub`, resolvable chapter URL, `chapterNumber`/`chapterPart`/`bookIndex` set, prev/next resolve to existing stubs or are `null`, no chapter Wiki page compiled.

## B-4 — Book-level Wiki only (small set)

Compile only what the TOC and preface support, through SKILL Step 6:

- Entity for the book itself (native title);
- Entity for the author only when the analysis finds the author significant, never just to resolve the `author` link;
- optional Entity for a companion site;
- 1–3 Terms or Concepts the preface names as anchors of the whole book;
- optional 0–1 Guide when the preface itself gives a reusable methodology (for example reading paths);
- the Book Index linked from the relevant Map, created when none exists (Step 8).

Never precompile chapter-specific pages.

## B-5 — Index and log

- Wiki index from [records](records.md): new book-level pages under their sections, Stats recounted, one Recent Ingests row noting `{N} chapters scaffolded, {M} wiki pages`.
- Wiki log from the same record: one appended entry for the whole scaffold, noting the progressive compile plan.

## Promotion — a chapter the owner has read

Trigger: the owner runs ingest on a chapter stub or describes reading that chapter with intent to compile. Never promote an unread or unobtained chapter.

1. Fetch the chapter from the stub's `source`. Only `status: stub` whose Original Content is still exactly the placeholder is promotable.
2. Replace only the placeholder with the verbatim chapter text; set `status: completed` for the full chapter or `reading` when only part was obtained; update `date_modified`. Every other byte stays, including Source, TOC Preview, human Reading Notes and the navigation keys. A later `reading` → `completed` needs the missing text actually obtained.
3. Compile the chapter's Wiki pages by SKILL Step 6, updating existing pages first under its clean-context rule; Steps 7 and 8 apply.
4. In the Book Index change only this chapter: its TOC checkbox `- [ ]` → `- [x]` and its Progress Tracking row to `| N | [[chapter]] | reading-or-completed | YYYY-MM-DD |`. All other Index bytes, human notes included, stay.
5. Update the wiki index per Step 9 and append to the wiki log: `## [YYYY-MM-DD] promote | {book} ch{NN}`.
6. Read back the chapter, the Index and every touched page, then report qmd reindex status (Step 10).

## Bibliographic acquisition

Prefer the URL the user supplied.
Read a Yes24 product page with `defuddle` or the aside browser for title, authors, publication date, ISBN-13, TOC and publisher text.
When the TOC is missing, open `https://www.aladin.co.kr/shop/wproduct.aspx?ISBN=<ISBN13>`; its TOC images are `…/letslook/…_toc<N>.jpg` (`_toc1` is the cover) and count as TOC text only after OCR is actually performed.
For a title or ISBN alone, search Yes24 first and then Aladin.
For classic or historical texts, distinguish the recognized local title, the original-language title, the translator and the edition.

Label every recorded field by origin: observed storefront metadata, OCR or inferred summary, or user-supplied reading context.
A storefront blurb is not a finished summary, and a three-line summary is not catalog fact.
A storefront blurb or empty TOC is unfinished bibliographic work, not a finished book note.

## Work and edition identity

Search for the existing work and edition with verified bibliographic data (ISBN, author, translator, publisher, edition) before creating a note.
A translated or alternate title alone does not establish a different work, and differing editions are never merged silently.
Discovering another title is not a reason to rename an existing note; a requested move needs a supported, link-preserving surface.
The destination vault's template decides note identity, field mapping, naming and placement; a missing book template or registration blocks creation and is reported as such, not worked around with an invented schema.

## Selected chapters

Obtain only the selected chapters or supplied excerpts.
Retain original page/chapter locations, quotation boundaries, missing pages and conversion provenance.
Write purpose-grounded chapter analysis with links back to the obtained evidence, and reusable Concepts only where their independent information value warrants them.
A complete TOC is not a complete book, and a selected chapter is not whole-book coverage.

## Human reading

The personal book/review template remains owned by the destination vault.
Preserve the destination's human reading sections: thinking, reactions, dated personal bullets, anecdotes and next steps.
Quotes stay quotes and first-person notes stay first-person.
When updating, map existing highlights onto the TOC chapters instead of appending them as a dump, and keep the richer copy of a duplicated highlight.
When the exact review append is authorized, put agent suggestions and useful verified links only in its actual permitted Suggested/Linking sections; never rewrite the owner's review sections.
