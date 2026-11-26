---
name: "principle-read-back"
description: "Apply when a write to a vault note has just finished, before reporting it done or linking to it."
disable-model-invocation: true
license: MIT
---

# Read back after writing

A write that returned no error is not a verified change. Report each leg you could not run as unverified.

1. Re-read the note from the vault: the intended change is present, the frontmatter still parses, nothing else moved, nested lists use one indent character and no YAML line is indented with a tab.
2. Resolve every changed link or embed from the note that contains it and compare the returned path with the intended one, as [links](../principle-link-form/references/links.md) describes; a file of the same name existing on disk is not resolution.
3. Look at every changed embed in reading view; resolution does not prove rendering.

The vault's live policy overrides any line here. This principle shapes a write the task already asked for; it is not a reason to make one, and not a reason to withhold one.
