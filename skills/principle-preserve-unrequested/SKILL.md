---
name: "principle-preserve-unrequested"
description: "Apply when editing an existing note: change only what the task asked for and keep everything else byte-identical."
disable-model-invocation: true
license: MIT
---

# Preserve what the task did not ask for

An edit is trusted only when it leaves no side effects. Everything outside the requested change survives byte for byte.

- Read the current note, frontmatter included, before editing it.
- Change only what was requested: one property, one section, one link.
- Keep everything else identical: unrelated properties and their order, headings, block identifiers, existing links and embeds, aliases, tags, `%%comments%%`, footnote definitions, code fences, indentation, line endings and the trailing newline.
- Reflow, reorder frontmatter keys, switch link style or re-case headings only when that normalization is the request. When `term`, `concept`, `entity` or `ingest` revises a wiki page, bringing it to its current template counts as requested; a narrow correction from `verify` or `query` does not.
- Fix the link text instead of renaming or moving a file to make a link resolve; a rename rewrites links across the vault and needs its own approval.
- Get explicit scope before deleting a section, clearing or replacing whole frontmatter, changing or removing links across several notes, or running a find-and-replace across notes.

The vault's live policy overrides any line here.
