---
name: "principle-knowledge-notes"
description: "Decides what kind of knowledge note something is and what shape it takes: Term, Concept, Guide or Entity (person, organization, place, paper, book, media, product), with a template for each, plus claims within a page and evidence kept in Raw. Use for page-type decisions or corrections (is this a Term or a Concept, is this channel an Entity, which template does a book note use) and whenever a page is written from a template. A folder for an optional Entity type is never created without the owner's approval. Creating the page belongs to ingest."
license: MIT
---

# Knowledge notes

This principle owns two things: which kind a piece of knowledge is, and the shape of its page. It writes nothing; `ingest` creates and updates pages under the destination vault's live policy and the owner's authorization.

## Kinds

- Classify a name as a Term only when it is a real term of a field: it appears with the same meaning in that field's dictionaries, textbooks, standards, glossaries or peer-reviewed literature, independently of the selected source and of any one coiner (`ReplicaSet`, `AI Agent`, `Ikigai`).
- Classify a model, framework or method that one author named as a Concept, however widely it is cited (`Golden Circle`, `PARA`). Reuse that still attributes the name to its coiner is popularity, not independence.
- Classify a reusable abstract idea, technique, method or pattern without an established field name as a Concept, whether or not the source names it (`LLM Wiki Pattern`, `Asymmetric Partnership`).
- Classify an executable ordered procedure as a Guide. Keep guidance without an executable order with the Concept it belongs to.
- Classify a named individual as an Entity rather than the kind it exemplifies (`Claude Code`, not `coding agent`). A kind is never an Entity: a flower species or a genre is a Term or Concept even when the vault files it near Entities.
- Keep related senses of one name in one Term when a shared definition covers them (`AI Agent`: anything that perceives its environment and acts on it, covering the reinforcement learning agent and the LLM-based agent).
- Separate unrelated meanings of the same name into different Terms (`Transformer (Machine Learning)`, `Transformer (Electrical Engineering)`).
- Keep a source-specific passage or argument as an attributed claim in the Term or Concept it concerns, never as a page title.
- Leave knowledge that fits none of these kinds in Raw and have the task that found it ask the owner before creating a page.
- Keep the levels distinct: Raw holds evidence, each Wiki page holds exactly one Term, Concept, Entity or Guide and cites its Raws, and Maps group pages.

## Entity types

Seven Entity types are required; each has its own template under `templates/entity/`:

| Type | What it is | Template |
| --- | --- | --- |
| `person` | a named human | [person](templates/entity/person.md) |
| `organization` | a company, lab, team, school, government body | [organization](templates/entity/organization.md) |
| `place` | a named location: venue, city, landmark | [place](templates/entity/place.md) |
| `paper` | one scholarly work, identified by DOI and citekey | [paper](templates/entity/paper.md) |
| `book` | one book work and edition | [book](templates/entity/book.md) |
| `media` | a publisher that keeps putting things out: a YouTube channel, podcast, newsletter, blog | [media](templates/entity/media.md) |
| `product` | software, a service, a model or a dataset | [product](templates/entity/product.md) |

- One video, episode, issue or post is a Raw source, not an Entity; the `media` Entity that published it lists it.
- Any other named individual (an event, a movie, an album, a game title) is an optional type and uses the [common Entity template](templates/entity.md).
- This principle names types only. The vault's live policy decides each type's folder.
- **A new folder for an optional type needs the owner's approval.** Creating or adding to an Entity inside an existing type folder needs no approval, and a required type with no folder yet gets one without asking: first map it to a folder existing notes of that type or a synonym already use, otherwise create one beside the existing Entity type folders in their naming and numbering, and the report names it for the owner to register. When an optional type has no folder yet, ask the owner before creating one: name the type, the proposed folder and the Entities that would go there. Without approval, create nothing and list them as candidates in the run report.

## Entity pages belong to the owner

An Entity is the owner's note about something in their life. The agent adds to it; it never takes it over.

- **Two zones.** Every Entity template has an owner zone on top and an auto zone at the bottom, starting at `## From Sources`.
	- The owner zone holds the type's headings, left empty for the owner. Never write, reorder or rephrase anything there.
	- The auto zone holds source-grounded additions: dated facts and mentions, each with its Raw, plus `### Sources` and `### Related`. Add only; never edit or remove an earlier line.
	- When the live policy names its own section for agent-written Entity content (for example `## Wiki`), that section is the auto zone, kept in its existing sub-structure under the same append-only rules.
	- In frontmatter, keep every owner key and value. Append to `source`, `related` and `aliases`, and update `date_modified`.
- An existing Entity with neither heading gets `## From Sources` appended at the end of its body the first time an addition lands. Existing Entities are never converted, moved or retyped in bulk, and a missing auto zone is not a defect.

## Templates

| Kind | Template |
| --- | --- |
| Term | [term](templates/term.md) |
| Concept | [concept](templates/concept.md) |
| Guide | [guide](templates/guide.md) |
| Entity, optional type | [entity](templates/entity.md) |
| Entity, required type | `templates/entity/{type}.md` |

When the destination vault registers its own template for a kind or type, the vault's template wins for frontmatter keys and owner headings; the auto-zone and approval rules above still apply. Raw, book chapter and Persona templates belong to `ingest`.
