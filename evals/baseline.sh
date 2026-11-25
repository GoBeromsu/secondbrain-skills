#!/bin/sh
# Materialize a skill as it shipped in a past release, as skill-creator's old_skill baseline.
# Usage: evals/baseline.sh <skill> [commit]   (default commit: 1c73d0b, release 0.28.1)
# Extracts the whole skills/ tree of that commit, so links to sibling skills (../ingest/...) still
# resolve, into evals/results/<skill>-workspace/old-skills/ (gitignored) and prints the path of
# the skill inside it: evals/results/<skill>-workspace/old-skills/<skill>.
set -eu
skill=${1:?usage: evals/baseline.sh <skill> [commit]}
ref=${2:-1c73d0b}
root=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)
git -C "$root" cat-file -e "$ref:skills/$skill/SKILL.md" 2>/dev/null || {
	echo "skills/$skill does not exist at $ref" >&2
	exit 1
}
dest="$root/evals/results/$skill-workspace/old-skills"
rm -rf "$dest"
mkdir -p "$dest"
git -C "$root" archive "$ref" skills | tar -x -C "$dest" --strip-components=1
printf '%s\n' "$dest/$skill"
