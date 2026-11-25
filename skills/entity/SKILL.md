---
name: "entity"
description: "Apply when the user shows interest in a specific named thing (not a kind or a method): a product, tool, library or model, a person, an organization, a place, a book, a paper, or a channel, podcast or newsletter. Research it and write or update its Entity page in the wiki from the template for its type. Also use whenever the owner asks to add, record or update a person, company, product, book, paper or place note, or brings news about one. Material the owner hands over to compile, such as a paper's PDF or an article, belongs to ingest; a request to save it without compiling belongs to capture."
license: MIT
---

# Entity

Research one identifiable thing and leave the wiki with one Entity page that tells the owner what a source alone cannot: what it is, where it came from, how it really works, and what their own records show about it. The answer the user asked for comes first; the page is written after, and the report names it.

Every type is revised and consolidated: the page is one sourced synthesis, rewritten as evidence grows, with no append-only zone. Open each principle leaf named at a step by reading `../<leaf>/SKILL.md` before acting on that step.

## Step 1 — Resolve the type, the vault roles and the target

Open `principle-note-kinds` and `principle-entity-types`, then pick the type and its template. A kind (a genre, a species, a category of tool) is a Term or Concept, not an Entity.

| Type | What it is | Template |
| --- | --- | --- |
| `person` | a named human | [person](assets/person.md) |
| `organization` | a company, lab, team, school, government body | [organization](assets/organization.md) |
| `place` | a named location: venue, city, landmark | [place](assets/place.md) |
| `paper` | one scholarly work, identified by DOI and citekey | [paper](assets/paper.md) |
| `book` | one book work and edition | [book](assets/book.md) |
| `media` | a publisher that keeps putting things out: a YouTube channel, podcast, newsletter, blog | [media](assets/media.md) |
| `product` | named software, a service, a library, an agent, a model or a dataset | [product](assets/product.md) |
| optional | any other named individual: an event, a movie, an album, a game title | [other](assets/other.md) |

A template the vault registers for the type wins over these for frontmatter keys and headings, except that it never brings back an append-only zone (`## Wiki`, `## From Sources`).

The live policy decides each type's folder. Creating or adding to an Entity inside an existing type folder needs no approval. A required type with no folder yet gets one without asking: first map it to the folder existing notes of that type or a synonym already use (`channel` → media, `people` → person), otherwise create one beside the existing Entity folders in their naming and numbering, and name it in the report for the owner to register. For an optional type with no folder, name the type, the proposed folder and the Entities that would go there, and ask the owner; without approval create nothing and list them as candidates. A move or a type correction of an existing Entity happens only on the owner's own request.

Read the vault guideline (live policy) for the folders that play the wiki, source and work roles and for the permanent-notes folder; the type's folder follows the rules above. When the guideline leaves out one of these role mappings this run needs, stop before writing and run `onboard`'s Vault roles step, which asks the owner once and records the answer; never guess a folder. Running as a subagent, return the missing mappings to the main thread instead, which asks once for all of them. Open `principle-vault-roles` and `principle-resolve-target`.

## Step 2 — Look the entity up in the vault

Run every `obsidian` command with `vault=<resolved vault>` and give `backlinks` the candidate page as `path=`, as [`obsidian-cli`](../obsidian-cli/SKILL.md) requires; an untargeted command reads whatever vault or note has focus.

Search titles, aliases, handles, translations and identifiers (ISBN, DOI, citekey, repository) with `obsidian search query=<name>` and `obsidian backlinks path=<page>`. An existing page or alias for the same referent is updated, never duplicated, and never moved or retyped; open `principle-revise-and-consolidate` and `principle-preserve-voice`, and follow [updating](../ingest/references/updating.md): before-image, a separate reviewer, template migration on touch. When the run only brings news, add just the new claims.

## Step 3 — Gather before writing

One source rarely carries all the page needs, so collect evidence first and write second. Open `principle-provenance`.

- **The maker's or subject's own account.** Beyond what triggered the page, read their own pages for origin and mechanism: an about or history page, the documentation of the feature the owner cares about, release notes for what changed; for a repository, the README and the files that carry the claim at one commit. Read as many as the claims need; when a page that should carry the origin could not be found, say which was sought instead of stretching one source.
- **The owner's record.** Search the whole vault for the name and aliases, not only the notes the request names: daily and periodic notes, project notes, essays, meeting notes. Read each hit in context and note its date; mentions scattered over years are where a change of view lives.
- **The limits.** For each claim, note what its evidence does not establish: a maker's retrospective is not independent research, a documented rule is not a measured effect.
- Every web page read stays a `[label](URL)` link on the page. Save a Raw only when the owner handed the material over and asked to ingest or save it; that is `ingest`'s job.

## Step 4 — Write the page

Fill the type's template. Open `principle-standalone-note`, `principle-not-a-research-log`, `principle-plain-tldr`, `principle-quotation-attribution`, `principle-note-shape`, `principle-draw-structure`, `principle-frontmatter`, `principle-link-form` and `principle-markdown-blocks`.

Naming:

- Title the page with the full original name, followed by the common abbreviation in parentheses when one is in use. Put abbreviations, translations, former names, handles and romanizations in `aliases`.
- Title a person with the real name a source confirms, in its original language and script; never infer a real name. When none is confirmed, report it rather than presenting an alias as a real name.

Format:

- Frontmatter keys in alphabetical order; about five subject tags. Fill only keys a source supports and omit the rest.
- When the live policy types Entities `wiki-page`, a new page also gets the wiki-page fields of the [frontmatter contract](../ingest/references/frontmatter.md): `layer: entities`, `explored: false`, `confidence` and `verificationStatus: unverified`. An existing page keeps its own `explored`, `confidence` and `verificationStatus` values.
- A template the vault registers for the type wins for frontmatter keys and headings, except that it never brings back an append-only zone (`## Wiki`, `## From Sources`).
- External URLs in frontmatter only under `*_url` keys as plain URLs (`blog_url`, `instagram_url`, `linkedin_url`, `x_url`, `youtube_url`, and `feed_url` and `source_url` as the vault's properties already define them); the canonical homepage, or a product's repository, stays `url`. `source` lists vault notes as quoted wikilinks. When updating a page with older keys (`youtube`, `x`, `linkedin`, `website`, `feedUrl`, `repository`), move a value to its `*_url` or `url` key only when it is a URL with the same meaning; a bare handle or a conflicting value stays and is reported ([updating](../ingest/references/updating.md)).
- Every entity name with a page in the vault is a `[[wikilink]]` in the body and a quoted wikilink in frontmatter (`organization: "[[Imperial College London]]"`). Quoted words stay as written, so when such a name appears only inside a quotation, link it once in your own prose beside the quotation.
- At read-back, check that each existing vault entity is linked once in the body, at its first eligible prose mention. Never alter quoted or preserved text.
- Body external links are `[label](URL)`; no raw URL. No list of channels or profiles in the body; those are frontmatter keys.
- English section headings in the template's order. No `---` in the body and no `status` key.

Sections:

- **TL;DR** says what it is and, in bold, why it matters to the owner's work, in plain text; on a person page the bold phrase is the fact that matters most.
- **Origin** names who made it or who they are, when, their relevant background and the problem they said prompted it, then separates that account from what it is today.
- **Explanation** opens with one concrete worked example and follows the mechanism or work the owner depends on. Bold the one reading a newcomer usually gets wrong. Date changing features, prices, roles and versions.
- **Personal Insights** is organized under `###` headings named for a theme or judgment, never as a dated list of mentions. Each paragraph cites the records it draws on, quotes the owner's sentence where it carries the judgment, and keeps an earlier view beside the later one that replaced it. A conclusion no record states is labelled as interpretation. When the vault holds no owner record, say so in one sentence.
- **Footnotes** carry each sourced claim's locator and, where it changes how the claim reads, the limit of that evidence as a fact about the evidence. One named footnote per source passage, reused.
- **References** lists each external work once, with a nested line giving its publication date, or that none is shown, and what it establishes.

## Type rules

- **person.** The body holds only sourced facts and `## Updates`; the template has no Personal Insights, and the general Personal Insights rule does not apply. Facts a source states about the person go into Origin and Explanation; news goes under `## Updates` as dated lines, newest last: `- [[YYYY-MM-DD]] {fact} — [label](URL)` or `— [[Raw]]`. Impressions the owner wrote do not live on the entity: move them, sentences unchanged, into a separate note in the permanent-notes folder named `{date_created} {Name}`, where `date_created` is the person page's value. That note has `authorship: user` and `related: "[[{Name}]]"`; once it exists, the person page's `related` links it back; until then that `related` item is left out. Writing it is the one permitted new note in the work area.
- **organization.** Use the name it uses for itself. A branch with its own address is its own Entity. A product it makes, a channel it runs and a place it occupies are separate Entities, linked.
- **place.** Use the name in local use, qualified by area when shared. A trip or itinerary is not a place. The organization that runs it is its own Entity.
- **media.** One video, episode, issue or post is a Raw, listed under `## Published`, never an Entity. The person or organization behind it is its own Entity named in `operators`; a channel never replaces its operator's page.
- **book.** Identity is the work and edition: search by ISBN, author, translator, publisher and edition before creating; a translated or alternate title alone is not a different work, and editions are separate Entities, never merged silently. For a classic, distinguish the recognized local title, the original-language title, the translator and the edition. `author` holds the book's authors. Set bibliographic keys only from the bookstore or publisher page, and label each Bibliographic Record line `observed`, `inferred` or `owner`. The cover is cited as an observed line in the Bibliographic Record. The table of contents is kept in original order and language with its source linked; an empty table of contents is unfinished bibliographic work. Chapter Raws are listed under `## Chapters`, progress as appended dated lines; the latest line for a chapter is its state. `## Highlights` is filled only by the owner or a highlight-sync tool. Reading-state keys the owner set (`status`, `bookstore`, `date_started`, `date_finished`) are kept as they are and never set by this skill.
- **paper.** Identity is `doi` and `citekey`, resolved against the actual paper and identical to its Raw; surname plus year is a search hint, never identity. A provisional citekey carries `citekeyProvisional: true`; a later registered key is recorded and the page is never renamed for it. Link the paper's Raw only when the vault has one; a paper researched from the web is cited by `doi` and a `[label](URL)` reference, and no Raw is created for it. `author` holds the paper's authors in source order.
- **product.** The README, documentation and release notes are evidence, not the page. A pinned repository link already carries its commit; label it plainly (`README`, `LICENSE`) and keep the sha out of prose.

## Step 5 — Link the work note

When the conversation is about a note in the work area, turn the first mention of the entity in that one note into `[[Entity]]` (or `[[Entity|original text]]`) and change nothing else. The note the conversation is about is one the user named or is working in; a note found only by searching the vault is not it, and no other name in it is linked. Open `principle-preserve-unrequested`.

## Step 6 — Read back and report

Open `principle-read-back` and read back every note written. Before the closing Wiki line, report each principle leaf that changed a decision and what it changed, any impressions note moved out, any type folder created, and any optional-type candidate awaiting approval. The final line is `Wiki: created [[X]], updated [[Y]]`, listing only wiki pages that actually changed, with any failure on the same line. Classify each page once by whether it existed before the task: fixing a page just created does not also make it updated, and a work-note link or a separate impressions note outside the wiki does not belong in this line.

Put all source links or a Sources list before the Wiki line, not after it. Nothing follows that line.
