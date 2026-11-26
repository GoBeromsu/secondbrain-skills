# Embeds Reference

Prefix a wikilink with `!` to render its target in place. Everything in [links](links.md) about targets applies to embeds too.

```markdown
![[Note Name]]                         Embed full note
![[Note Name#Heading]]                 Embed section
![[Note Name#^block-id]]               Embed block, or a list that has a block ID
![[image.png]]                         Embed image
![[image.png|300]]                     Width only (keeps aspect ratio)
![[image.png|640x480]]                 Width x height
![[audio.mp3]]                         Audio player
![[clip.mp4]]                          Video player
![[document.pdf#page=3]]               PDF page
![[document.pdf#height=400]]           PDF viewer height
![[Reading List.base#View Name]]       Base, optionally one of its views
![[Team Board.canvas]]                 Canvas
```

- Embed a heading or block in preference to a whole note, which grows as its source grows. Never embed a note into itself or build a cycle between two notes.
- The pipe is a size only on an embed. `[[image.png|300]]` without `!` is a link labelled `300`.
- Keep the extension on every target that is not a Markdown note: `![[Team Board]]` embeds a note of that name, never the canvas. Add folder path when a basename is shared (`![[Projects/Diagram.png|600]]`).
- An embedded canvas displays its shapes only, not the text inside cards, as [Obsidian's embed documentation](https://help.obsidian.md/embeds) states. That is not a broken link; leave it as written.

## External media

```markdown
![Alt text](https://example.com/image.png)
![Alt text|300](https://example.com/image.png)
![Demo](https://example.com/demo.mp4)
```

Wrap a URL that contains spaces or parentheses in angle brackets: `![Alt text](<https://example.com/my image.png>)`.

## Search results

````markdown
```query
tag:#project status:done
```
````

The app runs a `query` block when it renders the note, so the result is not stored in the file.

A player, a query result and external media cannot be judged from the note source. Report their rendering as unverified unless reading view was checked.
