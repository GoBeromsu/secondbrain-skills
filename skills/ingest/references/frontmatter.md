# Frontmatter — single source

The destination's live policy wins wherever it defines a field, value or placement; this schema fills the rest. One meaning has one field.

## Writing rules

- YAML frontmatter is indented with 2 spaces; the Markdown body with tabs.
- Wikilinks inside YAML are double-quoted: `"[[Name]]"`. Body wikilinks are bare.
- `description` is English, one or two sentences, always double-quoted (`description: ""` when empty).
- Dates are ISO 8601 (`YYYY-MM-DD`, time optional). An existing value keeps its form.
- Keys appear in alphabetical order on every note ingest writes, including Raws, as the vault's linter sorts them; `principle-frontmatter` holds the rule.
- Within the note kinds ingest handles, only a note in the vault's Entity folder with a book type and a `## Reading Progress` section may carry frontmatter `status`. Preserve an existing owner-maintained value from the live policy's book reading statuses; ingest never sets or changes it. Chapter Raws track acquisition in the body callout, not in frontmatter.
- External URLs on a wiki page sit only under `url` (the canonical homepage, or the repository of a product that has none) or a snake_case `*_url` key (`blog_url`, `instagram_url`, `linkedin_url`, `x_url`, `youtube_url`, and any other `*_url` key the vault's properties define, such as `feed_url` or `source_url`) as plain URLs; every other web reference goes in the body as `[label](URL)`.
- New keys are camelCase, except the `*_url` keys above, the snake_case date keys below and these kebab-case keys (`source-attachment`, `source-format`, `conversion-tool`, `conversion-fidelity`, `superseded-by`). The snake_case date keys are exactly `date_created`, `date_modified`, `date_ingested`, `date_published` and `conversion_date`; the verification timestamps are `exploredDate` and `verifiedAt`.
- Unknown applicable metadata stays unknown, never invented. An inapplicable optional key is omitted.
- Fill every slot as a value serialized by YAML's own rules, never by pasting raw text. A person name containing `"` or `\` inside a double-quoted `"[[Name]]"` follows YAML double-quoted escaping (`\"`, `\\`). Emit lists as YAML lists, one item per existing value; never collapse several existing items into one string.
- A Persona's `source` keeps every existing item as a separate list item and appends this Raw.

## Required on every note (7) plus provenance

| Key | Value |
| --- | --- |
| `type` | role value from the table below |
| `aliases` | list of alternative names |
| `description` | English, double-quoted |
| `author` | list. People are quoted wikilinks `"[[Name]]"` whether or not that note exists; a missing target alone is not a reason to create an Entity; SKILL Step 6 decides which Raw authors get one. Raw: the original author(s). Book and paper Entities: the work's authors as quoted wikilinks, in source order. Wiki and other agent-written pages: the author the live policy names, otherwise the writing agent's role name (`Claude`, `Codex`, …). |
| `date_created` | creation date of this note |
| `date_modified` | last modification date of this note |
| `tags` | list |
| `model`, `effort` | on every agent-written content page, in alphabetical order with the other keys: the runtime-reported model id (a list when several contributed) and reasoning effort, `default` when unreported. Never fabricate a model. |

No `created_by` or `authorship` default. A vault whose live policy defines its own provenance keys (for example `created_by`) gets exactly those values from that policy; never infer them.

## Roles

| Role | type | layer | status | Template |
| --- | --- | --- | --- | --- |
| Raw Source | `raw-source` | — | — | [raw](../assets/raw.md) |
| Book chapter (Raw) | `raw-source` | — | — | [book chapter](../assets/book-chapter.md) |
| Term | `wiki-page` | `terms` | — | [term](../../term/assets/term.md) |
| Concept | `wiki-page` | `concepts`; `theory`, `method` or `scale` for a paper-derived Concept | — | [concept](../../concept/assets/concept.md) |
| Entity | live policy | `entities` when typed `wiki-page` | owner-maintained reading status only on a book Entity with `## Reading Progress` | Its type template in `../../entity/assets/` and the rules in `entity`. |
| Guide | `wiki-page` | `guides` | — | [guide](../assets/guide.md) |
| Map | `moc` | — | — | live Map template |
| Persona | `persona` | — | — | [persona](../assets/persona.md) |

`category` names the Raw kind: `Articles`, `Papers`, `Books`, `Transcripts`, `Clippings` or `AI Research`, plus any value the destination's live policy registers for its own Raw lanes (for example a personal `Mail` lane). It selects the Raw folder of the same kind in the destination. Never invent a value the live policy does not list.

## Raw Source keys

| Meaning | Key | Notes |
| --- | --- | --- |
| Original address or reference | `source` | Canonical URL or reference. A capture bundle with several member URLs keeps them as a list. |
| Kind | `category` | One of the six values above or a value the live policy registers. |
| Acquisition date | `date_ingested` | When the source was taken into the vault; for a chapter stub, the scaffold date. |
| Publication date | `date_published` | The original's own date when known (Web Clipper `published`). |
| Language | `language` | The source's language code, such as `en` or `ko`. |
| Length | `length` | The source's size as stated or counted, such as `12 pages` or `3,400 words`. |
| Collection purpose | `collectionPurpose` | The owner's answer verbatim, or the stated inference and its reason when the owner delegated it. |
| Related notes | `related` | Quoted wikilink list of existing notes from Step 2; `[]` when none. |
| Originals and earlier captures | `referenced` | List. A wikilink when the original or earlier capture is already a Raw or Entity in the vault, otherwise its canonical URL. It records where a claim came from; it never proves the original was read and never authorizes fetching it. |
| Retained document | `source-attachment` | `"[[original-filename]]"` of the binary moved into the attachments folder. |
| Converted format | `source-format` | `pdf`, `pptx`, `docx`, `hwp`, `hwpx`, … |
| Converter | `conversion-tool` | `markitdown`, `pandoc`, `hwp5txt`, `defuddle`, `hwpx-xml`, … |
| Conversion date | `conversion_date` | Date of the conversion. |
| Conversion fidelity | `conversion-fidelity` | `high`, `medium` or `low`. |
| Newer version | `supersedes` / `superseded-by` | Source Update, major change: new `-v2` Raw points back with `supersedes`; the earlier Raw gains `superseded-by`. |
| Paper | `citekey`, `doi`, `citekeyProvisional` | Paper Raw; same `citekey` and `doi` as the paper Entity; `citekeyProvisional: true` only for a generated key. |
| Book chapter | `book`, `chapterNumber`, `chapterPart`, `chapterPrev`, `chapterNext` | Chapter Raws: quoted wikilink to the book Entity, integer, original-language part name, quoted wikilinks or `null` at the ends. |

## Wiki page keys

| Meaning | Key | Notes |
| --- | --- | --- |
| Evidence | `source` | Quoted Raw wikilinks, plus other inspected evidence allowed by the selected template and live policy. Append newly used sources and keep earlier entries. |
| Related knowledge | `related` | Quoted wikilink list. |
| Confidence | `confidence` | `high` (well-sourced), `medium` (partial), `low` (speculative). A page resting only on secondary claims is not well-sourced. |
| Reuse unit | `layer` | Per the Roles table. |
| Field | `domain` | Term only: fields of use; see the [Term template](../../term/assets/term.md) for their format. |
| Definition status | `definitionStatus` | Term only: `consensus`, `contested` or `emerging`. |
| Exploration gate | `explored` | `false` on every new page; `true` only after a human read it or a source-backed review loop verified it, with optional `exploredBy`, `exploredDate`. |
| Verification state | `verificationStatus` | `unverified` on every new page; `verify` sets `verified`, `partial`, `unverified` or `disputed` with `verifiedAt`, `verifiedBy`. |
| Claim classification | `claimType`, `evidenceScope` | Optional at ingest; record only when the classification is clear. `claimType`: `definition`, `empirical`, `theoretical`, `historical`, `prescriptive`, `interpretive` or `mixed`. `evidenceScope`: `single-source`, `multi-source-primary`, `multi-source-mixed`, `synthesis-only` or `user-original`. |
| Conflict | `disputed` | Set only by `verify`; `audit` only queues it, ingest never sets it. |
| Persona | `personaOf`, `personaMaturity`, `personaDomains` | Persona only; ingest never changes `personaMaturity`. |
| Paper | `citekey`, `doi` | Paper Entity only; see [papers](papers.md). |
| Map | `topic`, `related` | Map only. |

## Existing notes and migration

New notes use the schema above. A run that touches an existing note preserves what it already holds.

- Keep every existing key and value, including unknown keys and earlier identity, location and history values. Ordinary ingest changes only the keys its update names (`source`, `related`, `date_modified` and additions the preservation review accepted, plus the template migration on touch [updating](updating.md) defines for every page ingest revises, which also moves a legacy URL key such as `youtube` or `x` to its `*_url` key); it renames, re-forms, copies or removes nothing else, date keys and `author` values included, except ingest Step 8's Entity reference links.
- For a Persona append, also refresh `effort` to the contributing runtime's reported effort (`default` when unreported), and preserve prior `model` IDs in order while adding newly reported contributing model IDs once each. Use a scalar for one ID, a list for several, and `default` only when no model ID is known. This provenance update leaves `author` and all Persona-specific properties unchanged.
- Identity matching reads `source` first, and any other source address or locator the existing note already records; compare the destination URL of a Markdown link with a bare URL independent of its display label. Titles never prove sameness. Ingest requires no identity key beyond this schema.
- Key migration runs only when the owner explicitly authorizes it for named notes, apart from the template migration on touch that [updating](updating.md) defines for a page `term`, `concept`, `entity` or `ingest` revises. Record each note's before-image first; map a value only when its meaning is verified equivalent to the target key (`source_obtained_at` is not `date_ingested` without proof that both record the same acquisition); stop on any conflict, such as a target key already holding a different value or an ambiguous meaning, and report it. A completed migration leaves one key per meaning, with no permanent dual keys. A value still needed for identity, location or history is never dropped merely as legacy.
