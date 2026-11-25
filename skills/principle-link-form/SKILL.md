---
name: "principle-link-form"
description: "Apply when writing a link, URL or embed into a note: wikilinks, external links, first-mention linking and embedded media."
disable-model-invocation: true
license: MIT
---

# Link form

A parser, an editor and a later agent all resolve links from their raw characters, so one form per kind of target keeps them readable everywhere.

- Link a note in the vault as `[[Note]]` and external material as `[name of the article or site](URL)`, so no raw URL is left in prose you write.
- Convert a bare or backticked URL in text you write or restyle to that form; a real path or URL stays as it is where a command, code, quotation or captured source text has it.
- Link the same note once per note, at its first mention in the body, and write it as plain text after that; this holds for terms and people alike.
- Call a person by another name with `[[Full Name|Short Name]]` (`[[Ada Lovelace|Ada]]`).
- Link a note only after reading the target confirms it supports what the sentence says, and create no page just to have a link target.
- Embed an external image or video by its URL in image syntax (`![Diagram](https://example.com/diagram.png)`), not in an HTML tag, instead of downloading it into the vault; download only when the user asks.
- Keep the extension on every target that is not a Markdown note (`[[Team Board.canvas]]`), and add enough folder path to make a shared basename unambiguous.

The vault's live policy overrides any line here. This principle shapes a write the task already asked for; it is not a reason to make one, and not a reason to withhold one.

## References

- [links](references/links.md): wikilink forms, block identifiers, targets that are not Markdown notes, destination resolution.
- [embeds](references/embeds.md): every embed form, sizing, external media, embed readback.
