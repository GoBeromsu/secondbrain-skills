# Terms

A Term page lets the owner understand a name a field uses: after reading it they know what the thing is, how it works and how it connects to what they already know. This file owns what becomes a Term, its title and its sections; `lint` reports existing pages against it.

## What is a Term

- Make a Term for a name an established field uses independently of this source, whether self-contained jargon (`ReplicaSet`) or a shared word whose meaning varies by field (`AI Agent`).
- Before writing, collect every sense the name has: its general-dictionary and encyclopedia senses, how vault notes already link or use it, and how the owner uses it; never take the source's field as the only one.
- Keep related senses on one page when one definition can state what they share (AI Agent: anything that perceives its environment and acts on it, covering the reinforcement learning agent and the LLM-based agent).
- Split unrelated meanings under one name into separate Terms (`Transformer (Machine Learning)`, `Transformer (Electrical Engineering)`).
- Make a named individual thing (a product, service, model, dataset or organization such as `OpenClaw` or `Claude Code`) an Entity and link it from the Term as an example.
- Keep a name only one author uses as a Concept until an independent source uses it.
- Give every Term `layer: terms`.

## Title

1. Title it with the full name in its original language, whichever language that is.
2. Append `(ACRONYM)` when the field uses an acronym: `Retrieval-Augmented Generation (RAG)`.
3. Add a parenthetical qualifier only when two unrelated Terms would otherwise share a title.
4. Put everything else in `aliases`: translations, other scripts, spelling variants, years, former and incorrect forms.
5. Use the correct current form; name an incorrect or former form found in `aliases` in `## Origin`.
6. Write no space directly after `(` or before `)`.

## Sections

Fill [term](../templates/term.md):

- **TL;DR:** in two sentences, state what every sense shares and the trade-off that makes the term matter. Record in `definitionStatus` whether that definition is `consensus`, `contested` or `emerging`; claim `consensus` only when the sources show agreement.
- **Explanation:** explain it for a reader meeting it for the first time, under `###` headings phrased as the reader's questions (what it changes, why it works, how it behaves as a parameter varies, what problem it solves). Write one idea per short sentence, put formulas in display math, show the worked example as a table, and bold the one sentence a reader must keep. Link each vault Term or Concept it relies on at first use instead of re-explaining it, and connect it to the owner's own notes and earlier queries the vault search returns.
- **Where It Is Used:** open with a table of field and what the term does there in one line, then one `###` per field with bold-labelled bullets of one use each, its citation at the line end, and the owner's own notes grouped under one bullet with short link labels; include it even for a single-sense term.
- **Origin:** write a paragraph on where the word comes from, its first documented use (who, where, when, cited from the primary source) and when each later sense appeared; add bullets only when a sequence needs them. Write an unknown point as unknown.
- **Senses:** add one `### {field}` section per sense only when the meaning varies by field, each with that field's definition, since when it is used that way, examples and its own typed relations; list those fields in `domain`.
- **Literature Review:** give one `### [[Author]] (year): what it adds` entry per source, walked up to the source that establishes the claim, with bold-labelled bullets.
- **Personal Insights:** leave the owner's own notes as they are.
- **Related Terms:** group links under labels in the page's language with the type in parentheses: broader (contains this term), narrower (a kind or variant of it), related split into what it is made of, other methods for the same problem and where it is used, and confused-with (often mixed up with it). Give each link one line saying why; state how a confused-with term differs. Never make one page both broader and related; put a relation that holds for one sense in that sense section.
- **References:** list each Raw with its author and role, then each of the owner's notes the page draws on.

When a relation or a numeric behavior is easier to see than to read (how senses derive from one another, how a parameter changes a trajectory), add a Pele diagram by `obsidian-visualize` beside the text that states it.

Keep a superseded definition with its date and source when adding a new one.

Link a Term as a whole page, never a heading inside it.
