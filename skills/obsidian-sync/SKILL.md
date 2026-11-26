---
name: "obsidian-sync"
description: "Operates the headless `ob` client (npm `obsidian-headless`) for Obsidian Sync on a server, VPS or replica with no desktop app: pairs a vault path to a remote vault, sets the sync mode, and runs one-shot or `--continuous` sync. Use for headless sync setup, inspection or repair; notes that disappeared or reverted after a sync; `ob` errors; `(Conflicted copy ...)` files; or a sync daemon to start, stop or restart. Not for GUI Sync settings, Publish or the `obsidian` desktop CLI."
license: MIT
---

# Obsidian Headless Sync

Drive `ob` so that every sync run has a named local root, a named remote vault, a known direction and a way back. Exit code 0 is not success; success is that the observed file changes match the direction the user authorized.

Two properties of this client shape everything below:

- **Download modes delete.** `pull-only` and `mirror-remote` both apply remote deletions to the local vault. Neither is read-only.
- **Pairing resets policy.** `ob sync-setup` writes a fresh config: mode `bidirectional`, conflict strategy `merge`. Pairing arms uploads and discards an earlier `pull-only` or `conflict` choice.

## The client

`ob` comes from the npm package `obsidian-headless` and needs Node.js 22 or later. It talks to the Sync service directly and never uses a running desktop app. It is not the `obsidian` desktop CLI.

```bash
node --version && ob --version
ob <command> --help      # the authority for this build
```

This manual was written against 0.0.14. Read a subcommand's `--help` before a command that changes something, and use only a form the build documents; never guess a flag or hand-edit the client's config files. If `ob` is missing, say so and offer `npm install -g obsidian-headless`; do not install it as a side effect of a diagnosis.

`ob login` prompts for email, password and a 2FA code, so the user runs it in their own terminal. One login reaches every vault the account can see: separate pairings are not separate credentials.

## Name both ends

- **Local root.** Always pass `--path`; without it `ob` targets the current directory. The path is compared as a string, so a different letter case or a symlinked parent is a different vault, and the symptom is `No sync configuration found for <path>` (exit 3). Resolve it on the acting host and reuse it:

  ```bash
  OBSIDIAN_VAULT_PATH=$(cd /srv/vaults/example-vault && pwd -P)
  ```

- **Remote vault.** `--vault` takes an ID or a name. Prefer the ID from `ob sync-list-remote`; a name can be changed or duplicated.

## One writer

Use one sync writer per vault folder. The desktop app's Sync and `ob sync` on the same folder produce conflicts and unexplained deletions. `ob sync` locks only against another `ob sync` (`Another sync instance is already running for this vault.`); it does not see the desktop app, a file-sync tool or a backup job. Never delete `.sync.lock` by hand: a live lock is a live writer.

## Ask before each effect

Approval for one class never covers another.

| Effect | Commands |
|---|---|
| Local read, safe to run first | `ob --version`, `ob sync-list-local`, `ob sync-status` |
| Network read | `ob sync-list-remote`, `ob login` with no arguments |
| Credentials | `ob login`, `ob logout` (clears the token for every vault on the host) |
| Remote create | `ob sync-create-remote` |
| Pairing | `ob sync-setup` (overwrites the config for that vault ID) |
| Config | `ob sync-config` |
| Vault mutation | `ob sync`, `ob sync --continuous`: the commands that can delete notes |
| Unlink | `ob sync-unlink` (removes stored config, sync state and `sync.log`, no undo) |
| Daemon | supervisor start, stop, restart, delete |

## Workflow

A step you cannot complete is a stop to report, not a risk to absorb.

### 0. Baseline, local only

```bash
ob sync-list-local
ob sync-status --path "$OBSIDIAN_VAULT_PATH"
find "$OBSIDIAN_VAULT_PATH" -name '*.md' -not -path '*/.git/*' | wc -l
```

Create a restore point that holds the root's current content: a Git commit or tag, or a tested file-level backup. Record what it covers. A tag over a dirty tree does not capture uncommitted work, and that work is the user's; do not commit or clean it to tidy the snapshot.

### 1. Pair, then set pull-only before any run

```bash
ob sync-list-remote
ob sync-setup --vault "<remote-vault-id>" --path "$OBSIDIAN_VAULT_PATH" --device-name "example-replica-01"
ob sync-config --path "$OBSIDIAN_VAULT_PATH" --mode pull-only
ob sync-status --path "$OBSIDIAN_VAULT_PATH"
```

If the expected vault is absent, stop; do not pair a similar name or create a replacement. An end-to-end encrypted vault prompts for its password, which needs a real terminal: piping, `--json` or non-interactive `ssh` fails with `Password not provided.` or `Failed to validate password.` (exit 2). Never pass the password with `--password` or store it in a script, environment file or supervisor definition.

Setting `pull-only` is mandatory: a fresh pairing is `bidirectional`, and an `ob sync` before this step uploads local state. Confirm that `sync-status` shows the intended vault, the exact root and `pull-only`.

### 2. One bounded run

```bash
set -o pipefail
ob sync --path "$OBSIDIAN_VAULT_PATH" 2>&1 | tee "${TMPDIR:-/tmp}/ob-first-run.log"
```

No `--continuous` here. The run ends after `Fully synced`. `pull-only` keeps local-only files but still applies remote deletions.

### 3. Compare with the baseline

Accept the run only when all hold:

- The log ends with `Fully synced`, with no repeated transport or authentication errors.
- Every `Deleting` or `Reverting` line is one you can explain from the remote side.
- The file-count change and the diff against the restore point match the authorized direction.
- No `Renaming conflicted file`, `Merge failed.` or `Rejected server change` line is unexplained.
- A representative changed file opens and holds the expected content.

Anything unexplained ends the workflow: go to [recovery](references/recovery.md). Do not re-pair, switch modes or run again to see whether it clears; each destroys the evidence.

### 4. Promote only on request

```bash
ob sync-config --path "$OBSIDIAN_VAULT_PATH" --mode bidirectional
ob sync --path "$OBSIDIAN_VAULT_PATH"
```

Uploading is its own approval. Repeat step 3, and consider `--continuous` only after a second clean one-shot run; see [daemon](references/daemon.md). A pull-only run proves nothing about uploads: report that direction as unverified unless a round-trip was authorized and read back.

`mirror-remote` deletes local-only files and reverts local edits. It is a deliberate "discard this machine's work" operation with its own approval and restore point, never a repair step.

## Conflicts

`merge` (default) rewrites a Markdown file in place. `conflict` keeps both sides: the remote version at the original path and the local one as `<name> (Conflicted copy <device-name> <YYYYMMDDHHMM>).<ext>`.

- Set `--conflict-strategy conflict` before the run that could conflict, and again after any re-pairing.
- The strategy does not apply to the first run of a new pairing: the newer file wins outright. Only the restore point protects that run.
- Never delete or move `(Conflicted copy ...)` files. Each is the only surviving copy of one side; report the paths and let the user decide.
- `Merge failed.` is an incident, not a log line to skip.

## Network failure

Continuous mode reconnects on its own; `Disconnected from server` followed by a later `Fully synced` is normal, so do not restart it. If a one-shot run died midway, re-run the same command in the same mode and compare as in step 3. `The connected remote vault no longer exists.`, an expired subscription and password or token errors are not transport problems: retrying replays them, so go to [recovery](references/recovery.md). Never treat a connectivity symptom by unlinking, re-pairing or switching modes.

## Secrets

- Unattended runs take the account token from `OBSIDIAN_AUTH_TOKEN`. Never inline it in a command, a committed file or a supervisor definition kept in a repository.
- The encryption password is only ever typed at the interactive prompt.
- Never copy, print or commit the client's token file, `config.json` (it holds the derived encryption key and salt) or `state.db`. Record a configuration with `ob sync-status --json` instead.
- `sync.log` records the vault name, vault ID, absolute root and device name. Redact them before sharing, and never write a token, password, key or salt into a report, issue or commit.

## References

- [commands](references/commands.md): what `--help` omits - hidden side effects, `--path` matching, mode semantics, conflict mechanics, exit codes, error strings, run-output vocabulary, on-disk layout.
- [daemon](references/daemon.md): continuous sync under a supervisor: preconditions, start, stop, restart, log growth, health, crash loops.
- [recovery](references/recovery.md): contain, preserve evidence, classify, restore, re-admit sync.

Sync is transport authority, not content authority: it grants no permission to edit a note. Obsidian Publish, GUI Sync settings and version history are outside this skill.
