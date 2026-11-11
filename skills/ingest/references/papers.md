# Papers — twelve-axis Paper Mode

Paper Mode compiles one Raw, one paper hub, N knowledge atoms in a per-paper folder named by citekey (`40. Paper Analyses/{citekey}/` unless the live policy places it elsewhere) and a few Wiki promotions. Success has two layers: (a) the notes cover the paper so the original need not be reopened, (b) they explain it better than the original. A paper that only needs light collection goes through Standard ingest instead (P-0 option).

Triggers: an explicit paper request, the papers lane or `category: Papers`, a DOI/arXiv/journal URL, or a converted document with Abstract and References. Announce Paper Mode inside P-0; no separate question. Question budget: exactly two, P-0 and P-1.

## P-0 — Purpose, scope and target RQ (question 1)

- Read Core Context once per session; check the paper's topic against the reuse axes actually registered in its §2 and the existing Wiki domains. Clearly outside the vault's scope: stop and offer (a) accept as a new area, (b) fold into the nearest existing area, (c) Standard collection only. Never widen the domain silently.
- One question carries both the Step 1 purpose and the target: list open research questions (`type: research-question`, status not answered or superseded) as options, plus: register a new RQ the owner states, a mothership draft (linked through `mainVaultRelated` only), none (`targetManuscript: none`, still twelve-axis), or simple collection (switch to Standard ingest and leave Paper Mode).
- Skip the purpose part when the task states a purpose or the candidate carries `collectionPurpose`. When the owner delegates ("알아서", "자동으로"), infer the purpose from the source and the registered §2 axes and record the inference and its reason in `collectionPurpose`.
- Record `collectionPurpose` (verbatim or stated inference) and `targetManuscript` (`"[[RQ-…]]"` or `none`). Link only an RQ the owner designates; never derive one from the title.
- Step 2 runs without a question: surface RQs already waiting for this paper (citekey `{surname}{year}` stem match in RQ `cites`, then `qmd` over the Wiki, keyword fallback) and, with a mothership, its related notes read-only. Record only stat-verified and owner-confirmed `mainVaultRelated` links in the Step 2 form; `mainVaultCmds` only as a registered reference copied exactly.

## P-1 — Type and strategy (question 2)

Classify from the Abstract and method headings and confirm with a one-line reason, together with the strategy:

| paperType | Signals |
| --- | --- |
| `quantitative` | hypotheses, sample, regression/SEM/ANOVA, p-values |
| `qualitative` | interviews, focus groups, coding, thematic analysis, trustworthiness |
| `theory-concept` | no empirical data; definitions, propositions, a proposed framework |
| `mixed-methods` | a quantitative and a qualitative strand with integration |
| `scale-development` | item development, EFA/CFA, validity as the aim |
| `meta-analysis` | systematic search, pooled effect sizes, PRISMA |

A paper outside the six (book review, editorial, tutorial) takes the nearest type, with the deviation recorded in the hub; no seventh type.

| Strategy | When | What is written now |
| --- | --- | --- |
| ① parallel fan-out | the runtime has subagents and the blueprint plans more than one batch of atoms | all atoms, 5–9 atoms per batch split along axis boundaries; each batch gets the SPEC, the Raw, its atom table, special notes and a self-check duty |
| ② single run by importance | no subagents, or one batch of atoms or fewer | hub draft → core axes → remaining axes → Wiki promotion |
| ③ progressive stub | the paper is long (over about 15,000 words) or the owner asks for "핵심만" | core axes in full; every other planned atom as `status: stub` with its Analysis Context and a one-line question; a stub is promoted later by ingesting its path |

Core axes (progressive default): quantitative S02·S03·S08·S09·S12; qualitative S02·S04·S08·S09·S12; theory-concept S04·S06·S08·S09·S12; mixed-methods S06·S08·S09·S12; scale-development S06·S07·S08·S09·S12; meta-analysis S04·S08·S09·S10·S12. Under 30 atoms, shrink the batch count in proportion. A progressive run is reported as progressive, never as complete. A subagent's self-check is advisory, never the gate.

## P-2 — Save Raw

Step 3 and Step 5 as in the main recipe: Raw in the Papers folder, `category: Papers`, verbatim `## Original Content`, conversion fields recorded (fidelity governs quotation). Resolve the DOI or full citekey against the actual paper; surname plus year is a search hint, never identity. Add `citekey`, `doi`, `targetManuscript`, same values as the hub. Zotero with Better BibTeX is optional: fill metadata and the registered citekey from it, and restore page numbers from its PDF. Without it, generate `authYearShorttitle`, set `citekeyProvisional: true` and put a `> [!warning] Provisional citekey` callout in the hub; on later registration the key is pinned, notes and folder are never renamed.

## P-3 — Hub and atoms

The twelve axes are coordinates, not a file count. A note is one knowledge atom: one concept, claim, distinction, mechanism or case, answering exactly one question. Thirty to a hundred or more atoms per paper is normal; density, not word count, decides.

Common skeleton (all types):

| S | Name | Meaning |
| --- | --- | --- |
| 1 | CITATION | full bibliography; held by the hub, never an atom |
| 2 | PURPOSE AND GENERAL RATIONALE | the broad aim and why it matters |
| 3 | FIT AND SPECIFIC RATIONALE | place in prior literature and the specific justification |
| 4 | PARTICIPANTS (varies) | who or what was studied |
| 5 | CONTEXT (varies) | setting, situation, scope of application |
| 6 | STEPS IN SEQUENCE (varies) | procedure, argument, design, development or review order |
| 7 | DATA (varies) | data, items, argument material, extracted fields |
| 8 | ANALYSIS (varies) | analysis, integration, conceptual work, synthesis |
| 9 | RESULTS (varies) | main findings, outputs, meta-inferences |
| 10 | CONCLUSIONS | how the results answer S02 |
| 11 | CAUTIONS (varies) | authors' warnings plus the analyst's reservations |
| 12 | DISCUSSION / WRITING VALUE | what to carry into the owner's own writing |

Type-specific `analysisStepName` values, copied exactly into the atom:

| S | quantitative | qualitative | theory-concept | mixed-methods | scale-development | meta-analysis |
| --- | --- | --- | --- | --- | --- | --- |
| 2 | PURPOSE AND GENERAL RATIONALE | PURPOSE AND GENERAL RATIONALE | PURPOSE AND GENERAL RATIONALE | PURPOSE AND GENERAL RATIONALE | PURPOSE | PURPOSE AND REVIEW QUESTION |
| 3 | FIT AND SPECIFIC RATIONALE | FIT AND SPECIFIC RATIONALE | FIT AND SPECIFIC RATIONALE | FIT AND SPECIFIC RATIONALE | FIT AND RATIONALE | FIT AND RATIONALE |
| 4 | PARTICIPANTS | PARTICIPANTS | CORE CONSTRUCTS / KEY CONCEPTS | PARTICIPANTS / DATA SOURCES FOR BOTH STRANDS | SAMPLES / PARTICIPANTS ACROSS STUDIES | CORPUS / STUDY SET |
| 5 | CONTEXT | CONTEXT | SCOPE CONDITIONS / INTELLECTUAL CONTEXT | CONTEXT | CONTEXT OF USE | CONTEXT OF THE REVIEWED FIELD |
| 6 | STEPS IN SEQUENCE | STEPS IN SEQUENCE | ARGUMENT IN SEQUENCE | DESIGN IN SEQUENCE | DEVELOPMENT PROCESS IN SEQUENCE | REVIEW PROCESS IN SEQUENCE |
| 7 | DATA | DATA | BUILDING BLOCKS / EVIDENTIARY BASE | DATA | DATA / ITEMS | DATA EXTRACTED FROM STUDIES |
| 8 | ANALYSIS | ANALYSIS | CONCEPTUAL WORK DONE | ANALYSIS AND INTEGRATION | ANALYSIS | ANALYSIS / SYNTHESIS |
| 9 | RESULTS | RESULTS | MAIN OUTPUTS | RESULTS / META-INFERENCES | RESULTS | RESULTS |
| 10 | CONCLUSIONS | CONCLUSIONS | CONCLUSIONS | CONCLUSIONS | CONCLUSIONS | CONCLUSIONS |
| 11 | CAUTIONS | CAUTIONS | CAUTIONS / BOUNDARY CONDITIONS | CAUTIONS | CAUTIONS | CAUTIONS |
| 12 | DISCUSSION / WRITING VALUE | DISCUSSION / WRITING VALUE | DISCUSSION / WRITING VALUE | DISCUSSION / WRITING VALUE | DISCUSSION / WRITING VALUE | DISCUSSION / WRITING VALUE |

These names are fixed literals, also embedded in `scripts/verify_paper.py`; `analysisStepName` matches them after case and whitespace folding only, so never add a parenthetical or paraphrase. Qualitative emphasis (researcher first, duration, trustworthiness) lives in the guiding questions below, not in the name.

Guiding questions per axis (S01 is always the hub's full citation; S10 asks how the results answer S02 unless stated):

- **quantitative** — S02 the broad aim and how the authors justify its general importance; S03 how the topic fits the prior literature and how that lineage becomes this study's specific rationale; S04 who was studied: number, characteristics, selection and sampling; S05 where the study took place and that setting's important features; S06 the main procedural steps in the order performed and how they relate (a Mermaid flowchart when useful, labels in double quotes); S07 what the data were (test scores, survey answers, frequencies), how collected, the researcher's role in collection; S08 which analyses and which question each was built to answer, naming techniques and software; S09 the primary results, statistics (β, p, CI) quoted verbatim; S10 how the authors claim the results answer S02; S11 the authors' stated limits plus the analyst's reservations on design, sample and interpretation; S12 everything of value (results, design, references, instruments, theory, inspiration) restated for `targetManuscript`.
- **qualitative** — S02, S03, S10, S12 as quantitative; S04 the researchers themselves first (who they are and their relation to the aim, participants and site), then participant number, characteristics and selection; S05 the site and its important features; S06 procedural steps in order with their duration and relations; S07 what the data were (field notes, interview transcripts, photos, diaries), how collected, the researcher's role; S08 which analysis and what it was meant to reveal, with software if any; S09 the primary findings, usually what was going on at the site, key participant quotes verbatim; S11 the authors' warnings plus the analyst's reservations, especially on how trustworthiness and believability were strengthened.
- **theory-concept** — S02 the big problem the paper tries to solve; S03 which gap, conflict or ambiguity in existing theory it targets; S04 the core concepts, each definition quoted verbatim, and how each differs from similar concepts; S05 how far the theory reaches: which situations, levels and conditions; S06 the argument in order (for example problem → critique of existing theory → redefinition → mechanism → propositions); S07 the material the argument is built from: prior studies, philosophers, classic theory, case examples; S08 the conceptual work actually done: redefinition, integration, separation, typology, mechanism, propositions; S09 the final outputs: framework, model, typology, propositions, concept map; S10 what the paper finally makes us see anew; S11 whether claims are untested, too broad or vague, hard to carry into empirical work; S12 what is usable now: definition sentences, quotable lines, the framework figure, propositions to turn into hypotheses, ways of distinguishing concepts.
- **mixed-methods** — S02 why mixing was needed: what quantitative alone and qualitative alone lacked; S03 how the topic was treated before and why mixing is required; S04 who the quantitative sample and the qualitative participants are, same group or different; S05 whether the two strands share a context; S06 (the key axis) the design type: explanatory sequential, exploratory sequential, convergent or embedded; S07 the quantitative and qualitative data separately, and where the two meet; S08 the quantitative analysis, the qualitative analysis and the integration (merging, connecting, building, joint display); S09 whether the strands confirm, conflict, complement or produce a new interpretation; S10 what mixing made better understood; S11 whether one strand is weak, the strands were only placed side by side, or it is two separate studies under a mixed label; S12 the design approach, joint display ideas, hints for follow-up designs. Key test: what the two strands made together.
- **scale-development** — S02 what is to be measured and why a new scale is needed; S03 the limits of existing scales and the distinction from similar constructs; S04 each sample (pilot, exploratory, confirmatory, revalidation) recorded per study; S05 which groups, cultures, languages and situations the scale is for; S06 item generation → expert review → pilot → EFA → CFA → validity → invariance; S07 item count, response format, subfactors, reverse and deleted items, with full item text verbatim only for openly licensed scales, otherwise summary plus source; S08 EFA/CFA, reliability (alpha, omega), convergent/discriminant and criterion validity, measurement invariance, translation and back-translation; S09 final factor and item counts, fit indices verbatim, practicality; S10 what the scale opens up for researchers; S11 validation limited to certain groups, cultural translation problems, shallowness of short forms, self-report bias; S12 usable items, translation cautions, differences from similar scales, the operational definition.
- **meta-analysis** — S02 the question the review answers; S03 why this review is needed now and the limits of earlier reviews; S04 number of included studies, search period and databases, inclusion and exclusion criteria; S05 which fields, populations, countries and situations were pooled; S06 search → deduplication → abstract screening → full-text review → final inclusion → coding → synthesis, with PRISMA counts when given; S07 what was extracted per study: effect sizes, sample information, variables, moderators, mediators, design, measurement; S08 for systematic reviews thematic grouping, quality appraisal and narrative synthesis, for meta-analyses effect-size computation, random/fixed effects, heterogeneity, publication bias, meta-regression (the two diverge only at S08 and S09); S09 overall effect, consistent patterns, moderation and mediation, under-studied areas, effect sizes verbatim; S10 what is now fairly certain and what remains uncertain; S11 quality of included studies, country or sample skew, publication bias, excessive heterogeneity (apples and oranges); S12 a map of the field, representative and core studies, frequently used variables, missing populations and contexts, sentences proposing follow-up research.

Each axis's guiding questions are a minimum scope, not a length cap. Expanding axes by type: quantitative S07·S08·S09 (one hypothesis, model or scale per atom); qualitative S08·S09 (one theme per atom); theory-concept S04·S09·S07 (one definition, distinction or proposition per atom; cases × conditions); mixed-methods S06·S08·S09 (strand results plus each integration point); scale-development S07·S08 (one validity-evidence type per atom; item text verbatim only for public scales); meta-analysis S04·S08·S09 (one effect cluster per atom).

Rules: one atom has exactly one `analysisStep`; no merged S08+S09 notes. A sub-idea that needs more than a paragraph becomes its own atom, linked both ways. A dense section collapsed into one or two atoms is under-decomposition. An axis with no real content gets zero atoms and `skipped ({reason})` in the Step Map; never silent omission, never boilerplate. A section with no obvious axis goes to the nearest one (cases usually S07) rather than leaving a hole. The purpose is a layer on full coverage, not a filter.

**P-3a — Blueprint.** Before any atom, list every H2/H3 of the converted text and fix each atom's filename `{Surname} {Year} - S{NN} {title}`, its one question, its mining location and its neighbour links. The output is the hub draft from [paper hub](../templates/paper-hub.md), `{Surname} {Year} - S00 Hub`: S01 Citation, Coverage Map, Step Map with every axis `planned`, Atom Catalog, and a temporary `> [!note] Compile Plan`. Check scale against the expanding axes above. No owner confirmation; the question budget stays two. Scan for an existing folder with the same citekey first.

**P-3b — Compile.** Write a SPEC (paper constants, Raw path, full atom filename list, link design, frontmatter example with `model`/`effort`, self-check) outside the vault, in session scratch. Write atoms from [paper atom](../templates/paper-atom.md) in the fixed order: H1 → `> [!info] Analysis Context` (paper, purpose, position, this atom's question with neighbours) → `## 쉬운 도입` → `## 정밀 해설` → `## 예시` → `## 원문 근거` → `## 개념 관계` (at least one direct link to a sibling atom, not via the hub) → optional `## 내 원고 맥락` / `## Open Questions`. Upstream targets 700–1,500 words of body per atom. Analyst additions are marked 【분석자 주】. Then finish the hub: every `planned` becomes `compiled`, `stub {M}건` or `skipped ({reason})`, the Compile Plan callout is deleted, Wiki Promotions are fixed.

**Evidence.** In `## 원문 근거`, each key statement gets `> [!quote] 원문 (p.{N}, §{section})`. The locator is page first (restored from a PDF when available), section only when pages are lost. Hard requirements: the quoted text is verbatim from the Raw's `## Original Content` and each quotation is located there independently (`grep -F` finds it); statistics (β, p, CI, fit indices), definitions and participant words are quoted verbatim; no summary or paraphrase inside a quote. Two to six quotations per atom is guidance, not a hard count.

## P-4 — Wiki promotion

Promote reusable knowledge to Terms when the field already names it, otherwise to Concepts (`layer: theory | method | scale | concepts`), and authors, journals and datasets to Entities, by Step 6's rules: update before create, clean-context update of existing pages, `explored: false` and `verificationStatus: unverified` on new pages, `model`/`effort` provenance, two-way links (the Wiki page's "Paper Analyses" section ↔ the atom's `related` and `## 개념 관계`). A Scale page is made only when the paper actually develops or validates a scale: `layer: scale`, the measured construct, the item count, a Psychometrics table with one row per study (sample, α/ω, CFA fit, notes; reliability and validity are sample-dependent, so they live in the table, not frontmatter) and the copyright callout — full item text only for an openly licensed scale, otherwise a summary plus the source; [concept](../templates/concept.md) carries that block. Promote only what the paper supports. Upstream's P-4 heading reads "no upper limit, lower bound 10–15"; that number is recorded here for traceability, not as a quota: promote what the paper supports and, when that is fewer, report the count and why instead of padding. There is no blanket Scale, RQ or Persona requirement; an existing Persona follows Step 7 only.

## P-5 — RQ sync

Only when `targetManuscript` names an owner-designated RQ: add the citekey to the RQ's `cites`, the S12 gist to `evidenceFor` or `evidenceAgainst`, and one line in its body. A mothership draft is reported through `mainVaultRelated` only; nothing is written to the mothership.

## P-6 — Index and log

Confirm the hub has no `planned` left and no Compile Plan callout. Add the hub only to the `index.md` Paper Analyses section (atoms never), recount Stats from the folders, add the Recent Ingests row. Append to `log.md`:

```markdown
## [YYYY-MM-DD] ingest-paper | {Surname} {Year} — {title}
- Purpose: {collectionPurpose}
- targetManuscript: {RQ link or none}
- Atoms: {count per axis; strategy}
- Wiki: {promoted and updated pages}
- Review: {P-7 summary, failures fixed or open}
```

Git does not replace either file; ingest does not commit or push.

## P-7 — Review

Run the package's mechanical gate, from the package root, on the paper folder, then read back:

```bash
python3 scripts/verify_paper.py "<paper analysis folder named by citekey>" [--vault VAULT] [--raw RAW]
```

`scripts/verify_paper.py` is this package's own verifier, written from the P-7 requirements below. It needs Python 3.9+ and PyYAML, reads only the vault, and writes nothing. The vault defaults to the nearest ancestor holding `index.md`, the Raw to the hub's `source`. Exit 0 prints `ALL PASS (mechanical)`; 1 means validation failures; 2 means a prerequisite or input could not be resolved (PyYAML missing, no single hub, unresolvable Raw, unknown `paperType`). Exit 0 is necessary, not sufficient. It checks:

1. every note's frontmatter parses as a mapping without duplicate keys or leftover `{{…}}` slots; hub and atoms carry ISO `date_created`/`date_modified` (modified not earlier), `model` and `effort`.
2. hub `type: paper-hub`, `status: active`, `citekey`, `targetManuscript` (`none` or an RQ wikilink), a known `paperType`, no leftover `[!note] Compile Plan`; each atom `type: paper-analysis`, `paperType` and `citekey` equal to the hub's, exactly one ` - S{NN} ` filename marker equal to the integer `analysisStep` in 2–12, `analysisStepName` equal to the type's literal name above (case and whitespace folded only), `paperHub` linking the hub, `source` naming the paper's Raw, `status` `completed` or `stub`.
3. every atom, stub included, has `> [!info] Analysis Context`; a completed atom has `## 쉬운 도입`, `## 정밀 해설`, `## 예시`, `## 원문 근거`, `## 개념 관계` once each, non-empty (a section holding only a `---` separator or comments is empty) and in that order; an S12 atom needs only `## 개념 관계`; a stub needs only Analysis Context.
4. `## 개념 관계` of each completed atom links at least one sibling atom (not the hub, not itself).
5. every `[!quote]` is found contiguously in the Raw's `## Original Content` after NFC, curly-quote/dash/ellipsis folding and whitespace collapse — Unicode minus `−` is never folded to `-`, and no line is skipped for being short, numeric or a negation; each quote header carries a page or § locator; an empty quote fails; a completed non-S12 atom with no located quote fails.
6. Atom Catalog links ↔ atom files both ways, with per-step counts; Coverage Map atom links ⊆ Catalog and ⊆ files; each Step Map row S01–S12 appears once, has the type's step name, an integer Atoms cell equal to the files carrying that `S{NN}`, stated stub counts, no `planned`, and `skipped (reason)` only where no atom exists.
7. every leaf heading (H1–H6; a heading with deeper headings under it is a parent and needs no row of its own, and a parent's row never covers its leaves) of the Raw's `## Original Content` has a Coverage Map row naming an atom or a stated omission; a row matching several identical headings, or an ambiguous prefix, fails rather than counting as coverage.
8. `index.md` links the hub and no atom.
9. atoms live directly in the paper folder; a subfolder holding Markdown notes fails as unsupported, never silently skipped.

Stubs, S12 atoms with no quote, and headings covered only by a stated omission are listed as not fully verified. A mechanical PASS is quantitative only; it is not semantic fidelity and not the qualitative PASS. An atom with zero located quotes or insufficient source evidence is never reported as fully verified. Then read the hub, every atom, the Raw and `index.md` back and check each item; fix and rerun on failure:

- frontmatter parses; required keys, `model`/`effort`, `paperHub`, integer `analysisStep` 2–12 and its exact `analysisStepName`, `status` `completed` or `stub`;
- every atom has Analysis Context, the required sections in order, and at least one sibling-atom link;
- every quotation is found verbatim in the Raw's `## Original Content`;
- the Atom Catalog and the actual atom files match both ways; every Coverage Map section points at an atom or a stated omission; no Step Map `planned` remains;
- `index.md` lists the hub and no atom; the `ingest-paper` log entry exists.

The orchestrator runs `verify_paper.py` itself; a subagent's self-check is advisory. Passing shows structure and verbatim presence, not faithfulness: it does not prove an atom reads the paper correctly or covers it. Also read two long sections against their atoms (decomposition), one atom per axis including S09–S12 (exposition), and spot-check that quotes support the claims they back. Report type, strategy, atom count per axis, promoted pages, unfinished axes and the P-4 shortfall if any; then Step 10.

## Failure modes

Summary-card atoms; under-decomposition; coverage holes; fabricated pages or passages; missing provenance; a citekey that does not match RQ `cites`; silent scope expansion; writes into a mothership; RQ not synced; atoms listed in `index.md`; atoms written without a Blueprint.
