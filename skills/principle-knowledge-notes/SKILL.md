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

- Type an Entity by what it is: person, organization, place, paper, book, media (a publisher that keeps putting things out), product, or an optional type for any other named individual: an event, program, scholarship or award.
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

The guideline's own rules override any line here.
