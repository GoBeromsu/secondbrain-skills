# Frontmatter — single source

The destination's live policy wins wherever it defines a field, value or placement; this schema fills the rest. One meaning has one field.

## Writing rules

Key form (indentation, quoting, alphabetical order, `*_url` keys, `status`, unknown values) follows `principle-markdown`. In addition:

- `description` is English, one or two sentences, always double-quoted (`""` when empty).
- New keys are camelCase, except `*_url` keys, the date keys `date_created`, `date_modified`, `date_ingested`, `date_published` and `conversion_date`, and the kebab-case `source-attachment`, `source-format`, `conversion-tool`, `conversion-fidelity` and `superseded-by`.
- Only a book Entity with `## Reading Progress` carries `status` (the owner's reading status, never set or changed by ingest); chapter Raws track acquisition in their body callout.

## Required on every note (7) plus provenance

| Key | Value |
| --- | --- |
| `type` | role value from the table below |
| `aliases` | list of alternative names |
| `description` | English, double-quoted |
| `author` | list of quoted `"[[Name]]"` people (a missing target is no reason to create an Entity). Raw: the original author(s). Book and paper Entities: the work's authors in source order. Agent-written pages: the author live policy names, else the agent's role name (`Claude`, `Codex`, …). |
| `date_created` | creation date of this note |
| `date_modified` | last modification date of this note |
| `tags` | list |
| `model`, `effort` | on every agent-written page: the runtime-reported model id (a list when several contributed) and reasoning effort, `default` when unreported. Never fabricate a model. |

No `created_by` or `authorship` default; a vault whose policy defines its own provenance keys gets exactly those.

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

- Keep every existing key and value, unknown keys included. Ingest changes only `source`, `related`, `date_modified`, reviewed additions, Step 8's Entity reference links and the template migration in [updating](updating.md) (which also moves a legacy URL key such as `youtube` to its `*_url` key).
- A Persona append keeps every `source` item and appends this Raw, refreshes `effort`, and keeps prior `model` IDs in order while adding new ones once (scalar for one, list for several); `author` and Persona keys stay.
- Identity matching reads `source` first, then any other locator the note records, comparing a Markdown link's URL independent of its label. Titles never prove sameness.
- Any other key migration needs the owner's explicit authorization for named notes: keep a before-image, map a value only when its meaning is verified equivalent (`source_obtained_at` is not `date_ingested` without proof), stop and report on any conflict, and leave one key per meaning. A value still needed for identity, location or history is never dropped as legacy.
