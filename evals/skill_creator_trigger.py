#!/usr/bin/env python3
"""Run skill-creator's run_eval.py or run_loop.py with one project dir per query.

run_eval.py writes each query's temporary command into one shared `.claude/commands/`, so with
`--num-workers` above 1 every parallel `claude -p` sees several copies of the same description and
often picks another worker's copy, which counts as "not triggered". This wrapper gives each query
its own temp project dir and otherwise runs skill-creator's own code unchanged. `claude` should be
a shim that adds `--setting-sources project,local --strict-mcp-config`, so installed user plugins
(including a released secondbrain-skills) do not compete.

  SKILL_CREATOR=<skill-creator dir> PATH=<shim>:$PATH \
    python3 evals/skill_creator_trigger.py run_loop --eval-set ... --skill-path ... --model opus
"""
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.environ["SKILL_CREATOR"])

from scripts import run_eval  # noqa: E402

_original = run_eval.run_single_query


def isolated_query(query, skill_name, skill_description, timeout, project_root, model=None):
    tmp = tempfile.mkdtemp(prefix="sb-trigger-")
    os.makedirs(os.path.join(tmp, ".claude", "commands"))
    try:
        return _original(query, skill_name, skill_description, timeout, tmp, model)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


run_eval.run_single_query = isolated_query

if __name__ == "__main__":
    tool = sys.argv.pop(1)
    if tool == "run_eval":
        run_eval.main()
    elif tool == "run_loop":
        from scripts import run_loop
        run_loop.main()
    else:
        sys.exit("usage: skill_creator_trigger.py run_eval|run_loop <args>")
