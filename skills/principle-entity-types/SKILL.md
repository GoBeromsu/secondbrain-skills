---
name: "principle-entity-types"
description: "Apply when choosing an Entity's type, its template or the folder a new Entity goes into."
disable-model-invocation: true
license: MIT
---

# Entity types

The type decides the template and the folder, so it is settled before an Entity page is written.

| Type | What it is | Template |
| --- | --- | --- |
| `person` | a named human | [person](../entity/assets/person.md) |
| `organization` | a company, lab, team, school, government body | [organization](../entity/assets/organization.md) |
| `place` | a named location: venue, city, landmark | [place](../entity/assets/place.md) |
| `paper` | one scholarly work, identified by DOI and citekey | [paper](../entity/assets/paper.md) |
| `book` | one book work and edition | [book](../entity/assets/book.md) |
| `media` | a publisher that keeps putting things out: a YouTube channel, podcast, newsletter, blog | [media](../entity/assets/media.md) |
| `product` | named software, a service, a library, an agent, a model or a dataset | [product](../entity/assets/product.md) |
| optional | any other named individual: an event, a movie, an album, a game title | [other](../entity/assets/other.md) |

- One video, episode, issue or post is a Raw source, not an Entity; the `media` Entity that published it lists it.
- The vault's live policy decides each type's folder; this principle names types only. Creating or adding to an Entity inside an existing type folder needs no approval.
- A required type with no folder yet gets one without asking: first map it to the folder existing notes of that type or a synonym already use (`channel` → media, `people` → person), otherwise create one beside the existing Entity folders in their naming and numbering, and name it in the report for the owner to register.
- **A new folder for an optional type needs the owner's approval.** Name the type, the proposed folder and the Entities that would go there; without approval create nothing and list them as candidates.
- An update never moves or retypes an existing Entity; a move or a type correction needs the owner's own request.
- A template the vault registers for a type wins over the template here for frontmatter keys and headings, except that it never brings back an append-only zone (`## Wiki`, `## From Sources`).

The vault's live policy overrides any line here. This principle shapes a write the task already asked for; it is not a reason to make one, and not a reason to withhold one.
