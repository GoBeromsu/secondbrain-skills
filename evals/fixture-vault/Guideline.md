---
aliases:
  - Vault Guideline
date_created: 2026-11-26
date_modified: 2026-11-26
description: Live policy for the eval fixture vault. Names the folder for each vault role, the lifecycle notes that carry status, and how Entity pages are marked.
tags:
  - guideline
type: guideline
---
# Guideline

This vault is an eval fixture. Its folder names differ from any real vault on purpose: skills must read the roles from here, never from a hardcoded path.

## Roles

| Role | Folder | Rule |
| --- | --- | --- |
| wiki | `Knowledge/` | Agents create, revise, overwrite and delete pages freely. |
| source | `Sources/` | Raw sources. Saved only when the owner hands over material and asks to ingest or save it. |
| work | `Projects/` | The owner's work notes. Agents only turn the first mention of a term that has a page into a wikilink. |
| daily-notes | `Projects/Journal/` | `YYYY-MM-DD` filenames. Missing daily notes may be linked by date; agents do not create them. |

Wiki subfolders: `Maps/` for MOCs, `People/`, `Organizations/`, `Places/`, `Products/` and `Books/` for Entities, `Terms/`, `Concepts/`, `Guides/`.

## Pages

- Notes in the registered Entity folders are Entities; `layer: entities` also identifies an Entity elsewhere. Terms have `layer: terms`, Concepts `layer: concepts`, Guides `layer: guides`, MOCs `type: moc`.
- The owner's permanent notes live in `Notes/`. Impressions the owner wrote about a person move there as `{date_created} {Name}.md`, with `authorship: user` and `related` linking the person.

## Lifecycle

Only lifecycle notes carry `status`: notes with `type: project` or `type: task`. Allowed values are `todo`, `inprogress`, `done` and `stop` for these two types.

Book Entities of `type: book` in a registered Entity folder carry the owner's `status` only when they have a `## Reading Progress` heading. No other note, including a chapter Raw, has a `status` key.

## Frontmatter

- Keys in alphabetical order.
- External URLs only under `*_url` keys as plain URLs (`blog_url`, `x_url`, `youtube_url` …); `url` is the canonical homepage.
