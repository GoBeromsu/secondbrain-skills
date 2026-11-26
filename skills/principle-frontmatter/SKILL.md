---
name: "principle-frontmatter"
description: "Apply when writing or editing a note's YAML frontmatter: key order, value types, links and URLs in properties, and which keys a page may carry."
disable-model-invocation: true
license: MIT
---

# Frontmatter

Frontmatter is read by Obsidian, Bases, linters and later agents before anyone reads the body, so it must parse and mean one thing per key.

- Indent YAML with two spaces per level; YAML rejects a tab as indentation.
- Fill every value by YAML's own rules: lists stay lists with one item per value, and a value containing `"` or `\` follows double-quoted escaping.
- Quote a wikilink in YAML (`"[[Name]]"`). Name an entity that has a page in the vault as that wikilink, not as plain text (`organization: "[[Imperial College London]]"`).
- On a wiki page, sort keys alphabetically, as the vault's linter does.
- On a wiki page, put an external URL under a key ending in `_url` (`blog_url`, `github_url`, `instagram_url`, `linkedin_url`, `website_url`, `x_url`, `youtube_url`), as a plain URL. Use `url` for a non-product Entity's canonical homepage only. For a product's repository or homepage, use `github_url` for the hosts `github.com` and `www.github.com`, regardless of path, and `website_url` for any other host, including `github.io`. Never use bare `url` on a product; follow [`entity`'s update rules](../entity/SKILL.md) for legacy values. Put other web references in the body as `[label](URL)`. A Raw keeps the provenance keys its ingest schema defines, such as `source` and `referenced`.
- Add `status` only to a note that tracks a lifecycle; never add it by default.
- Never write `---` in the body; it is a frontmatter delimiter, not a separator.
- Use the key the vault already uses for a meaning, and omit an optional key whose value is unknown rather than inventing one.

The vault's live policy overrides any line here. This principle shapes a write the task already asked for; it is not a reason to make one, and not a reason to withhold one.

## References

- [properties](references/properties.md): property types, YAML rules, tags, safe frontmatter edits.
