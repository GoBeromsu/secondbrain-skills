# Updating an existing wiki page

The procedure behind `principle-writing`'s revise-and-consolidate rules, for every skill that revises a Term, Concept, Guide or Entity page that already exists: `ingest`, `term`, `concept`, `entity`, and the narrow write-backs of `verify` and `query`.

## Steps

1. Keep a before-image of the page before drafting.
2. Draft only what is new from the inspected evidence; when the page or an alias already covers the subject, the draft holds only the new claims. Neither the existing wiki nor one new source is ground truth.
3. Have a separate reviewer, in its own context, compare the draft with its evidence and the before-image. It keeps every valid statement, link and frontmatter value and reduces the draft to the minimal patch. When the runtime has no separate context, skip that page's update and report it.
4. Change an existing statement only on verified evidence (a `verify` result or the owner's confirmation). When a source explicitly conflicts with a claim, keep both, attributed, in a `> [!warning] Contradiction` callout; a source that is silent does not contradict.
5. Apply the patch and read the page back against the before-image (`principle-editing`).

## Template migration on touch

- When `term`, `concept`, `entity` or `ingest` revises a page, bring it to its current template as you go: sections, frontmatter keys and URL keys. A template change alone is never a reason to touch a page nobody asked to update.
- Move a value to a new key only when it means the same thing (a profile URL, not a bare handle). A value that does not fit, or a target key that already holds a different value, stays where it is and is reported.
- A narrow `verify` correction or `query` feedback patch migrates nothing.

## What stays fixed

- The creation date, identity and provenance.
- Verification fields (`explored`, `verificationStatus`, `confidence` changes) belong to `verify`.
- `authorship`: rewriting generated prose does not change it; a wiki Entity marked `authorship: user` follows the vault roles in `principle-knowledge-notes`.
