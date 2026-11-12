---
name: "secondbrain-mode"
description: "Sets the working stance for a vault task spanning several packages: delegates independent units to subagents, owns their work and ends with an independent review. Use for secondbrain-mode, 세컨드브레인 모드, or a multi-step task such as capture, then ingest, then query. A single task runs directly without it."
license: MIT
---

# Secondbrain mode

A stance, not a dispatcher: every package runs directly from its own description. Load this when a task spans several of them.

## Stance

- Read the destination vault's live policy before any write. A package never grants write permission by itself.
- One request runs to the end. Ask once, up front, for what only the owner can answer; do not stop for a second approval between steps the request already covers.
- Read a `principle-*` package in full before applying it.
- Report what was written, what was skipped and what stayed unknown. Missing evidence is never success.

## Subagents

Delegate reading, per-source work or edits to background subagents only when they split into independent units worth running in parallel, or would fill the main thread with material it does not need to keep; otherwise do them in the main thread, which always keeps the request, the decisions and the summary.

- Brief each one like a peer: the goal, what is already ruled out, file pointers instead of pasted content, and the package and principle it must read in full first.
- One subagent per independent unit: one source, one topic bundle, one package.
- A fix round goes to a fresh subagent with the original brief and the prior report.
- You own its work. Read the diff or the written notes yourself and write your own summary.

## Review

A task that wrote to the vault or changed a skill ends with one independent review subagent over the whole change. When the runtime has no subagents, read every write back yourself and report that the review was not independent.

- Give the reviewer the artifact and the governing package or principle, not your conclusion.
- Ask for findings with path and line, ordered by severity, and what it could not check.
- Fix each finding or dismiss it with a concrete reason, and report which was which.

## Changing a skill

1. Read `principle-skill-creating` in full.
2. Make the edit, or delegate it to a subagent briefed with that principle and the package path when it runs in parallel with other independent edits.
3. Run the repository's format checks; here, `claude plugin validate . --strict`.
4. Send the diff to a separate review subagent, asking where the change breaks the principle and where it duplicates or contradicts a sibling package.
