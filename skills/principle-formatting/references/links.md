# Links Reference

## Wikilinks

```markdown
[[Note Name]]                          Link to note
[[Note Name|Display Text]]             Custom display text
[[Note Name#Heading]]                  Link to heading
[[Note Name#^block-id]]                Link to block
[[#Heading in same note]]              Same-note heading link
```

Obsidian tracks a wikilink when its target is renamed; a Markdown link to a vault path is not tracked the same way.

## Block identifiers

Define a block ID by appending `^block-id` to any paragraph:

```markdown
This paragraph can be linked to. ^my-block-id
```

For lists and quotes, place the block ID on a separate line after the block:

```markdown
> A quote block

^quote-id
```

## Targets that are not Markdown notes

Obsidian resolves a bare wikilink stem to a Markdown note. For every other file type, keep the extension in the link, as [Obsidian's internal-link documentation](https://help.obsidian.md/links) requires:

```markdown
[[Team Board.canvas]]                  Canvas file
[[Team Board.canvas|Board]]            Canvas file with display text
[[Reading List.base]]                  Base file
[[Architecture Diagram.png]]           Image file
[[Handbook.pdf]]                       PDF file
```

`[[Team Board]]` is a different link: it reaches a Markdown note of that name if one exists, and otherwise stays unresolved. It never proves that the Canvas was reached.

When several files share a basename, which one a bare link reaches depends on the source note's own location, so include enough of the vault-relative folder path to make the target unambiguous:

```markdown
[[Projects/Team Board.canvas]]
```

## Destination resolution

Obsidian resolves link text relative to the note that contains it, so a destination is only correct with respect to that note. Through the app's supported scripting surface:

```js
app.metadataCache.getFirstLinkpathDest(linkpath, sourcePath)
```

- `linkpath` is the destination text only: no `[[` `]]` delimiters, no `|display text`, no `#heading` or `#^block-id` subpath. For `[[Projects/Team Board.canvas|Board]]` it is `Projects/Team Board.canvas`.
- `sourcePath` is the vault-relative path of the note that holds the link.
- `null` means the link is unresolved.
- A returned file whose `path` differs from the intended vault-relative target is a wrong destination, even though nothing reports it as unresolved.
- "The note has no unresolved links" is not the check. Unrelated links and intentional placeholders say nothing about whether this destination is right.
- When the app or its index is unavailable, report destination resolution as unverified. A file of the same name existing on disk is not resolution evidence, because a bare stem may resolve elsewhere.
