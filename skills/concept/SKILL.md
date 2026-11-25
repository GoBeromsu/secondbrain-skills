---
name: "concept"
description: "Apply when the user explores a new methodology, framework, conceptual model, technique or pattern (not a named product or a field term), or an idea one author named, that the vault's wiki has no page or alias for: research it and write or update its Concept page in the wiki from the Concept template. Also use whenever the owner asks to explain, create or update an idea, method or framework note. Material the owner hands over to compile belongs to ingest, even when it is about a method; a request to save it without compiling belongs to capture."
license: MIT
---

# Concept

Research one idea and leave the wiki with one canonical Concept page for it. The answer the user asked for comes first; the page is written after, and the report names it.

When a page or alias for the idea already exists, the run only adds claims the page does not yet carry. Open each principle leaf named at a step by reading `../<leaf>/SKILL.md` before acting on that step.

## Step 1 — Resolve the vault roles and the target

Read the vault guideline (live policy) for the folders that play the wiki, source and work roles and for the Concept folder. When the guideline leaves out a mapping this run needs, stop before writing and run `onboard`'s Vault roles step, which asks the owner once and records the answer; never guess a folder. Running as a subagent, return the missing mappings to the main thread instead, which asks once for all of them.

Open `principle-vault-roles`, `principle-resolve-target` and `principle-note-kinds`. Confirm the idea is a Concept: a model, framework or method one author named, or a reusable idea, technique or pattern without an established field name. Hand a real field term to `term`, a named individual to `entity`, and a solved procedure to a Guide.

## Step 2 — Look the idea up in the vault

Run every `obsidian` command with `vault=<resolved vault>` and give `backlinks` the candidate page as `path=`, as [`obsidian-cli`](../obsidian-cli/SKILL.md) requires; an untargeted command reads whatever vault or note has focus.

Search titles, aliases, translations and spelling variants with `obsidian search query=<name>`, and `obsidian backlinks path=<page>` for an existing page. An existing page for the same idea is updated, never duplicated; open `principle-revise-and-consolidate` and `principle-preserve-voice`, and follow [updating](../ingest/references/updating.md).

## Step 3 — Research

Read the coiner's own account first, then the strongest independent treatments and the owner's notes that mention the idea. Open `principle-provenance` and `principle-standalone-note`.

- Every web page read stays a `[label](URL)` link on the page. Save a Raw only when the owner handed the material over and asked to ingest or save it; that is `ingest`'s job.
- Note for each claim what its evidence does not establish.

## Step 4 — Write the page

Fill [concept](assets/concept.md). Open `principle-not-a-research-log`, `principle-plain-tldr`, `principle-quotation-attribution`, `principle-note-shape`, `principle-draw-structure`, `principle-frontmatter`, `principle-link-form` and `principle-markdown-blocks`.

Naming:

- Title it with the idea's full name in its original language, whichever language that is, followed by the common abbreviation in parentheses when one is in use (`Getting Things Done (GTD)`). Put abbreviations, translations, former names and spelling variants in `aliases`.

Format:

- Frontmatter keys in alphabetical order; about five subject tags. `layer` is `concepts`, or `theory`, `method` or `scale` for a paper-derived Concept.
- `source` lists vault notes as quoted wikilinks. An external URL in frontmatter goes only under a `*_url` key as a plain URL; every other web reference is a `[label](URL)` in the body. No raw URL anywhere in the body.
- An entity with a page in the vault is a `[[wikilink]]` in the body and a quoted wikilink in frontmatter. Quoted words stay as written, so when such a name appears only inside a quotation, link it once in your own prose beside the quotation.
- A template the vault registers for this kind wins for frontmatter keys and headings.
- English section headings, in the template's order. No `---` in the body and no `status` key.

Optional blocks, kept only when they apply and deleted otherwise:

- The Contradiction callout only when a source explicitly conflicts with an existing claim; keep both, attributed, with the uncertainty stated. Silence is not a contradiction.
- The Bias Check for `confidence: high` or synthesis-heavy pages, with both its lines filled.
- The scale block (Copyright caution through Use Cautions) and the `measuredConstruct` and `itemCount` keys only for `layer: scale`, when the paper develops or validates the scale.

Content:

- Overview says what the idea offers the owner's work, in the page's own words.
- Details answers reader questions (how it works, why it holds, where it applies, where it stops), compiled from every source rather than walking one source in order.
- Terms links the field terms the idea uses; Related links neighbouring pages with the reason once.

## Step 5 — Link the work note

When the conversation is about a note in the work area, turn the first mention of the concept in that one note into `[[Concept]]` (or `[[Concept|original text]]`) and change nothing else. The note the conversation is about is one the user named or is working in; a note found only by searching the vault is not it, and no other name in it is linked. Open `principle-preserve-unrequested`.

## Step 6 — Read back and report

Open `principle-read-back` and read back every note written. Report candidates and each principle leaf that changed a decision and what it changed before the closing Wiki line. The final line is `Wiki: created [[X]], updated [[Y]]`, with any failure on the same line.
