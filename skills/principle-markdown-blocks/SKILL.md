---
name: "principle-markdown-blocks"
description: "Apply when writing Markdown blocks into a note: nested lists, code fences, emphasis, callouts, footnotes, tags, comments, math or Mermaid."
disable-model-invocation: true
license: MIT
---

# Markdown blocks

Block syntax is checked from raw characters, without understanding the content, so it reads the same in the editor, the parser and the next agent only when it is exact. Standard Markdown is assumed knowledge; the syntax Obsidian adds is in the references.

- Indent each nested list level with the note's existing indent character, and with one tab per level where the note has none; mixed tabs and spaces make list depth ambiguous.
- Leave indentation inside code blocks and quotations as the source has it.
- Name a language on every code fence, and `text` when there is none.
- Put a space after a closing `**` that follows punctuation and is followed directly by a letter (`**traceability(audit)** suffix`), because that marker does not close the emphasis; leave `**term**suffix` as it is.
- Use a callout type Obsidian recognizes, or one the vault's CSS defines.

The vault's live policy overrides any line here. This principle shapes a write the task already asked for; it is not a reason to make one, and not a reason to withhold one.

## References

- [callouts](references/callouts.md): callout types, aliases, folding, nesting, custom CSS.
- [syntax](references/syntax.md): tags, comments, highlights, math, Mermaid fences, footnotes, a complete note.
