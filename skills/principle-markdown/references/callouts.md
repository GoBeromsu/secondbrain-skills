# Callouts Reference

A callout is a blockquote whose first line starts with `[!type]`.

```markdown
> [!note]
> Basic callout.

> [!warning] Custom Title
> Callout with a custom title.

> [!tip] Title Only

> [!faq]- Collapsed by default
> Foldable callout (- collapsed, + expanded). Without a marker it does not fold.

> [!question] Outer callout
> > [!note] Inner callout
> > One more `>` per nesting level, on every inner line.
```

- Put the fold marker directly after `]`, before the title: `> [!tip]- Title`.
- Keep `>` on every line, including the blank line between two paragraphs and each line of a code fence. A line without it ends the callout.
- The type is matched without regard to case. An unknown type still renders, with default styling, so a typo such as `[!waring]` looks valid in source.

## Types

| Type | Aliases |
|------|---------|
| `note` | - |
| `abstract` | `summary`, `tldr` |
| `info` | - |
| `todo` | - |
| `tip` | `hint`, `important` |
| `success` | `check`, `done` |
| `question` | `help`, `faq` |
| `warning` | `caution`, `attention` |
| `failure` | `fail`, `missing` |
| `danger` | `error` |
| `bug` | - |
| `example` | - |
| `quote` | `cite` |

An alias renders the same as its type; use one name per note.

## Custom callouts (CSS)

```css
.callout[data-callout="custom-type"] {
  --callout-color: 255, 0, 0;
  --callout-icon: lucide-alert-circle;
}
```

`--callout-color` takes comma-separated RGB channels, not a hex string. The CSS belongs in a vault snippet or theme, which is a separate change from writing the note.
