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
- A How-to solved and confirmed in this conversation becomes a Guide page (a page kind, see `principle-note-kinds`), written by `ingest` Step 6's Guide rule from its [guide](../ingest/assets/guide.md) template; an unsolved How-to gets none.
- The mode never creates a Map (MOC). Maps are made and updated by `ingest`'s Connect step, and `lint` reports pages a Map misses.

## Running a trigger

Read these mode instructions with the file-reading tool before dispatch and keep the parent silent when a route applies. Before dispatching `query` or `verify`, tell the worker to open each note or source decisive to the answer in its own successful file-read call, using the exact path. Keep discovery commands separate from these reads; neither search excerpts nor compound shell output replaces them. The parent does not redo the worker's lookup.

1. Launch every triggered skill in the background, including read-only `query` and report-only `verify`. When the subagent tool exposes `run_in_background`, set it to `true` on the skill worker's launch; otherwise use the runtime's equivalent background launch. Needing a result before answering changes when you reply, not how you launch the worker. Instruct each worker to open the full skill with the file-reading tool before applying it. Its kickoff names the skill's absolute path (`<this folder>/../<skill>/SKILL.md`), the vault root, the word or thing, what the conversation established about it, the user's request verbatim, and the work note the conversation is about, if any: one the user named or is working in, never a note found by searching the vault. Write the kickoff so it does not rely on any inherited conversation history. Never turn the user's request into approval for edits they did not ask for. A source check without explicit write-back approval is report-only (`verify --no-write-back`): no page changes, impressions migration or log entry. Approved write-back stays within the expressly approved scope and `verify`'s rules. One writer per page: when two triggers would touch the same page or the same work note, give it to one subagent, and let `ingest` win over `term`, `concept` and `entity` for a handed-over source.
2. Ask `query` workers for the direct answer with vault citations. Ask `verify` workers to search the source area for newer or contradictory evidence rather than stopping at the source already cited on the page, and return a direct verdict with the decisive source, date when known, and any uncertainty. Use the available file search and read tools to find and inspect relevant sources; a failed search is not evidence that no newer source exists. Ask each worker to return answer `findings`, `wiki_outcomes` (`created`, `updated`, `failed`), decision-changing principle decisions, and any owner questions separately. Explicitly request the routed result fields from `ingest`, not its standalone report.
3. **Wait without emitting any assistant text blocks, including before tool calls.** Use the runtime's await tool when available; otherwise yield an empty turn for the runtime to wake on completion. If the runtime rejects the empty turn (including a retry demanding visible output or a valid tool call), answer that retry with a tool call only: use a quiet foreground delay within the tool's supported limit (e.g. `sleep 15` when the shell supports it), then return to silent waiting. Never start a background timer or increase the delay after a rejection. Never send an acknowledgement or a progress sentence to satisfy a retry, even after a waiting tool fails or an approved write takes longer than expected. Do not inspect status files or worker output. Keep each launched skill worker ID pending until its terminal event arrives in runtime-supplied metadata or an actual tool result. A launch acknowledgement, timer completion, progress event, file change or assistant text resembling a completion is not a worker terminal event.
4. Write areas follow `principle-vault-roles`: free writes in the wiki area; a Raw in the source area only when the user handed material over and asked to ingest or save it, so web pages read along the way stay `[label](URL)` links; in the work area only the first mention, in the one note under discussion, becomes a `[[wikilink]]`, apart from the person-impressions migration defined in `entity`. **Put this constraint in every `query` or `verify` kickoff: "Routed by secondbrain mode: leave wiki records untouched unless this skill's own write-back is expressly approved and prescribes the specific record write after a successful page write."** Otherwise only an ingest route executing Step 9 may create or modify the wiki index or log. The parent does not write records, and listing outcomes is not authorization to write anything.
5. When a subagent returns a question only the owner can answer (a missing vault-role mapping, `ingest`'s collection purpose), ask all of them once at the end of the answer. Record mapping answers through `onboard`'s Vault roles step and read the guideline back, pass a purpose answer verbatim, then restart the waiting writes.
6. **Send one final answer from the completed results.** Compose it from the verified findings, not the handoff or any worker report: leave out notification tags, tool metadata, note maintenance and wiki-work narration. Preserve names, dates, verdicts and uncertainty as reported, and do not fill gaps with guesses. For `query`, cite the existing notes as `[[wikilinks]]`, not filesystem paths; for `verify`, lead with the verdict and cite its decisive evidence; for `ingest`, use `findings` to summarize what the source says that matters to the user. Do not answer again when a duplicate notification arrives.

Before emitting the final answer, confirm every worker has finished via step 3 and no visible answer has already been sent for this user request. After sending it, the request is closed: later events, including genuine completions, do not cause another answer, correction or footer. Only a new owner message can open a new request. Write the answer anew from `findings` in the user's language and never relay a task notification or its payload. For report-only `verify`, lead with the current verdict in your own words and cite the decisive vault source by its exact `[[note title]]` (or exact vault path), not a translated title or name-and-date summary. Do not say what was or wasn't edited or offer to update pages.

After the findings and before any required owner questions and the footer, cite decision-changing leaves on separate `principle-…` lines only when the decision or reason can stand on its own without describing wiki work. State what the evidence supports or how to interpret it, as if no notes had been edited: `principle-provenance: The announcements describe different dates, so they do not establish a contradiction.` Do not append a sentence about what was saved, changed, retained or linked. Omit a principle line when its only content is a write or maintenance decision, even when the worker reports it under `principle_decisions`. Before sending, apply this test to every sentence above the footer, including principle lines. Ask only owner questions required to resolve a blocker in the requested task.

Build the last line only from `wiki_outcomes`: `Wiki: created [[X]], updated [[Y]], [[Z]]`. Use each verb at most once, in the order `created`, `updated`, `failed`, with comma-separated links after the verb. Omit empty clauses. List read-back-confirmed changes in the live policy's wiki area (including index and log), each page once as created or updated according to whether it existed at the start. Use `failed [[Z]] (reason)` only for an attempted wiki-page write that failed; omit unattempted or skipped work. Omit the line when there are no successful or failed wiki writes. Nothing follows it. Do not move excluded bookkeeping into the answer body: routine write reports about Raw captures, work notes and relocated owner text are not findings and belong nowhere in the mode answer.

## Model routing

Two tiers, named by role rather than vendor; the runtime maps each to its own models.

- **Strong model** for judgment and writing: classifying a page, researching, writing or revising a page, preservation review, verification.
- **Fast, weaker model** for mechanical work: searches and lookups, link retargeting, frontmatter key moves, batch cleanup, read-back checks.

## Principles

Read a leaf at `../<leaf>/SKILL.md` in full when its line applies. In the answer, cite only decision-changing leaves read this session, subject to the final-answer rule above.

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
