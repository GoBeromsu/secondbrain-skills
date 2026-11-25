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

`Guideline.md` gives each role a folder name different from the owner's vault, so a skill that hardcodes a path fails: wiki is `Knowledge/`, source (Raw) is `Sources/`, work is `Projects/`. It also names the lifecycle types (`project`, `task`) and marks Entities with `layer: entities`.

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

Each case names the paths it applies to. A case passes on a path when every expected finding is reported and none of its clean files has a finding; a final row per path fails on any finding no case expects. A script that crashes, prints a malformed line, or whose `# violations` total disagrees with its lines counts as not run, and every row of that path fails. The runner also stops if `evals.json` names a fixture file that does not exist, or if its `policy` differs from the wiki folder and lifecycle types `Guideline.md` declares. Without `--cli`, or when Obsidian does not have the fixture open, the CLI path does not run; `obsidian-lint.py` never opens or switches a vault itself. Only open the fixture in Obsidian when no other session depends on which vault is focused.

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

The `claude` shim for skill-creator's scripts adds `--setting-sources project,local --strict-mcp-config`. The baseline for `term`, `concept` and `entity` is 0.28.1's `principle-knowledge-notes`, which held their templates; `secondbrain-mode` has no 0.28.1 counterpart, so its baseline gets the whole 0.28.1 skills tree. Checks that read a page reuse `skills/lint/scripts/link-lint.py --checks all`; its `BROKEN` rule is ignored there because the term template asks for one link to a term that has no page yet. The narration check looks for reports of wiki work in the answer body (a page written, saved, filed, or a subagent); citing a vault page in a `query` or `verify` answer is the answer, not narration.

### Recorded knowledge-skill runs (2026-11-26)

| Skill | Final iteration | `with_skill` | 0.28.1 `old_skill` |
| --- | --- | --- | --- |
| term | 14 | 26/27 | 12/27 |
| concept | 13 | 19/19 | 10/19 |
| entity | 14 | 21/21 | 6/21 |
| secondbrain-mode | 14 | 58/60 | 38/60 |

Totals pool graded rows across cases. The baseline uses 0.28.1 `principle-knowledge-notes` for term, concept and entity and the whole 0.28.1 skill tree for mode. Each final iteration has a skill-creator `benchmark.json` and a static `review.html` in its workspace under `evals/results/`.

Final whole-plugin trigger run (`trigger_run.py`, default Claude config with `CLAUDE_CONFIG_DIR` unset, 3 runs per query): term 20/20, concept 20/20, entity 20/20, and secondbrain-mode 13/13 for non-auto-invocation, not activation or lifecycle. No runs failed and no `principle-*` or `secondbrain-mode` Skill-tool invocations were observed.

