---
name: "principle-formatting"
description: "Guides everything about a vault note that can be judged from its raw characters without understanding the content: Obsidian Flavored Markdown syntax (wikilinks, embeds, callouts, properties or frontmatter, tags, comments, highlights, math, footnotes, block references), which form a link takes, list indentation, code fences and emphasis markers, plus which note is the target, what stays untouched and how the result is read back. Use whenever a .md file or note in a vault is created or edited, even for a small addition and even when another workflow is the one producing the note (a source turned into a note, a translation, a summary, a research write-up, adding images or video), and to clean up, organize, tidy, restyle or review the formatting of notes. Load it in addition to whichever workflow handles the request: it works alongside that workflow and does not replace it. Not for choices of wording, argument or translation, .canvas or .base internals, or vault CLI operations."
license: MIT
---

# Formatting

Formatting is every part of a note that can be checked from its raw characters without understanding what it says: syntax, link form, indentation, and whether the rest of the note survived the edit. An editor, a parser and a later agent all depend on it reading the same everywhere.

Apply these lines to text you write or were asked to restyle. Standard Markdown is assumed knowledge; the syntax Obsidian adds is in the references at the end. The destination vault's live policy overrides any line here. These lines shape a write the task already asked for; they are not a reason to make one, and not a reason to withhold one.

## Resolve the target before writing

A request that names the note and the change settles all four of these, so carry it out without asking again. Hold the write only while one of them is unknown:

| What | Resolved when you can state it exactly |
| --- | --- |
| Vault root | The directory the user named for this task, as an exact path |
| Target note | Its vault-relative path, including extension, not just a title |
| Effect | Create, insert, replace or delete, named at the level of a section, property or link |
| Authority | The user's request, or a standing instruction for this vault, covers that note and that effect |

- Reuse authority the task already granted instead of asking again for a note and effect it covers.
- When one is missing or ambiguous, name that one item and keep going with the reading and drafting that do not depend on it.
- Write through the vault-aware surface the user selected, and otherwise through the host's file write and edit tools; shell redirection and stream editors silently reformat a note, drop its trailing newline and mangle YAML and callout prefixes.

## Preserve what the task did not ask for

- Read the current note, frontmatter included, before editing it.
- Change only what was requested: one property, one section, one link.
- Keep everything else byte-identical: unrelated properties and their order, headings, block identifiers, existing links and embeds, aliases, tags, `%%comments%%`, footnote definitions, code fences, indentation, line endings and the trailing newline.
- Reflow, reorder frontmatter keys, switch link style or re-case headings only when that normalization is the request.
- Fix the link text instead of renaming or moving a file to make a link resolve; a rename rewrites links across the vault and needs its own approval.
- Get explicit scope before deleting a section, clearing or replacing whole frontmatter, changing or removing links across several notes, or running a find-and-replace across notes.

## Links

- Link a note in the vault as `[[Note]]` and external material as `[name of the article or site](URL)`.
- Convert a bare or backticked URL in text you write or restyle to that form, and keep a real path or URL where a command, code, quotation or captured source text has it.
- Link the same note once per note, at its first mention in the body, and write it as plain text after that; this holds for terms and people alike.
- Call a person by another name with `[[Full Name|Short Name]]` (`[[Ada Lovelace|Ada]]`).
- Embed an external image or video by its URL in image syntax (`![Diagram](https://example.com/diagram.png)`, `![Demo](https://example.com/demo.mp4)`), not in an HTML tag, instead of downloading it into the vault; download only when the user asks.
- Keep the extension on every target that is not a Markdown note (`[[Team Board.canvas]]`), and add enough folder path to make a shared basename unambiguous.

## Indentation and blocks

- Indent each nested list level with the note's existing indent character, and with one tab per level where the note has none; mixed tabs and spaces make list depth ambiguous.
- Indent YAML frontmatter with two spaces per level; YAML rejects a tab as indentation.
- Leave indentation inside code blocks and quotations as the source has it.
- Name a language on every code fence, and `text` when there is none.
- Put a space after a closing `**` that follows punctuation and is followed directly by a letter (`**traceability(audit)** suffix`), because that marker does not close the emphasis; leave `**term**suffix` as it is.

## Read back

A write that returned no error is not a verified change. Report each leg you could not run as unverified.

1. Re-read the note from the vault after every write: the intended change is present, the frontmatter still parses, nothing else moved, nested lists use one indent character and no YAML line is indented with a tab.
2. Resolve every changed link or embed from the note that contains it and compare the returned path with the intended one, as [links](references/links.md) describes; a file of the same name existing on disk is not resolution.
3. Look at every changed embed in reading view; resolution does not prove rendering.

## References

- [links](references/links.md): wikilink forms, block identifiers, targets that are not Markdown notes, destination resolution.
- [embeds](references/embeds.md): every embed form, sizing, external media, embed readback.
- [callouts](references/callouts.md): callout types, aliases, folding, nesting, custom CSS.
- [properties](references/properties.md): property types, YAML rules, tags, safe frontmatter edits.
- [syntax](references/syntax.md): tags, comments, highlights, math, Mermaid fences, footnotes, a complete note.
