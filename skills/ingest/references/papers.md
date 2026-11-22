# Papers

A paper goes through the ordinary Steps of [ingest](../SKILL.md). This file adds only what a paper needs on top: its original, its identity and its Entity. Apply it to an explicit paper request, the papers lane or `category: Papers`, a DOI, arXiv or journal URL, a citekey, or a converted document with Abstract and References.

## Original retrieval

- Retrieve the original through its DOI, publisher or author repository; reuse its Raw when the vault already holds one, otherwise preserve it under Steps 3 and 5 with `category: Papers`.
- For an explicitly researched Term, retrieve each original its evidence requires the same way. For a Term extracted from one source, attribute secondary claims to the selected source and record the original in `referenced` without fetching it.
- Record what was actually inspected in `## Ingest Notes`, including an abstract-only or partial reading. A paywalled or unobtainable full text stays unread; never compile it from the abstract as if read.

## Citekey and DOI

- Resolve the DOI or full citekey against the actual paper; surname plus year is a search hint, never identity.
- Put `citekey` and `doi` on the Raw and on the paper Entity, same values on both.
- A citekey the owner's reference manager already assigned may be reused as given. Otherwise generate `authYearShorttitle`, set `citekeyProvisional: true`, and say so in the report; a later registered key is recorded, and notes are never renamed for it.

## Paper Entity

- The paper Entity is the paper's hub: create it from [paper](../../principle-knowledge-notes/templates/entity/paper.md) or update the existing one by Step 6's Entity rules, writing only to its `## From Sources` auto zone.
- Its auto zone lists the paper's Raw, the Terms, Concepts and Guides compiled from it, and dated source-grounded facts, each citing the Raw.
- Every author whose real name the paper confirms is a person Entity by Step 6; a journal, lab or dataset is an Entity of its required type only when the analysis finds it significant.
- Compile Terms and Concepts only for what the paper supports, updating existing pages before creating; a shortfall is reported, never padded.
