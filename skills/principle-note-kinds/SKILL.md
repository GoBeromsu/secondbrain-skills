---
name: "principle-note-kinds"
description: "Apply when deciding what kind of wiki page a piece of knowledge is: Term, Concept, Guide or Entity, or whether it stays in Raw."
disable-model-invocation: true
license: MIT
---

# Note kinds

Each wiki page holds exactly one kind of knowledge, and the kind decides the template, the skill that writes it and how a reader finds it.

- **Term** only when the name is a real term of a field: it appears with the same meaning in that field's dictionaries, textbooks, standards, glossaries or peer-reviewed literature, independently of the selected source and of any one coiner (`ReplicaSet`, `AI Agent`, `Ikigai`). Written by `term`.
- **Concept** for a model, framework or method one author named, however widely cited (`Golden Circle`, `PARA`); reuse that still attributes the name to its coiner is popularity, not independence. Also for a reusable abstract idea, technique or pattern without an established field name (`LLM Wiki Pattern`). Written by `concept`.
- **Guide** for an executable ordered procedure, written only when the How-to was actually solved and confirmed in the conversation or came from an ingested How-to source. Guidance without an executable order stays with its Concept. A guide is a page kind, not a skill: it is written from `ingest`'s guide template.
- **Entity** for a named individual rather than the kind it exemplifies (`Claude Code`, not `coding agent`). A kind is never an Entity: a flower species or a genre is a Term or Concept. Written by `entity`.
- Keep related senses of one name in one Term when a shared definition covers them; separate unrelated meanings into Terms qualified by field (`Transformer (Machine Learning)`, `Transformer (Electrical Engineering)`).
- Keep a source-specific passage or argument as an attributed claim in the Term or Concept it concerns, never as a page title.
- Leave knowledge that fits none of these kinds in Raw and ask the owner before creating a page.
- Keep the levels distinct: Raw holds evidence, each wiki page holds one Term, Concept, Entity or Guide and cites its sources, and Maps group pages. Maps belong to `ingest`; no other writer creates one.

The vault's live policy overrides any line here. This principle shapes a write the task already asked for; it is not a reason to make one, and not a reason to withhold one.
