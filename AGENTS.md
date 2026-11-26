# AGENTS.md

Rules for agents editing this repository. Keep every file as short as its job allows.

## Anti-patterns

- **One check, two implementations.** `obsidian-lint.py`/`.js` re-implemented `link-lint.py`, and `DUP-HEADING` ran in both `link-lint.py` and `marksman-lint.py`. Keep one owner per check. Prefer an existing tool (defuddle, knap, marksman, `ob`, the Obsidian CLI) over a custom script, but only where it works in the skill's setting — lint must run with the app closed.
- **A rule restated in a skill.** A skill points to the principle that states a rule (`../principle-*/SKILL.md`); it does not copy it.
- **A principle per formatting habit.** TL;DR, quotation and attribution and the like are Markdown form and belong in `principle-markdown`. Principles are grouped by function: archival, markdown, writing, knowledge-notes, editing.
- **A skill that is a mode of another.** inbox, reindex and status became parts of ingest and lint. A new skill needs its own trigger and workflow.
- **Trimming the why.** Cut repetition, not the reason a rule exists (archival: the original author's words are the record). A dropped cue in secondbrain-mode cost eval assertions.
- **Taking the owner's label as the classification.** "Make a term note" asks for a page; the note kind comes from the criteria in `principle-knowledge-notes`.
- **A new lint rule without checking graders.** Eval graders run `link-lint`; a vault-wide rule (`ORPHAN`) failed every suite that writes a fresh page.

## Changing a skill

- Run its eval against the previous snapshot with the skill-creator layout (`evals/agent_run.py`), and keep results in the ignored `evals/results/`.
- Pass `python3 scripts/validate.py` before committing.
