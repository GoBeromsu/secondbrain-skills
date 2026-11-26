---
name: "principle-resolve-target"
description: "Apply when about to write to a vault note: the vault root, the target note, the effect and the authority must each be stated exactly before the write happens."
disable-model-invocation: true
license: MIT
---

# Resolve the target before writing

A request that names the note and the change settles all four of these, so carry it out without asking again. Hold the write only while one of them is unknown:

| What | Resolved when you can state it exactly |
| --- | --- |
| Vault root | The directory the user named for this task, as an exact path |
| Target note | Its vault-relative path, including extension, not just a title |
| Effect | Create, insert, replace or delete, named at the level of a section, property or link |
| Authority | The user's request, a standing instruction for this vault, or the role of the area the note sits in (`principle-vault-roles`) covers that note and that effect |

- Reuse authority the task already granted instead of asking again for a note and effect it covers.
- When one is missing or ambiguous, name that one item and keep going with the reading and drafting that do not depend on it.
- Write through the vault-aware surface the user selected, and otherwise through the host's file write and edit tools; shell redirection and stream editors silently reformat a note, drop its trailing newline and mangle YAML and callout prefixes.

The vault's live policy overrides any line here.
