---
name: "principle-markdown"
description: "Apply whenever writing or restyling Markdown in a note: frontmatter, wikilinks, external links and embeds, lists, code fences, callouts, footnotes, tags, math or Mermaid; a note's headings, tables, bold and terms; a TL;DR or Key Insight callout; quoting, translating or interpreting a source; and deciding whether a structure prose would make the reader rebuild should be drawn as a diagram."
disable-model-invocation: true
license: MIT
---

# Markdown

Obsidian, Bases, linters and later agents read a note from its raw characters, so frontmatter, links and blocks mean the same thing everywhere only when their form is exact. Standard Markdown is assumed knowledge; the syntax Obsidian adds is in the references.

## Shape and terms

A reader scans before reading, so the shape of a note tells them where an answer is and the terms tell them it is the same thing each time.

- Write a heading that predicts its content, and keep under it only what answers the same question.
- Use a list for steps and options, prose for an argument, and a table when several things are compared on several criteria.
- Bold only what a reader scans for, such as a key term, a decision or a warning.
- Use one term for one concept throughout, following the existing page's title, so the reader never wonders whether two words mean two things.
- Write a TL;DR or Key Insight callout as plain sentences with at most one bold phrase, naming a note or product in plain words; it is read first and often alone, so the sections below carry the links and footnotes for the same claims.
- A document type's required headings and templates stay as they are.

## Quotation and attribution

A reader must be able to tell whose words they are reading: the source's, a translator's, or the writer's.

- Put quoted source text, its translation, its interpretation and the writer's own words in separate paragraphs or under short labels (`Translation`, `Interpretation`, `My words`).
- Keep a translation out of the blockquote that holds the original, and mark it as a translation.
- Present a sentence as a quotation only when its source is named and contains it word for word.

## Diagrams

Draw a structure the reader would otherwise rebuild in their head: stages, a change of state, containment, which part calls which, a branch between paths.

- Use `obsidian-visualize` to put an inline Pele diagram beside the paragraph it illustrates, with each box and arrow grounded in the sources read.
- Nest regions for containment, show transitions for changing state, branch where paths diverge. When a source defines the subject with a diagram, draw that diagram's own structure (four overlapping circles as a Venn), not a flow of boxes.
- This is a judgment per page, not a quota: a subject one sentence or a table already carries gets no diagram, and a calculation stays in prose or a table.

## Frontmatter

- Indent YAML with two spaces per level; YAML rejects a tab as indentation.
- Fill every value by YAML's own rules: lists stay lists with one item per value, and a value containing `"` or `\` follows double-quoted escaping.
- Quote a wikilink in YAML (`"[[Name]]"`). Name an entity that has a page in the vault as that wikilink, not as plain text (`organization: "[[Imperial College London]]"`).
- On a wiki page, sort keys alphabetically, as the vault's linter does.
- On a wiki page, put an external URL under a key ending in `_url` (`blog_url`, `github_url`, `instagram_url`, `linkedin_url`, `website_url`, `x_url`, `youtube_url`), as a plain URL. Use `url` for a non-product Entity's canonical homepage only. For a product's repository or homepage, use `github_url` for the hosts `github.com` and `www.github.com`, regardless of path, and `website_url` for any other host, including `github.io`. A bare `url` on a product hides which host it points at, so a product does not use it; follow [`entity`'s update rules](../entity/SKILL.md) for legacy values. Put other web references in the body as `[label](URL)`. A Raw keeps the provenance keys its ingest schema defines, such as `source` and `referenced`.
- Add `status` only to a note that tracks a lifecycle; elsewhere it is noise a Base will still filter on.
- Leave `---` out of the body; Obsidian reads it as a frontmatter delimiter, not a separator.
- Use the key the vault already uses for a meaning, and omit an optional key whose value is unknown rather than inventing one.

## Links and embeds

- Link a note in the vault as `[[Note]]` and external material as `[name of the article or site](URL)`, so no raw URL is left in prose you write.
- Convert a bare or backticked URL in text you write or restyle to that form; a real path or URL stays as it is where a command, code, quotation or captured source text has it.
- Link the same note once per note, at its first mention in the body, and write it as plain text after that; this holds for terms and people alike.
- Call a person by another name with `[[Full Name|Short Name]]` (`[[Ada Lovelace|Ada]]`).
- Link a note only after reading the target confirms it supports what the sentence says, and create no page just to have a link target.
- Embed an external image or video by its URL in image syntax (`![Diagram](https://example.com/diagram.png)`), not in an HTML tag, instead of downloading it into the vault; download only when the user asks.
- Keep the extension on every target that is not a Markdown note (`[[Team Board.canvas]]`), and add enough folder path to make a shared basename unambiguous.

## Blocks

- Indent each nested list level with the note's existing indent character, and with one tab per level where the note has none; mixed tabs and spaces make list depth ambiguous.
- Leave indentation inside code blocks and quotations as the source has it.
- Name a language on every code fence, and `text` when there is none.
- Put a space after a closing `**` that follows punctuation and is followed directly by a letter (`**traceability(audit)** suffix`), because that marker does not close the emphasis; leave `**term**suffix` as it is.

The vault's live policy overrides any line here. This principle shapes a write the task already asked for; it is not a reason to make one, and not a reason to withhold one.

## References

Open only the one the write needs.

- [properties](references/properties.md): property types, YAML traps, links in properties, tags, editing an existing block.
- [links](references/links.md): wikilink forms, block identifiers, targets that are not Markdown notes, destination resolution.
- [embeds](references/embeds.md): embed forms, sizing, external media, search-result embeds.
- [callouts](references/callouts.md): callout form, folding, nesting, types, custom CSS.
- [syntax](references/syntax.md): tags, comments, highlights, tables, math, Mermaid fences, footnotes.
