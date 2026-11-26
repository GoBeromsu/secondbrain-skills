# Secondbrain-mode trigger summary — 2026-11-26

| Run | Passed / queries | Trials per query | Evidence in `evals/results/` |
| --- | ---: | ---: | --- |
| Whole plugin (non-auto-invocation) | 13/13 | 3 | `trigger-plugin.json` |
| Whole plugin (non-auto-invocation, full trace) | 13/13 | 1 | `trigger-plugin-full.json` |
| Historical isolated description | 14/14 | 3 | `secondbrain-mode-workspace/run_eval-final.json`, `secondbrain-mode-workspace/run_eval.json` |

Commands: `python3 evals/trigger_run.py` (full trace: add `--full --runs 1`); historical isolated harness: `python3 evals/skill_creator_trigger.py run_eval --eval-set evals/results/secondbrain-mode-workspace/trigger-evals.json --skill-path skills/secondbrain-mode --model opus` (see [eval setup](../README.md) for the wrapper environment).

The whole-plugin runner skips the explicit `/secondbrain-mode` command and requires zero automatic invocations regardless of historical labels. Both runs recorded zero errors and zero disabled-skill invocations across all 73 queries. This is not an activation, lifecycle, or background-routing score. The isolated harness exposed a temporary command using the description and graded old labels, including expected invocations, so its 14/14 does not measure `disable-model-invocation` and is not a score for the revised all-negative set. No description-loop result was recorded for this disabled skill.

## R4 final (2026-11-26)

Whole-plugin non-auto-invocation: **13/13 (100%)**, all negative queries, 3 runs per query. The default run observed 0 `principle-*` and 0 `secondbrain-mode` Skill-tool invocations and no run errors across 219 trials. This does not measure activation or lifecycle.

Command: `python3 evals/trigger_run.py` (current output: `evals/results/trigger-plugin.json`).
