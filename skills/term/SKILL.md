---
name: "term"
description: "Apply when the user asks what a word, acronym or established field term means (not a method one author coined, and not a named product, person or organization), or uses one the vault's wiki has no page or alias for: research it and write or update its Term page in the wiki from the Term template. Also use when the owner asks to define, create, look up or update a Term note for a word that is a field term; a Concept or Entity the owner labels a Term is handed off, not written as one. A named product, person or organization belongs to entity, and material handed over to compile belongs to ingest."
license: MIT
---

# Term

Research one field term and leave the wiki with one canonical Term page for it. A word is a candidate when the user asks about it or newly uses it and the wiki has no page or alias for it. Open each principle named at a step by reading `../<principle>/SKILL.md` before acting on that step; `principle-knowledge-notes`' Writing one page governs roles, lookup, title, form, entity links, the work note and the report.

## Step 1 — Resolve the vault roles and the target

Open `principle-knowledge-notes` and `principle-editing`, and resolve the roles and the Terms folder. A vault with no registered Terms folder takes Terms into its Concept folder, and the report says so. Confirm by the principle's criteria, not the owner's label, that the word is a Term; when it is a Concept or Entity, name that kind and why, and ask once before writing.

## Step 2 — Look the term up in the vault

Look it up as the principle describes, adding `obsidian unresolved verbose` filtered to the names, which shows links that already wait for the page. Updating an existing page, open `principle-writing`; a new related sense joins it.

- Fold an empty or stub wiki page for the same referent into the Term: copy its content and properties, leave the stub itself as it is (renaming, moving or emptying it would break or rewrite links in Raw and work notes), and report it with its backlinks so the owner can retire it.
- Retarget links to the same referent at the Term by editing the link inside wiki pages, keeping their display text (`[[이키가이]]` → `[[Ikigai|이키가이]]`); an alias alone does not resolve a link. Outside the wiki only the work note changes (Step 5); list the rest as candidates.

## Step 3 — Research

Read the field's own definitions (dictionaries, textbooks, standards, glossaries, peer-reviewed work) and the owner's notes that mention the term. Open `principle-archival`.

- Compare studies by the question they answer: what was done, who or what was measured, the unit and denominator, the result and its limits. Keep different outcomes distinct, label hypotheses, and separate original observations from replications and pooled estimates.

## Step 4 — Write the page

Fill [term](assets/term.md), using only the sections the term needs. Open `principle-writing` and `principle-markdown`.

- Never title it with the abbreviation or a translation alone (`Work Breakdown Structure (WBS)`). `domain` holds quoted English field wikilinks.
- Start with the definition and the finding or boundary that matters most. Explain it with a concrete example and distinguish the closest confusable idea. Use a table or formula for a worked numerical comparison. Preserve a superseded definition with its date and source.
- Cite empirical, quantitative and historical claims at the passage, table or figure that supports them, linking the first author's surname and year to that location. A footnote only for a quotation, method detail or caveat that would interrupt the explanation; check quoted wording against the original.
- Personal Insights holds only context found in the owner's notes, quoted accurately and linked; keep the owner's observation apart from a study's outcome, and suggest a separate insight note only when it stands on its own.
- Link to the whole Term, never to one of its sections, so the page stays the single target for the referent.
- Related Terms lists up to two notes whose wikilinks resolve in this vault, each with a nested relationship bullet; omit unfilled slots rather than substituting missing targets. One relevant term without a page may follow as the final top-level bullet, a bare `[[Term]]` with its nested relationship bullet; create no page for it and use that unresolved link nowhere else. Write other missing terms as plain text.
- References lists each cited work once, unnumbered, in the owner's research style where known: an existing source note by wikilink, or the first author and year linked to the full text, keeping coauthors, title, venue, DOI, the available Raw and the scope actually inspected. The precise locator stays beside the claim.

## Step 5 — Link the work note

Link the term from the work note as the principle describes. Open `principle-editing`.

## Step 6 — Read back and report

Read back as the principle describes. Every body wikilink resolves except the single planned final Related Terms bullet: in authored prose, remove other unresolved link markup while keeping useful text, or retarget it to a verified page for the same referent; in quoted or preserved text, report it and leave the text unchanged.

Before the footer, list Step 2 candidates and any Concept-folder fallback.
