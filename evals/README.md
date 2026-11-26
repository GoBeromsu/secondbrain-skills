# Evals

Evals run only against fixture vaults in this folder, never against a real vault.

| Path | What it is |
| --- | --- |
| `lint-links/` | Regression case for `skills/lint/scripts/link-lint.py` link-form rules. `scripts/validate.py` checks that the script reproduces `expected.tsv`. |
| `fixture-vault/` | Shared fixture vault. `Guideline.md` is its live policy. |
| `lint/evals.json` | skill-creator eval set for `lint`: one case per check, with the findings it expects, plus `trigger_evals` for description optimization. |
| `lint/run.py` | Runs the lint scripts on the fixture vault and grades the mechanical cases in `lint/evals.json` (those with `paths`). The report-only case and `trigger_evals` need agent runs, below. |
| `term/`, `concept/`, `entity/`, `secondbrain-mode/` `evals.json` | skill-creator eval sets for the knowledge skills: agent cases (`evals`) whose `expectations` each name a programmatic check, plus `trigger_evals` for description optimization. |
| `gen_evals.py` | Regenerates all four knowledge-skill `evals.json` files (`python3 evals/gen_evals.py`). |
| `agent_run.py` | Runs those agent cases through `claude -p` on a temp copy of the fixture vault, new skill and 0.28.1 baseline, and grades every expectation. |
| `trigger_run.py` | Loads the whole plugin and records which skill each trigger query invokes, so siblings compete; also counts auto-invocations of `principle-*` and `secondbrain-mode`, which must be 0. |
| `skill_creator_trigger.py` | Runs skill-creator's `run_eval.py` / `run_loop.py` with one project dir per query, so parallel workers do not see each other's temporary command. |
| `baseline.sh` | Materializes a skill from a past release as skill-creator's `old_skill` baseline. |
| `results/` | Workspaces and run outputs. Gitignored. |

## Fixture vault

`Guideline.md` gives each role a folder name different from the owner's vault, so a skill that hardcodes a path fails: wiki is `Knowledge/`, source (Raw) is `Sources/`, work is `Projects/`. `ENTITY-UNLINKED` identifies entities by the Entity folders declared in the guideline, with `layer: entities` as a fallback. The status exception covers lifecycle types (`project`, `task`) and the owner's declared book entities carrying reading progress.

Clean sample pages, which must produce no finding:

- the person `Knowledge/People/Jane Doe.md` (`authorship: user`, with the owner's impressions)
- the organization `Knowledge/Organizations/Northwind Labs.md` and the product `Knowledge/Products/Lumen Notes.md`
- the term `Knowledge/Terms/Backlink.md`, the concept `Knowledge/Concepts/Spaced Repetition.md` and the MOC `Knowledge/Maps/Tools MOC.md`
- the Raw `Sources/2026-11-20 Lumen Notes launch post.md`, the work note `Projects/Lumen Notes Trial.md` and `Guideline.md`

Agent cases also use the work note `Projects/Lumen Notes Import Plan.md`, which mentions transclusion, progressive summarization and Readwise Reader twice each (only the first mention may become a link), and the Raw `Sources/2026-11-25 Northwind Labs leadership update.md`, the news for the person-update case. The Guideline maps Guides to `Knowledge/Guides/` (`layer: guides`) and the owner's permanent notes to `Notes/`. The fixture root's `AGENTS.md` maps the ingest records to `Knowledge/index.md` and `Knowledge/log.md`.

`Knowledge/Broken/` holds one deliberately broken note per check; `Broken Link.md` also carries a link to a missing heading (marksman) and a missing `related` target (Obsidian CLI). `Spaced Repetition.md` names an Entity inside a quote, which must not be reported. The hiring post in `Sources/` and the weekly review in `Projects/` each carry a `status` that does not belong there. The Raw and the work note also mention Entities without links and use `---`, which shows that those checks only look at the wiki role.

`.obsidian/` makes the folder open as a vault. `.marksman.toml` lets marksman treat it as a workspace.

## Running the lint eval

```bash
python3 evals/lint/run.py          # python path (link-lint.py --checks all) and marksman path
python3 evals/lint/run.py --cli    # also obsidian-lint.py; Obsidian must already have fixture-vault open
```

Each case names the paths it applies to. A case passes on a path when every expected finding is reported and none of its clean files has a finding; a final row per path fails on any finding no case expects. A script that crashes, prints a malformed line, or whose `# violations` total disagrees with its lines counts as not run, and every row of that path fails. The runner also stops if `evals.json` names a missing fixture file or if its policy differs from the wiki folder, Entity folders, lifecycle types, or reading-progress book types declared by `Guideline.md`. Without `--cli`, or when Obsidian does not have the fixture open, the CLI path does not run; `obsidian-lint.py` never opens or switches a vault itself. Only open the fixture in Obsidian when no other session depends on which vault is focused.

## Baseline against new

The baseline is release 0.28.1, commit `1c73d0b`. skill-creator compares a changed skill with its snapshot (`old_skill`), and the new version's pass rate must be the same or higher.

```bash
evals/baseline.sh lint             # writes evals/results/lint-workspace/old-skills/ (the whole skills/ tree)
python3 evals/lint/run.py --skill-dir evals/results/lint-workspace/old-skills/lint \
  --json evals/results/lint-workspace/old_skill.json
python3 evals/lint/run.py --json evals/results/lint-workspace/new_skill.json
```

`baseline.sh <skill> [commit]` works for any skill that exists at that commit. It extracts every skill of that commit, so links from the snapshot to sibling skills (`../ingest/...`) still resolve; point the `old_skill` subagent at `old-skills/<skill>`. A baseline without the policy checks only runs its link-form rules, so it gets credit just for those.

Agent-level runs follow skill-creator's "Running and evaluating test cases": for each case in `lint/evals.json`, give one subagent `skills/lint` and another the snapshot, use the same `prompt`, and save the outputs to `evals/results/lint-workspace/iteration-<N>/<eval_name>/with_skill/outputs/` and `.../old_skill/outputs/`. Then grade each case against its `expectations` and aggregate the results with skill-creator's `aggregate_benchmark`.

For description optimization, extract the trigger set and pass it to skill-creator's `run_loop.py`:

```bash
python3 -c "import json; json.dump(json.load(open('evals/lint/evals.json'))['trigger_evals'], open('evals/results/lint-workspace/trigger-evals.json', 'w'), indent=2)"
```

### Recorded runs

| Date | Version | Path | Pass rate |
| --- | --- | --- | --- |
| 2026-11-26 | 0.28.1 snapshot (`1c73d0b`) | python + marksman | 4/16 |
| 2026-11-26 | feat/sb-lint | python + marksman | 16/16 |

Both runs grade the same 16 rows: a path that cannot run fails every row it owns. The 0.28.1 baseline has no policy checks and no marksman script, so only its link-form rows pass. The CLI path (`--cli`) was not run on the fixture: opening it in Obsidian would switch the owner's open vault.

## Running the knowledge-skill evals

Every run uses `claude -p --model opus` with `--setting-sources project,local --strict-mcp-config` and `--plugin-dir` set to the plugin under test, so installed user plugins (including a released secondbrain-skills) and MCP servers stay out. Agent runs get an `obsidian` stub on PATH and `Bash(obsidian:*)` denied: the real CLI would open or switch the owner's vault.

```bash
python3 evals/agent_run.py term                  # new skill and 0.28.1 baseline -> results/term-workspace/iteration-1
python3 evals/agent_run.py term --config new --iteration 2
python3 evals/agent_run.py term --grade-only --iteration 1
python3 evals/trigger_run.py                     # whole-plugin trigger routing, 3 runs per query
SKILL_CREATOR=<skill-creator dir> PATH=<claude shim>:$PATH \
  python3 evals/skill_creator_trigger.py run_loop --eval-set evals/results/term-workspace/trigger-evals.json \
  --skill-path skills/term --model opus --max-iterations 5 --timeout 90 --report none
```

The `claude` shim for skill-creator's scripts adds `--setting-sources project,local --strict-mcp-config`. The baseline for `term`, `concept` and `entity` is 0.28.1's `principle-knowledge-notes`, which held their templates; `secondbrain-mode` has no 0.28.1 counterpart, so its baseline gets the whole 0.28.1 skills tree.

- **Routing:** A finished background worker must open the requested skill. Query/verify require successful file-level reads of the case's relevant notes; opening only the skill does not count. Every changed wiki path needs a successful worker tool result. For shell results, the grader accepts exact literal file operands from `cat`/`head`/`tail` reads, `touch`, and single-output `cat`/`echo`/`printf` redirects (including a quoted `cat` here-doc). Dynamic paths, compound commands and paths merely echoed in an argument are not attribution. Parent writes, including visible relative shell redirects, fail the row.
- **Report:** Verify requires an affirmative current-role conclusion, not a question, hypothesis, rumor, unconfirmed claim or attribution alone, and a citation to the decisive source note. The mode grader checks all top-level assistant text in the stream, not just terminal summaries: the parent stays silent until trusted worker completion, then gives exactly one answer without wiki-work narration, including in `principle-` lines. Explaining product behavior, note-taking mechanics or a principle decision is allowed; reporting or offering wiki edits is not. The report-only query and verify cases do not authorize record writes. An expressly approved routed write-back can update only the records prescribed by its skill (query: index and log; verify: log). Mode case 9 declares the Query folder and seeds the index and log only in its disposable vault copy.
- **Footer:** The only `Wiki:` line comes last and has comma-separated created, updated and failed outcomes in that order, omitting empty clauses. Each failure needs a parenthesized reason (which may contain nested parentheses) and a corresponding structured or supported shell write error. A failed-only footer is valid; optional footer rows require no footer when there are no wiki outcomes. Source notes, work notes and unattempted work do not appear.
- **Ingest and lint:** Exactly one new Raw preserves the handed-over article verbatim and ends the excerpt with a standalone `<!-- end-original-content -->` marker. The final occurrence separates preserved text from authored sections, including chapter Reading Notes. Legacy Raws without it have no unambiguous lint boundary and are not rewritten. The owner's existing impressions must move byte-exact to a dated note with reciprocal links. Lint requires a wiki write unless the row is optional and checks changed wiki pages plus any changed source pages in mode. It treats external citation labels as body mentions and does not count frontmatter links as body links.

The runner saves `staged-SKILL.md` (when there is an entrypoint) and `skills-tree-manifest.json` before launch. In `outputs/run.json`, `skill_sha256` hashes the staged entrypoint and `skills_tree_sha256` hashes the staged tree manifest (sorted relative paths and content digests, encoded as compact JSON). `provenance_verified` requires a successful run, the staged plugin in the parent init event, and a successful `Read` of the exact staged entrypoint that returns matching file content. A matching excerpt establishes read provenance, not that the whole file was read or its instructions followed. `skill_read_by` distinguishes `parent` from `worker`; a worker read does not establish that the parent read the skill. Bash and Skill calls do not count. Path comparisons use only spellings captured at launch, not aliases resolved during grading.

`--skills-root DIR` replaces the full staged skills tree for the `new` config, including the new half of `--config both`. Pass the directory containing `<skill>/SKILL.md`, not a single skill's folder. The override does not affect baseline or `--grade-only` runs.

`--grade-only` runs no agents but overwrites grading and derived evidence in the selected iteration; copy a retained iteration to a fresh number first. It refreshes provenance metadata from the retained transcript and staged skill bytes, without changing grading expectations.

### Recorded knowledge-skill runs (2026-11-26)

| Skill | R4 iteration | `with_skill` | 0.28.1 `old_skill` |
| --- | --- | --- | --- |
| term | 70 | 27/27 | 9/27 |
| concept | 50 | 19/19 | 8/19 |
| entity | 50 | 39/39 | 14/39 |
| secondbrain-mode (R4 final run, stream regrade) | 70 | 65/69 | 35/69 |
| secondbrain-mode (historical i14 traces, stream regrade) | 114 | 49/69 | 37/69 |

Scores pool assertion rows. Mode and term i70 were fresh R4 runs; i70 predates the skill change and case 9 below. The stream regrade drops mode `with_skill` i70 from 68/69 (cases 1, 2 and 7) and i114 from 53/69 (cases 1, 3, 5 and 7); `old_skill` is unchanged at both iterations. Mode i70 vs i114, pass → fail: `with_skill` 2.8 (duplicate `Wiki:` footer); `old_skill` 1.2 (wiki narration) and 6.3 (no affirmed current role). The `with_skill` rows newly passing are 3.2, 3.5, 4.1–4.6, 4.9, 5.1–5.2, 6.1, 6.2, 6.4, 8.3, 8.4 and 8.8; no `old_skill` rows newly pass.

#### R4 variance trials (`with_skill`)

| Skill / case | Iterations | Saved grades, in iteration order |
| --- | --- | --- |
| Mode 2 — concept | 80–82 | 8/8, 8/8, 8/8 |
| Mode 3 — entity | 50–52 | 8/8, 8/8, 8/8 |
| Mode 4 — ingest | 60–62 | 12/12, 12/12, 12/12 |
| Mode 5 — report-only query | 60–62 | 8/8, 8/8, 8/8 |
| Mode 6 — report-only verify | 63–65 | 6/6, 6/6, 6/6 |
| Term 2 | 50–52 | 9/9, 9/9, 9/9 |
| Term 3 | 60–62 | 10/10, 10/10, 10/10 |
| Mode 9 — approved query write-back, first wait revision | 90–92 | 0/9 (timeout), 7/9, 0/9 (timeout) |
| Mode 9 — approved query write-back, final wait revision | 96–98 | 8/9, 8/9, 8/9 |

Earlier variance trials retain their saved rubric, except mode 2 (i80–82), which was stream-regraded without a score change.

Mode i90 regression checks: case 2 **7/8** and case 6 **5/6** (both emitted parent text before completion), case 5 **8/8**. Case 9 i91 emitted progress and repeated the `updated` verb in its footer. In i90 and i92 case 9, the query worker finished but the runner timed out waiting for surplus background timers. These trials predate the explicit prohibition on background wait timers.

Full mode follow-up i95 scored **59/78**: cases 1–9 were 6/8, 7/8, 6/8, 0/12 (timeout), 8/8, 5/6, 11/11, 7/8 and 9/9. Cases 1–6 loaded the preceding wait instructions; cases 7–9 loaded the final text. Rows that passed i114 and failed i95 were 1.1 and 1.5 (worker attribution and key order), 3.1 (worker attribution), and 4.7–4.8 and 4.10–4.12 (ingest did not complete within 230 seconds).

With the final wait revision, i96 cases 2, 5 and 6 scored **7/8**, **8/8** and **6/6**. All three approved query workers in i96–98 wrote the Query note, index and log, and each produced a valid final footer, but every parent emitted a progress message before completion. The i95 approved query was silent; silence is not reliable yet.

### R3 history (earlier rubric)

| Skill | Iteration | `with_skill` | 0.28.1 `old_skill` |
| --- | --- | --- | --- |
| term | 14 | 26/27 | 12/27 |
| concept | 15 | 19/19 | 10/19 |
| entity | 15 | 21/21 | 6/21 |
| secondbrain-mode | 15 | 53/60 | 35/60 |

These historical totals pool graded rows across cases under the earlier rubric. The baseline uses 0.28.1 `principle-knowledge-notes` for term, concept and entity and the whole 0.28.1 skill tree for mode. Each recorded iteration has a skill-creator `benchmark.json` and a static `review.html` in its workspace under `evals/results/`.

Targeted mode regrades, not new runs: iteration 17 copied to 137 (query 5/7 and verify 3/6: both lack successful structured reads; verify also reports a contradictory role); iteration 121 copied to 138 (Logseq 6/7: skipped work in the footer; ingest 6/9: verbatim Raw passes, but lint, narration and footer fail).

Second-review grade-only comparison, using copies of the retained `with_skill` traces. These are rubric changes, not fresh runs or baseline scores. Entity adds the no-records row; ingest adds three impressions-migration rows.

| Original → copy | Entity: old → revised | Ingest: old → revised |
| --- | --- | --- |
| 30 → 230 | 7/7 → 8/8 | 8/9 → 8/12 |
| 31 → 231 | 7/7 → 7/8 | 7/9 → 7/12 |
| 32 → 232 | — | 9/9 → 12/12 |
| 33 → 233 | — | 9/9 → 12/12 |
| 34 → 234 | — | 7/9 → 10/12 |
| 35 → 235 | — | 8/9 → 11/12 |
| 36 → 236 | — | 9/9 → 12/12 |

The revised rows detect unauthorized index/log creation in 231 Entity and missing impressions migration in 230–231 Ingest. Ingest 231 also has an unlinked entity; 234 has a non-verbatim Raw. Ingest 230, 231, 234 and 235 still narrate wiki work in the user-facing answer.

Final whole-plugin trigger run (`trigger_run.py`, default Claude config with `CLAUDE_CONFIG_DIR` unset, 3 runs per query): term 20/20, concept 20/20, entity 20/20, and secondbrain-mode 13/13 for non-auto-invocation, not activation or lifecycle. No runs failed and no `principle-*` or `secondbrain-mode` Skill-tool invocations were observed.
