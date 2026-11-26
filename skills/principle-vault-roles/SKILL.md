---
name: "principle-vault-roles"
description: "Apply when deciding whether and how a write may land in a folder: the vault's wiki, source and work areas each allow different writes."
disable-model-invocation: true
license: MIT
---

# Vault roles

A vault has three areas with different owners. The vault guideline (its AGENTS file or the policy note it names, the live policy) says which folders play each role; read it there and never assume a folder name. When the guideline is silent, `onboard` asks the owner once and records the answer in it.

| Role | What it holds | What a skill may write there |
| --- | --- | --- |
| wiki | compiled pages: Terms, Concepts, Entities, Guides, Maps | create, revise, overwrite and delete freely |
| source | Raw captures of what the owner handed over | only when the owner hands material over and asks to ingest or save it: a new Raw, or `ingest`'s own metadata update, stub promotion or appended evidence on an existing Raw; captured text never changes |
| work | the owner's own notes, projects, logs and permanent notes | nothing in a note marked `authorship: user`; otherwise, in the one note the conversation is about, turn the first mention of a term that now has a page into a `[[wikilink]]`, and nothing more |

- A web page read while answering a question or researching a word stays a `[label](URL)` link on the wiki page. It never becomes a Raw.
- In the work area add no sentence or section, and leave every other note alone. The one exception is the `entity` skill moving the owner's own impressions off a person Entity into a new note in the permanent-notes folder the guideline names, sentences unchanged.
- A wiki Entity with `authorship: user` may still be revised: set it to `authorship: mixed` and keep every sentence the owner wrote unchanged.
- The guideline's own rules override any line here.
