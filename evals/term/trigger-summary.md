# Term trigger summary — 2026-11-26

| Run | Passed / queries | Trials per query | Evidence in `evals/results/` |
| --- | ---: | ---: | --- |
| Whole plugin | 20/20 | 3 | `trigger-plugin.json` |
| Whole plugin (full trace) | 20/20 | 1 | `trigger-plugin-full.json` |
| Isolated description | 20/20 | 3 | `term-workspace/run_eval-final.json` |

Commands: `python3 evals/trigger_run.py` (full trace: add `--full --runs 1`); `python3 evals/skill_creator_trigger.py run_eval --eval-set evals/results/term-workspace/trigger-evals.json --skill-path skills/term --model opus` (see [eval setup](../README.md) for the wrapper environment). The whole-plugin runs recorded zero errors and zero disabled-skill invocations across all 73 queries.

Description optimization: `python3 evals/skill_creator_trigger.py run_loop --eval-set evals/results/term-workspace/trigger-evals.json --skill-path skills/term --model opus --max-iterations 5 --timeout 90 --report none`. The R3 run report records that the original description scored best on holdout and was kept. The loop's numeric scores and split counts were not retained in the workspace; 20/20 above is the separate isolated evaluation, not a holdout score.

## R4 final (2026-11-26)

Whole-plugin routing: **20/20 (100%)**, 10 positive and 10 negative queries, 3 runs per query. The default run observed 0 `principle-*` and 0 `secondbrain-mode` Skill-tool invocations and no run errors across 219 trials.

Command: `python3 evals/trigger_run.py` (current output: `evals/results/trigger-plugin.json`).
