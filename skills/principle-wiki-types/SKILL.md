---
name: "principle-wiki-types"
description: "Classifies Wiki knowledge as Term, Concept, Entity, Guide, a claim within a page or evidence kept in Raw. Use for page-type decisions or corrections, term인지 concept인지, 이건 무슨 페이지야. Creating the page belongs to ingest."
license: MIT
---

# Wiki page types

- Classify a name with a field-shared meaning used independently of the selected source as a Term (`ReplicaSet`, `AI Agent`).
- Classify a reusable abstract idea, technique, method or pattern without an established field name as a Concept, whether or not the source names it (`LLM Wiki Pattern`, `비대칭 동업`).
- Keep a name only one author uses as a Concept until an independent source uses it.
- Classify a named individual person, organization, product, service, model or dataset as an Entity rather than the kind it exemplifies (`OpenClaw`, `Claude Code`).
- Classify an executable ordered procedure as a Guide.
- Keep guidance without an executable order with the Concept it belongs to.
- Keep related senses of one name in one Term when a shared definition covers them (`AI Agent`: anything that perceives its environment and acts on it, covering the reinforcement learning agent and the LLM-based agent).
- Separate unrelated meanings of the same name into different Terms (`Transformer (Machine Learning)`, `Transformer (Electrical Engineering)`).
- Keep a source-specific passage or argument as an attributed claim in the Term or Concept it concerns, never as a page title.
- Leave knowledge that fits none of these kinds in Raw and have the task that found it ask the owner before creating a page.
- Keep the levels distinct: Raw holds evidence, each Wiki page holds exactly one Term, Concept, Entity or Guide and cites its Raws, and Maps group pages.
- Hand page creation to `ingest` under the destination vault's live policy and the user's authorization; this principle performs no write.
