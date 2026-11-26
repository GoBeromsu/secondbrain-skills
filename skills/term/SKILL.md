---
name: "term"
description: "Apply when the user asks what a word, acronym or established field term means (not a method one author coined, and not a named product, person or organization), or uses one the vault's wiki has no page or alias for: research it and write or update its Term page in the wiki from the Term template. Also use when the owner asks to define, create, look up or update a Term note for a word that is a field term; a Concept or Entity the owner labels a Term is handed off, not written as one. A named product, person or organization belongs to entity, and material handed over to compile belongs to ingest."
license: MIT
---

# Term

Research one field term and leave the wiki with one canonical Term page for it. The answer the user asked for comes first; the page is written after, and the report names it.

A word is a Term candidate when the user asks about it or newly uses it and the wiki has no page or alias for it. When a page or alias already exists, the run only adds claims the page does not yet carry. Open each principle named at a step by reading `../<principle>/SKILL.md` before acting on that step.

## Step 1 — Resolve the vault roles and the target

Read the vault guideline (live policy) for the folders that play the wiki, source and work roles and for the folder Terms go into. When the guideline leaves out a mapping this run needs, stop before writing and run `onboard`'s Vault roles step, which asks the owner once and records the answer; never guess a folder. Running as a subagent, return the missing mappings to the main thread instead, which asks once for all of them. A vault with no registered Terms folder takes Terms into its Concept folder, and the report says so.

Open `principle-knowledge-notes` and `principle-editing`. Confirm the word is a Term by the principle's criteria, not by the owner's label; when it is a Concept or Entity, follow the principle's rule for a mislabeled request instead of writing a Term.

## Step 2 — Look the term up in the vault

Run every `obsidian` command with `vault=<resolved vault>` and give `backlinks` the candidate page as `path=`, as [`obsidian-cli`](../obsidian-cli/SKILL.md) requires; an untargeted command reads whatever vault or note has focus.

Search with `obsidian-cli`, which matches what Obsidian itself resolves: `obsidian search query=<name>` for each title, alias, translation and spelling variant, `obsidian unresolved verbose` filtered to those names, and `obsidian backlinks path=<page>` for an existing page.

- An existing page or alias for the same referent is updated, never duplicated; open `principle-writing` and follow [updating](../ingest/references/updating.md). A new related sense joins the existing page.
- Fold an empty or stub wiki page for the same referent into the Term: copy its content and properties into the Term, leave the stub itself as it is (renaming, moving or emptying it would break or rewrite links in Raw and work notes), and report it with its backlinks so the owner can retire it.
- Retarget links to the same referent at the Term by editing the link inside wiki pages, keeping their display text (`[[이키가이]]` → `[[Ikigai|이키가이]]`); an alias alone does not resolve a link. Outside the wiki, only the work note the conversation is about may change, and only its first mention; list the rest as candidates in the report.

## Step 3 — Research

Read the field's own definitions (dictionaries, textbooks, standards, glossaries, peer-reviewed work) and the owner's notes that mention the term. Open `principle-archival`.

- Compare studies by the question they answer: what was done, who or what was measured, the unit and denominator, the result and its limits. Keep different outcomes distinct, label hypotheses, and separate original observations from replications and pooled estimates.

## Step 4 — Write the page

Fill [term](assets/term.md). Open `principle-writing` and `principle-markdown`.

Naming:

- Title the page with the full original-language name, followed by the abbreviation in parentheses when one is in common use (`Work Breakdown Structure (WBS)`); never the abbreviation or a translation alone.
- Put abbreviations, translations, former names and spelling variants in `aliases`. Group related senses in one page; qualify unrelated homonyms by field.

Format:

- About five subject tags; `domain` as quoted English field wikilinks; `source` lists vault notes as quoted wikilinks.
- Link each existing vault entity at its first eligible body mention, including in references and footnotes, and existing Raw notes by wikilink rather than bare filename.
- A template the vault registers for this kind wins for frontmatter keys and headings. English section headings, in the template's order, using only the sections the term needs.

Content:

- Start with the definition and the finding or boundary that matters most. Explain it with a concrete example and distinguish the closest confusable idea. Use a table or formula for a worked numerical comparison. Preserve a superseded definition with its date and source.
- Cite empirical, quantitative and historical claims at the passage, table or figure that supports them, linking the first author's surname and year to that location. Use a footnote only for a quotation, method detail or caveat that would interrupt the explanation, and check quoted wording against the original.
- Personal Insights holds only context found in the owner's notes, quoted accurately and linked; keep the owner's observation apart from a study's outcome, and suggest a separate insight note only when it stands on its own.
- Link to the whole Term, never to one of its sections, so the page stays the single target for the referent.
- Under Related Terms, list up to two relevant notes whose wikilinks resolve in this vault, each with a nested relationship bullet. Omit any unfilled existing-note slots rather than substituting missing targets. You may add one relevant term without a page as the final top-level bullet: a bare `[[Term]]` with a nested relationship bullet. Do not create its page or reuse that unresolved link elsewhere in the body; write any other missing terms as plain text.
- References lists each cited work once, unnumbered, following the owner's research style where known: link an existing source note by wikilink, or the first author and year to the full text; keep coauthors, title, venue, DOI, the available Raw and the scope actually inspected. The precise locator stays beside the claim.

## Step 5 — Link the work note

When the conversation is about a note in the work area, turn the first mention of the term in that one note into `[[Term]]` (or `[[Term|original text]]`) and change nothing else. The note the conversation is about is one the user named or is working in; a note found only by searching the vault is not it, and no other name in it is linked. Open `principle-editing`.

## Step 6 — Read back and report

Read back every note written, as `principle-editing` describes. For each written wiki page, scan the final text for entity titles and aliases, including in quotations, Personal Insights, references and footnotes. Checking that existing links resolve does not catch missing links. Keep quoted and preserved text unchanged: when the only mention is in such a passage, name and link the entity in your own prose beside it (e.g. `[[Trial Note]] records the owner's question about [[Product]]: "…"`). A link to the quoted note alone does not link the entities it mentions.

Check that all body wikilinks resolve except the single planned final Related Terms bullet. In authored prose, remove any other unresolved wikilink markup while keeping useful text, or retarget it to a verified page for the same referent. Report unresolved links in quoted or preserved text without changing that text.

In the standalone report, put decision-changing principles, Step 2 candidates and any Concept-folder fallback before the footer. When routed through secondbrain-mode, return the findings and wiki outcomes separately rather than the standalone report.

The standalone final line is `Wiki: created [[X]], updated [[Y]], failed [[Z]] (reason)`; omit empty clauses. Include only read-back-confirmed changes in the live policy's wiki area, each page once by whether it existed before the task. Use `failed [[Z]] (reason)` only for an attempted wiki write that failed. Omit unattempted work, Raw and other outside-wiki notes, including work-note links. Omit the line when there are no successful or failed wiki writes. Nothing follows it.
