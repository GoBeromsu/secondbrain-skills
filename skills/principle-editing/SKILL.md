---
name: "principle-editing"
description: "Apply around every write to a vault note, however small: before it, to pin down the vault, the target note, the effect and the authority; while editing an existing note, to change only what the task asked for; and after it, before reporting it done or linking to it, to read the note back and resolve every changed link and embed."
disable-model-invocation: true
license: MIT
---

# Safe vault writes

An edit is trusted only when it reached the intended note, left no side effects and was read back.

## Before: resolve the target

A request that names the note and the change settles all four of these, so carry it out without asking again. Hold the write only while one of them is unknown:

| What | Resolved when you can state it exactly |
| --- | --- |
| Vault root | The directory the user named for this task, as an exact path |
| Target note | Its vault-relative path, including extension, not just a title |
| Effect | Create, insert, replace or delete, named at the level of a section, property or link |
| Authority | The user's request, a standing instruction for this vault, or the role of the area the note sits in ([vault roles](../principle-knowledge-notes/SKILL.md#vault-roles)) covers that note and that effect |

- Reuse authority the task already granted instead of asking again for a note and effect it covers.
- When one is missing or ambiguous, name that one item and keep going with the reading and drafting that do not depend on it.
- Write through the vault-aware surface the user selected, and otherwise through the host's file write and edit tools; shell redirection and stream editors silently reformat a note, drop its trailing newline and mangle YAML and callout prefixes.

## While: preserve what the task did not ask for

- Read the current note, frontmatter included, before editing it; the owner or a sync may have changed it since you last looked.
- Change only what was requested: one property, one section, one link.
- Keep everything else byte-identical, because the owner, the vault's linter and other notes rely on what you did not mean to touch: unrelated properties and their order, headings, block identifiers, existing links and embeds, aliases, tags, `%%comments%%`, footnote definitions, code fences, indentation, line endings and the trailing newline.
- Reflow, reorder frontmatter keys, switch link style or re-case headings only when that normalization is the request. When `term`, `concept`, `entity` or `ingest` revises a wiki page, bringing it to its current template counts as requested; a narrow correction from `verify` or `query` does not.
- Fix the link text instead of renaming or moving a file to make a link resolve; a rename rewrites links across the vault and needs its own approval.
- Get explicit scope before deleting a section, clearing or replacing whole frontmatter, changing or removing links across several notes, or running a find-and-replace across notes.

## After: read back

A write that returned no error is not a verified change. Report each leg you could not run as unverified.

1. Re-read the note from the vault: the intended change is present, the frontmatter still parses, nothing else moved, nested lists use one indent character and no YAML line is indented with a tab.
2. Resolve every changed link or embed from the note that contains it and compare the returned path with the intended one, as [links](../principle-markdown/references/links.md) describes; a file of the same name existing on disk is not resolution.
3. Look at every changed embed in reading view; resolution does not prove rendering.

The vault's live policy overrides any line here.
