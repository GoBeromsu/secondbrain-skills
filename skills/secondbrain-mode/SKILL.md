---
name: "secondbrain-mode"
description: "Turns a conversation into knowledge accumulation: while on, new words, methods and named things the user meets are written into the vault's wiki by background subagents, and each answer ends with one line naming the pages written. Use for /secondbrain-mode or a request to turn secondbrain mode on or off."
disable-model-invocation: true
license: MIT
---

# Secondbrain mode

Every conversation is a chance to grow the owner's wiki. In this mode the main answer stays exactly what the user asked for, and the wiki work happens beside it in the background, reported in one line at the end.

Bundled skills live at `../<name>/SKILL.md` from this file. Put this file's absolute path in every subagent kickoff.

## On and off

The mode is on from the message that invokes it until the session ends or the user turns it off ("secondbrain mode off", "stop writing to the wiki"). While on, apply the triggers below to every user message without being asked again.

## Triggers

| The user | Skill |
| --- | --- |
| asks about a word they do not know | `term` |
| explores a new methodology | `concept` |
| shows interest in a specific product, person or organization | `entity` |
| hands over a paper or an article | `ingest` |
| asks about something they studied before | `query` |
| doubts something the wiki already says | `verify` |

- A word counts as unknown when the user asks about it or newly uses it and the wiki has no page or alias for it. When a page or alias exists, the skill only adds new claims to it.
- Handing over means giving the material itself and asking to keep, save or ingest it; that request is what lets `ingest` save a Raw, so the kickoff quotes it verbatim. A link mentioned in passing is not a handover: its new words go to `term`, `concept` or `entity`, and the link stays a `[label](URL)` on their pages. An explicit request to save without compiling does not trigger `ingest`.
- A How-to solved and confirmed in this conversation becomes a Guide page (a page kind, see `principle-note-kinds`), written by `ingest` Step 6's Guide rule from its [guide](../ingest/templates/guide.md) template; an unsolved How-to gets none.
- The mode never creates a Map (MOC). Maps are made and updated by `ingest`'s Connect step, and `lint` reports pages a Map misses.

## Running a trigger

1. Start one background subagent per triggered page with the runtime's subagent tool, before answering. Its kickoff names the skill's absolute path (`<this folder>/../<skill>/SKILL.md`) to read first, the vault root, the word or thing, what the conversation established about it, the user's request verbatim, and the work note the conversation is about, if any. Write the kickoff so it does not rely on any inherited conversation history. One writer per page: when two triggers would touch the same page or the same work note, give it to one subagent, and let `ingest` win over `term`, `concept` and `entity` for a handed-over source.
2. Each subagent returns the pages it created or updated, any failure with its reason, any vault-role mapping it found missing, and each principle leaf that changed a decision with what it changed.
3. Answer the user while the subagents work. For `query`, wait for its subagent's cited answer and give that. The answer carries no narration of wiki work, apart from naming the principles that changed a decision.
4. Write areas follow `principle-vault-roles`: free writes in the wiki area; a Raw in the source area only when the user handed material over and asked to ingest or save it, so web pages read along the way stay `[label](URL)` links; in the work area only the first mention, in the one note under discussion, becomes a `[[wikilink]]`.
5. When a subagent returns a question only the owner can answer (a missing vault-role mapping, `ingest`'s collection purpose), ask all of them once at the end of the answer. Record mapping answers through `onboard`'s Vault roles step and read the guideline back, pass a purpose answer verbatim, then restart the waiting writes.
6. Before the answer ends, collect every subagent started for it and close with one line: `Wiki: created [[X]], updated [[Y]], failed [[Z]] (reason)`. Omit the line when nothing was written or attempted.

## Model routing

Two tiers, named by role rather than vendor; the runtime maps each to its own models.

- **Strong model** for judgment and writing: classifying a page, researching, writing or revising a page, preservation review, verification.
- **Fast, weaker model** for mechanical work: searches and lookups, link retargeting, frontmatter key moves, batch cleanup, read-back checks.

## Principles

Read a leaf at `../<leaf>/SKILL.md` in full when its line applies, and in the answer name each principle that changed a decision and what it changed. Cite only leaves read this session.

**Vault and target**

- **principle-vault-roles.** Apply when deciding whether and how a write may land in a folder: the vault's wiki, source and work areas each allow different writes.
- **principle-resolve-target.** Apply when about to write to a vault note: the vault root, the target note, the effect and the authority must each be stated exactly before the write happens.
- **principle-preserve-unrequested.** Apply when editing an existing note: change only what the task asked for and keep everything else byte-identical.
- **principle-read-back.** Apply when a write to a vault note has just finished, before reporting it done or linking to it.

**Records**

- **principle-provenance.** Apply when attributing a claim, tracing who made a source, or a source is reposted, aggregated or quotes another creator's work.
- **principle-original-order.** Apply when capturing or touching a source's text: chapter order, message chronology, document structure or an existing Raw capture, and whenever tempted to reorder, tidy or replace captured text.
- **principle-hierarchy.** Apply when placing a newly captured or created note, or linking an item such as a chapter or a capture to the larger whole it belongs to.
- **principle-collective-description.** Apply when writing a hub, index or aggregate note whose single records cannot explain the scope, structure or history of their collection.

**Pages**

- **principle-note-kinds.** Apply when deciding what kind of wiki page a piece of knowledge is: Term, Concept, Guide or Entity, or whether it stays in Raw.
- **principle-entity-types.** Apply when choosing an Entity's type, its template or the folder a new Entity goes into.
- **principle-revise-and-consolidate.** Apply when updating a wiki page that already exists, including one found by an alias: Term, Concept, Guide or Entity of any type.
- **principle-not-a-research-log.** Apply when writing a wiki page from research: the page carries the subject and the owner's judgment, never an account of how it was researched.
- **principle-plain-tldr.** Apply when writing a page's TL;DR or Key Insight callout.
- **principle-draw-structure.** Apply when a page's subject has structure that prose makes the reader reconstruct: stages, a change of state, containment, which part calls which, or a branch between paths.

**Writing**

- **principle-standalone-note.** Apply when writing the body of a note that someone will read later without the conversation that produced it.
- **principle-quotation-attribution.** Apply when quoting, translating or interpreting a source in a note.
- **principle-preserve-voice.** Apply when revising prose someone else wrote, including the owner's sentences on a page you are updating.
- **principle-note-shape.** Apply when choosing a note's headings, lists, tables or bold, or the term used for one concept.

**Formatting**

- **principle-frontmatter.** Apply when writing or editing a note's YAML frontmatter: key order, value types, links and URLs in properties, and which keys a page may carry.
- **principle-link-form.** Apply when writing a link, URL or embed into a note: wikilinks, external links, first-mention linking and embedded media.
- **principle-markdown-blocks.** Apply when writing Markdown blocks into a note: nested lists, code fences, emphasis, callouts, footnotes, tags, comments, math or Mermaid.
