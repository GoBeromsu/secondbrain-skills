---
name: "principle-revise-and-consolidate"
description: "Apply when updating a wiki page that already exists, including one found by an alias: Term, Concept, Guide or Entity of any type."
disable-model-invocation: true
license: MIT
---

# Revise and consolidate

An existing page is the owner's accumulated record. An update makes it better without losing anything valid on it.

- Keep a before-image of the page before drafting.
- Draft only what is new: claims, sources and links the page does not already carry. When the page or an alias already covers the subject, add only the new claims.
- Draft from the inspected evidence, not from the page's own prose; neither the existing wiki nor one new source is ground truth.
- Have a separate reviewer compare the proposal with its evidence and the before-image, keep every valid statement, link and frontmatter value, and reduce the proposal to the minimal patch. When the runtime has no separate context, skip that page's update and report it.
- Change an existing statement only on verified evidence (a `verify` result or the owner's confirmation). When a source explicitly conflicts with a claim, keep both, attributed, in a `> [!warning] Contradiction` callout; a source that is silent does not contradict.
- When `term`, `concept`, `entity` or `ingest` revises the page, bring it to its current template as you go: sections, frontmatter keys and URL keys. Move a value to a new key only when it means the same thing (a profile URL, not a bare handle); a value that does not fit, or a target key that already holds a different value, stays where it is and is reported. A narrow `verify` correction or `query` feedback patch migrates nothing. A template change alone is never a reason to touch pages you were not asked to update.
- Preserve the creation date, identity and provenance. Verification fields (`explored`, `verificationStatus`, `confidence` changes) belong to `verify`.
- Rewriting generated prose does not change `authorship`. Revising a wiki Entity marked `authorship: user` sets it to `authorship: mixed`, and every sentence the owner wrote stays unchanged.

The vault's live policy overrides any line here. This principle shapes a write the task already asked for; it is not a reason to make one, and not a reason to withhold one.
