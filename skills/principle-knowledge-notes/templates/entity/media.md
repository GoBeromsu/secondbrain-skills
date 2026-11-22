# Media Entity

Use this scaffold for a publisher that keeps putting things out: a YouTube channel, podcast, newsletter or blog. The two-zone and frontmatter rules in the [common Entity template](../entity.md) apply.

- One video, episode, issue or post is a Raw, never an Entity. List it under `### Published` in the media Entity that put it out.
- Title it with the name the publisher displays. The person or organization behind it is its own Entity, named in `operators` and linked from `### Related`; a channel never replaces its operator's note.
- Record `platform`, `url` and `feedUrl` only from the source or the platform page. Where existing notes of this type already use other keys (`feed_url`, `youtube_channel_id`), use theirs.
- The owner zone holds why the owner follows it and their notes.

## Scaffold

```markdown
---
type: {{live_policy_type}}
aliases: []
description: "{{english_one_or_two_sentences}}"
author:
  - "{{live_policy_author_or_agent_role}}"
model: {{runtime_model}}
effort: {{runtime_effort_or_default}}
date_created: {{today}}
date_modified: {{today}}
tags: []
platform: {{youtube|podcast|newsletter|blog}}
url: "{{canonical_url}}"
feedUrl: "{{feed_url}}"
operators:
  - "[[{{person_or_organization}}]]"
source:
  - "[[{{raw_source}}]]"
related: []
---

# {{name}}

## Notes

## From Sources

- {{YYYY-MM-DD}} {{fact_or_mention}} — [[{{raw_source}}]]

### Published

- {{YYYY-MM-DD}} [[{{raw_item}}]] — {{one_line}}

### Sources

- [[{{raw_source}}]]

### Related

- [[{{related_page}}]]
```
