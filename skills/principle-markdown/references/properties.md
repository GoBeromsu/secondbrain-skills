# Properties (Frontmatter) Reference

Properties use YAML frontmatter at the start of a note:

```yaml
---
title: My Note Title
date: 2024-01-15
tags:
  - project
  - important
aliases:
  - Alternative Name
cssclasses:
  - custom-class
status: in-progress
rating: 4.5
completed: false
due: 2024-02-01T14:30:00
---
```

The opening `---` is the first line of the file, and a line of exactly `---` closes the block. One YAML error drops every property in the note.

## Property types

| Type | Example |
|------|---------|
| Text | `title: My Title` |
| Number | `rating: 4.5` |
| Checkbox | `completed: true` |
| Date | `date: 2024-01-15` |
| Date & Time | `due: 2024-01-15T14:30:00` |
| List | `tags: [one, two]` or YAML list |
| Tags | Only for the `tags` property |

- A date in another shape stays text and does not sort or filter as a date.
- A quoted `"true"` or `"4.5"` is text, not a checkbox or a number.
- An empty value (`status:`) is null, which differs from an absent key and from `status: ""`.
- Quote a value that contains `: ` or ` #` (`title: "Release #2: notes"`); unquoted, `#` starts a comment.
- A key written twice keeps one value silently.

## Links in properties

Links go in Text or List properties. Always quote a wikilink, because an unquoted `[[Other Note]]` is read as a nested list, not a link:

```yaml
related: "[[Other Note]]"
sources:
  - "[[Meeting Notes 2024-01-10]]"
  - "[[Team Board.canvas]]"
```

A link in a property resolves like a body link, so a changed one needs the same readback from its source note (see [links](links.md)).

## Default properties

- `tags` - Note tags (searchable, shown in graph view)
- `aliases` - Alternative names for the note, offered in link suggestions. A bare `[[Alias]]` does not resolve; write `[[Note|Alias]]`
- `cssclasses` - CSS classes applied to the note; they change nothing unless a snippet or theme styles them

All three take a list.

## Tags

```yaml
tags:
  - project
  - nested/tag
```

Write a frontmatter tag without the leading `#`. A tag holds letters (any language), numbers, `_`, `-` and `/` for nesting, needs at least one non-numerical character (`1984book`, not `1984`), and cannot contain a space.

## Editing an existing block

Change only the requested key. Leave unknown keys, list style and quoting as found, and extend a block list with a block item. Do not convert a value's type to tidy it; a quoted number or a text date may be deliberate.
