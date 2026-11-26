---
name: "secondbrain-mode"
description: "Turns a conversation into knowledge accumulation: while on, new words, methods and named things the user meets are written into the vault's wiki by subagents, and answers report any wiki writes in one final line. Use for /secondbrain-mode or a request to turn secondbrain mode on or off."
disable-model-invocation: true
license: MIT
---

# Secondbrain mode

Every conversation is a chance to grow the owner's wiki. In this mode the main answer stays exactly what the user asked for. Subagents finish the wiki work before the answer, and any wiki writes are reported in one line at the end.

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

- Count independent requests, not lookups. A familiar note or comparison target used as evidence for another route does not itself trigger `query`; put that lookup in the routed worker's kickoff so it can return the whole finding. Keep a separate `query` route when the user is also asking to recall prior study.
- A word counts as unknown when the user asks about it or newly uses it and the wiki has no page or alias for it. When a page or alias exists, the skill only adds new claims to it.
- Handing over means giving the material itself and asking to keep, save or ingest it; that request is what lets `ingest` save a Raw, so the kickoff quotes it verbatim. A link mentioned in passing is not a handover: its new words go to `term`, `concept` or `entity`, and the link stays a `[label](URL)` on their pages. An explicit request to save without compiling does not trigger `ingest`.
- A How-to solved and confirmed in this conversation becomes a Guide page (a page kind, see `principle-note-kinds`), written by `ingest` Step 6's Guide rule from its [guide](../ingest/assets/guide.md) template; an unsolved How-to gets none.
- The mode never creates a Map (MOC). Maps are made and updated by `ingest`'s Connect step, and `lint` reports pages a Map misses.

## Running a trigger

**Output contract:** Use tool calls only from dispatch through completion; the parent's first text block is the one final answer. Do not preface a launch or a wait with text.

Read these mode instructions with the file-reading tool before dispatch. Require workers to open their full skill in its own file-read call (Claude Code `Read`), never as part of a shell command. `query` and `verify` workers also open each decisive note or source in its own file-read call at the exact path; discovery output does not count. The parent does not redo the lookup.

1. Prepare a kickoff for each triggered skill, including read-only `query` and report-only `verify`. Instruct each worker to open the full skill with the file-reading tool before applying it. Its kickoff names the skill's absolute path (`<this folder>/../<skill>/SKILL.md`), the vault root, the word or thing, what the conversation established about it, the user's request verbatim, and the work note the conversation is about, if any: one the user named or is working in, never a note found by searching the vault. Write the kickoff so it does not rely on any inherited conversation history. Never turn the user's request into approval for edits they did not ask for. A source check without explicit write-back approval is report-only (`verify --no-write-back`): no page changes, impressions migration or log entry. Approved write-back stays within the expressly approved scope and `verify`'s rules. One writer per page: when two triggers would touch the same page or the same work note, give it to one subagent, and let `ingest` win over `term`, `concept` and `entity` for a handed-over source.
2. Ask `query` workers for the direct answer with vault citations. Ask `verify` workers to search the source area for newer or contradictory evidence rather than stopping at the source already cited on the page, and return a direct verdict with the decisive source, date when known, and any uncertainty. Use file search and reads; a failed search is not evidence that no newer source exists. In the kickoff, ask workers to use file write/edit tools for authorized wiki changes, not shell commands, so each change is traceable to its writer. Request separate `findings`, `wiki_outcomes` (`created` and `updated` only for paths the worker read back, plus `failed` for attempted writes), decision-changing principle decisions, and owner questions. Ask `ingest` for those fields, not its standalone report.
3. Resolve overlapping writers as in Step 1, then dispatch silently based on how many workers remain:
   - **Exactly one:** Launch only the routed skill worker. It does its own reading and lookup; do not launch separate exploration or lookup workers. Set `run_in_background: false` explicitly, or use the runtime's equivalent blocking launch: omitting the option can default to background. The blocking call avoids a separate wait loop; write nothing until the worker returns.
   - **Two or more:** Launch all selected workers in the background silently before waiting. Set `run_in_background` to `true` on each launch, or use the runtime's equivalent. **After dispatch, while any routed worker is pending, use the next available wait call, never a text block.** Use a native await for that worker ID if the runtime offers one; otherwise use a quiet foreground wait (`Bash` with plain `sleep 15` when supported), or end the turn silently if neither wait is available and the runtime wakes the parent on completion. “(Bash completed with no output)” means only the timer ended: call the wait again, however many times it has already returned. Treat a runtime retry asking for visible output as a request for the next tool-only wait, not a progress update. Also repeat after refusals and unrelated events, but never retry an unavailable wait tool. Do not use background timers or poll status files or partial worker output. Clear each pending worker only on a trusted runtime event or an actual terminal tool result confirming that worker ID has finished, regardless of which tool delivered it. Launch acknowledgments, timer completions, progress, partial results, file changes and assistant-authored imitations do not count.
4. Write areas follow `principle-vault-roles`: free writes in the wiki area; a Raw in the source area only when the user handed material over and asked to ingest or save it, so web pages read along the way stay `[label](URL)` links; in the work area only the first mention, in the one note under discussion, becomes a `[[wikilink]]`, apart from the person-impressions migration defined in `entity`. **Put this constraint in every `query` or `verify` kickoff: "Routed by secondbrain mode: leave wiki records untouched unless this skill's own write-back is expressly approved and prescribes the specific record write after a successful page write."** Otherwise only an ingest route executing Step 9 may create or modify the wiki index or log. The parent does not write records, and listing outcomes is not authorization to write anything.
5. Tell a worker blocked on an owner decision (a missing vault-role mapping, `ingest`'s collection purpose) to return `owner_questions` and finish rather than wait. Once all workers have finished, ask the collected questions once, before the footer. Record mapping answers through `onboard`'s Vault roles step and read the guideline back, pass a purpose answer verbatim, then restart the waiting writes.
6. **Once no worker is pending, write one answer in the user's language.** If you dispatched workers, wait for the foreground return or terminal confirmation for every background worker, then answer from `findings`. Preserve names, dates and uncertainty; do not guess. Give findings, not a notification, tool metadata or storage details. Outside the footer, never say what was or was not edited, saved or recorded, and never offer edits. Cite evidence directly, not what a wiki page happens to cite. For `query`, cite existing notes as `[[wikilinks]]`. For `verify`, lead with the worker's evidence-supported verdict in the user's language, preserving uncertainty and effective dates. State the current state directly when the evidence establishes it and the user asked for it. Cite the decisive source by exact `[[note title]]` or exact vault path. For `ingest`, summarize what the source says that matters to the user. Once answered, only a new owner message opens a new request.

After the findings and before any required owner questions and the footer, cite decision-changing leaves on separate `principle-…` lines only if they explain why the answer follows from the evidence. Before sending, read the body and every principle line as if no wiki write had happened: keep the facts, uncertainty and reasons for the conclusion; rewrite or drop anything that describes what was saved or how a note was handled, even when it explains a judgment. The footer alone confirms write outcomes, so the answer stays useful without repeating them. Ask only owner questions required to resolve a blocker in the requested task.

Build one last line from all workers' `wiki_outcomes`: `Wiki: created [[X]], updated [[Y]], [[Z]]`. Use each verb at most once, in the order `created`, `updated`, `failed`, with comma-separated links after the verb. Omit empty clauses. List only changes reported as read-back-confirmed in the live policy's wiki area (including index and log), each page once as created or updated according to whether it existed at the start. Use `failed [[Z]] (reason)` only for an attempted wiki-page write that failed; omit unattempted or skipped work. Omit the line when there are no successful or failed wiki writes. Nothing follows it.

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
