---
name: "principle-knowledge-notes"
description: "Apply whenever knowledge is about to become a wiki page: deciding whether it is a Term, Concept, Guide or Entity or stays in Raw, choosing an Entity's type, template or folder, and deciding whether a write may land in a folder at all, since the vault's wiki, source and work areas each allow different writes. Use it before creating, moving or retyping any page."
disable-model-invocation: true
license: MIT
---

# Knowledge notes

Each wiki page holds exactly one kind of knowledge, and the kind decides the template, the skill that writes it and how a reader finds it. The area a note sits in decides who may write it.

## Note kinds

- **Term** only when the name is a real term of a field: it appears with the same meaning in that field's dictionaries, textbooks, standards, glossaries or peer-reviewed literature, independently of the selected source and of any one coiner (`ReplicaSet`, `AI Agent`, `Ikigai`). Written by `term`.
- **Concept** for a model, framework or method one author named, however widely cited (`Golden Circle`, `PARA`); reuse that still attributes the name to its coiner is popularity, not independence. Also for a reusable abstract idea, technique or pattern without an established field name (`LLM Wiki Pattern`). Written by `concept`.
- **Guide** for an executable ordered procedure, written only when the How-to was actually solved and confirmed in the conversation or came from an ingested How-to source. Guidance without an executable order stays with its Concept. A guide is a page kind, not a skill: it is written from `ingest`'s guide template.
- **Entity** for a named individual rather than the kind it exemplifies (`Claude Code`, not `coding agent`; `Fulbright Program`, not `scholarship`). A kind has members rather than one history, so it is a Term or Concept, never an Entity. Written by `entity`.
- The owner's "term", "concept" or "entity" asks for a page, not for its kind. When these criteria give another kind, name the kind that fits and why, and ask once before writing.
- Keep related senses of one name in one Term when a shared definition covers them; separate unrelated meanings into Terms qualified by field (`Transformer (Machine Learning)`, `Transformer (Electrical Engineering)`).
- Keep a source-specific passage or argument as an attributed claim in the Term or Concept it concerns; as a page title it would split one subject across many pages.
- Leave knowledge that fits none of these kinds in Raw and ask the owner before creating a page.
- Keep the levels distinct: Raw holds evidence, each wiki page holds one Term, Concept, Entity or Guide and cites its sources, and Maps group pages. Maps belong to `ingest`; no other writer creates one.

## Entity types

The type decides the template and the folder, so it is settled before an Entity page is written.

- Type an Entity by what it is: person, organization, place, paper, book, media (a publisher that keeps putting things out), product, event (a named happening or programme with a time, one-off or recurring: a hackathon, a scholarship, an award round), or an optional type for any other named individual: a movie, an album, a game title.
- One video, episode, issue or post is a Raw source, not an Entity; the media Entity that published it lists it.
- An update leaves an Entity's folder and type alone: the owner chose them, and a move breaks links. Moving or retyping is the owner's call.
- A folder for a new optional type needs the owner's approval.

The type table and folder steps are in `entity` Step 1.

## Vault roles

A vault has three areas with different owners. The vault guideline (its AGENTS file or the policy note it names, the live policy) says which folders play each role; read it there, because vaults name their folders differently. When the guideline is silent, `onboard` asks the owner once and records the answer in it.

| Role | What it holds | What a skill may write there |
| --- | --- | --- |
| wiki | compiled pages: Terms, Concepts, Entities, Guides, Maps | create, revise, overwrite and delete freely |
| source | Raw captures of what the owner handed over | only when the owner hands material over and asks to ingest or save it: a new Raw, or `ingest`'s own metadata update, stub promotion or appended evidence on an existing Raw; captured text never changes |
| work | the owner's own notes, projects, logs and permanent notes | nothing in a note marked `authorship: user`; otherwise, in the one note the conversation is about, turn the first mention of a term that now has a page into a `[[wikilink]]`, and nothing more |

- A web page read while answering a question or researching a word stays a `[label](URL)` link on the wiki page. Raw is for what the owner handed over, so it does not become a Raw.
- In the work area add no sentence or section, and leave every other note alone. The one exception is the `entity` skill moving the owner's own impressions off a person Entity into a new note in the permanent-notes folder the guideline names, sentences unchanged.
- A wiki Entity with `authorship: user` may still be revised: set it to `authorship: mixed` and keep every sentence the owner wrote unchanged.

## Writing one page

`term`, `concept` and `entity` share these steps around their own research and template. The answer the user asked for comes first; the page is written after, and the report names it.

- **Roles.** Read the live policy for the wiki, source and work folders and the folder this kind goes into. When a mapping the run needs is missing, stop before writing and run `onboard`'s Vault roles step, which asks the owner once and records the answer; never guess a folder. A subagent returns the missing mappings to the main thread, which asks once for all of them.
- **Lookup.** Search each title, alias, translation and spelling variant with `obsidian search query=<name>`, and an existing page with `obsidian backlinks path=<page>`, always with `vault=<resolved vault>` as [`obsidian-cli`](../obsidian-cli/SKILL.md) requires; an untargeted command reads whatever vault or note has focus. An existing page or alias for the same referent is updated, never duplicated, by [updating](../ingest/references/updating.md): the run adds only claims the page does not carry.
- **Title.** The full name in its original language, followed by the common abbreviation in parentheses when one is in use (`Getting Things Done (GTD)`); abbreviations, translations, former names and spelling variants go in `aliases`.
- **Form.** A template the vault registers for the kind wins for frontmatter keys and headings. English section headings, in the template's order. About five subject tags; `source` lists vault notes as quoted wikilinks.
- **Entity links.** Before writing and again at read-back, scan the draft for the titles and aliases of vault entities, including comparisons, tables, quotations, Personal Insights, references and footnotes, and link each confirmed one once at its first eligible body mention; a link in a source note or in this page's frontmatter does not count, and checking that existing links resolve does not catch missing ones. When search is unavailable, follow other notes' wikilinks with direct reads and confirm candidates in the Entity folders the live policy registers. Quoted words stay as written, so an entity named only inside a quotation is linked once in your own prose beside it (`[[Trial Note]] records the owner's question about [[Product]]: "…"`).
- **Work note.** When the conversation is about a note in the work area (one the user named or is working in; a note found only by searching is not it), turn the first mention of the page's subject in that note into `[[Page]]` or `[[Page|original text]]` and change nothing else; no other name in it is linked.
- **Report.** Read back every note written, as `principle-editing` describes. Standalone, put the skill's listed findings and decision-changing principles before the footer; routed through `secondbrain-mode`, return findings and wiki outcomes separately instead. The standalone final line is `Wiki: created [[X]], updated [[Y]], failed [[Z]] (reason)`, omitting empty clauses. It holds only read-back-confirmed changes in the live policy's wiki area, each page once by whether it existed before the task; `failed [[Z]] (reason)` only for an attempted wiki write that failed. Unattempted work, Raw and other outside-wiki notes, work-note links included, stay out. No wiki writes and no failures: no line. Nothing follows it.

The guideline's own rules override any line here.
