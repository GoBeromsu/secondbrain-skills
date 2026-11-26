---
name: "entity"
description: "Apply when the user shows interest in a specific named thing (not a kind or a method): a product, tool, library or model, a person, an organization, a place, a book, a paper, or a channel, podcast or newsletter. Research it and write or update its Entity page in the wiki from the template for its type. Also use when the owner asks to add, record or update a note on one named person, company, product, book, paper, place, event or program, or brings news about one; a kind or method the owner labels an Entity is handed off, not written as one. Material the owner hands over to compile, such as a paper's PDF or an article, belongs to ingest; a request to save it without compiling belongs to capture."
license: MIT
---

# Entity

Research one identifiable thing and leave the wiki with one Entity page that tells the owner what a source alone cannot: what it is, where it came from, how it really works, and what their own records show about it. Every type is one sourced synthesis, rewritten as evidence grows, with no append-only zone. Open each principle named at a step by reading `../<principle>/SKILL.md` before acting on that step; `principle-knowledge-notes`' Writing one page governs roles, lookup, title, form, entity links, the work note and the report.

## Step 1 — Resolve the type, the vault roles and the target

Open `principle-knowledge-notes` and `principle-editing`. Confirm by the principle's criteria, not the owner's label, that the thing is one named individual; when it is a kind (a Term or Concept), name that kind and why, and ask once before writing. Then pick the type and its template.

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

A registered template never brings back an append-only zone (`## Wiki`, `## From Sources`).

Resolve the roles and the permanent-notes folder. The live policy decides each type's folder, and adding to an existing type folder needs no approval. A required type with no folder gets one without asking: the folder existing notes of that type or a synonym already use (`channel` → media, `people` → person), otherwise a new one beside the existing Entity folders in their naming and numbering, named in the report for the owner to register. For an optional type with no folder, name the type, the proposed folder and its Entities and ask; without approval create nothing and list them as candidates.

## Step 2 — Look the entity up in the vault

Look it up as the principle describes, adding handles and identifiers (ISBN, DOI, citekey, repository) to the names. Updating an existing page, open `principle-writing`; when the run only brings news, add just the new claims.

## Step 3 — Gather before writing

One source rarely carries all the page needs, so collect evidence first and write second. Open `principle-archival`.

- **The maker's or subject's own account.** Beyond what triggered the page, read their own pages for origin and mechanism: an about or history page, the documentation of the feature the owner cares about, release notes for what changed; for a repository, the README and the files that carry the claim at one commit. When a page that should carry the origin could not be found, say which was sought instead of stretching one source.
- **The owner's record.** Search the whole vault for the name and aliases, not only the notes the request names: daily and periodic notes, project notes, essays, meeting notes. Read each hit in context and note its date; mentions scattered over years are where a change of view lives.
- **The limits.** For each claim, note what its evidence does not establish: a maker's retrospective is not independent research, a documented rule is not a measured effect.

## Step 4 — Write the page

Fill the type's template. Open `principle-writing` and `principle-markdown`.

- Title a person with the real name a source confirms, in its original language and script; never infer one. When none is confirmed, report it rather than presenting an alias as a real name. Handles and romanizations go in `aliases`.
- When the live policy names `layer: entities` for Entities or types them `wiki-page`, a new page also gets the wiki-page fields of the [frontmatter contract](../ingest/references/frontmatter.md): `layer: entities`, `explored: false`, `confidence` and `verificationStatus: unverified`. An existing page keeps its own `explored`, `confidence` and `verificationStatus`.
- External URLs follow `principle-markdown`'s `*_url` rule, with `feed_url` and `source_url` as the vault's properties define them. Omit unknown slots; never write a bare `url` on a product, even when a registered template still lists it.
- Updating an older product, move its `url` by that host rule only when the value is a plain URL and the destination key is absent; otherwise leave it and report why. Older keys (`youtube`, `x`, `linkedin`, `website`, `feedUrl`, `repository`) move only a URL with the same meaning; a bare handle or conflicting value stays and is reported.
- Channels and profiles are frontmatter keys, never a list in the body.
- TL;DR's bold phrase says why it matters to the owner's work; on a person, the fact that matters most.
- Origin separates the maker's or subject's account (who, when, background, the problem they said prompted it) from what it is today.
- Explanation opens with one concrete worked example and follows the mechanism or work the owner depends on. Bold the one reading a newcomer usually gets wrong. Date changing features, prices, roles and versions.
- Personal Insights goes under `###` headings named for a theme or judgment, never a dated list of mentions. Each paragraph cites its records, quotes the owner's sentence where it carries the judgment, and keeps an earlier view beside the later one that replaced it. A conclusion no record states is labelled interpretation. With no owner record, say so in one sentence.
- One named footnote per source passage, reused, with its locator and, where it changes how the claim reads, the limit of that evidence.

## Type rules

- **person.** The body holds only sourced facts and `## Updates`; there is no Personal Insights. News goes under `## Updates` as dated lines, newest last: `- [[YYYY-MM-DD]] {fact} — [label](URL)` or `— [[Raw]]`. Impressions the owner wrote do not live on the entity: move them, sentences unchanged, into a new note in the permanent-notes folder named `{date_created} {Name}`, with the person page's `date_created`, `authorship: user` and `related: "[[{Name}]]"`; the person page's `related` then links it back. This is the one permitted new note in the work area.
- **organization.** The name it uses for itself. A branch with its own address is its own Entity; a product it makes, a channel it runs and a place it occupies are separate Entities, linked.
- **place.** The name in local use, qualified by area when shared. A trip or itinerary is not a place; the organization that runs it is its own Entity.
- **media.** One video, episode, issue or post is a Raw listed under `## Published`. The person or organization behind it is its own Entity in `operators`; a channel never replaces its operator's page.
- **book.** Identity is the work and edition: search by ISBN, author, translator, publisher and edition before creating; a translated or alternate title alone is not a different work, and editions are separate Entities, never merged silently. For a classic, distinguish the recognized local title, the original-language title, the translator and the edition. Set bibliographic keys only from the bookstore or publisher page, and label each Bibliographic Record line `observed`, `inferred` or `owner`, the cover included. Keep the table of contents in original order and language with its source; an empty one is unfinished work. Chapter Raws go under `## Chapters`, progress as appended dated lines whose latest line per chapter is its state. `## Highlights` is filled only by the owner or a highlight-sync tool. Never set or change `bookstore`, `date_started`, `date_finished` or `status`; `status` stays only on a book in a registered Entity folder of the live policy's book type with a real `## Reading Progress` heading.
- **paper.** Identity is `doi` and `citekey`, resolved against the actual paper and identical to its Raw; surname plus year is a search hint, never identity. A provisional citekey carries `citekeyProvisional: true`; a later registered key is recorded and the page is never renamed for it. Link the paper's Raw only when the vault has one; a paper researched from the web is cited by `doi` and a `[label](URL)` reference, and gets no Raw.
- **product.** The README, documentation and release notes are evidence, not the page. A pinned repository link already carries its commit; label it plainly (`README`, `LICENSE`) and keep the sha out of prose.

## Step 5 — Link the work note

Link the entity from the work note as the principle describes. Open `principle-editing`.

## Step 6 — Read back and report

Read back and report as the principle describes. Before the footer, list source links, any impressions note moved out, type folders created and optional-type candidates awaiting approval; the impressions note stays out of the footer.
