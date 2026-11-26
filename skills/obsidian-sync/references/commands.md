# `ob` behavior that `--help` does not show

Notes for `obsidian-headless` **0.0.14**. [`../SKILL.md`](../SKILL.md) owns the workflow and the authorization boundary.

**Flags and synopses come from the CLI, not from here.** `ob --help` lists the commands; `ob <command> --help` lists each one's options and accepted values (`sync-config --help` prints the valid `--mode`, `--conflict-strategy`, `--file-types`, and `--configs` values). Run them; they are local, need no account, and outrank this file. What follows is only what help omits: hidden side effects, matching rules, failure strings, and exit codes, checked against the 0.0.14 package.

## Version check

Before the first command that changes anything, read `node --version` (v22 or later), `ob --version`, and `ob <command> --help` for each subcommand this task will run. Check only that the build still offers a supported way to get each intended effect and its safety. A supported form that differs from this file is fine; record which one you used.

Stop and report version skew only when the build offers no supported way to get an intended effect or its safety: for example no way to set `pull-only` before the first sync, or no way to pair without putting the passphrase on the command line. Never emulate a missing capability by hand-editing `config.json` or by installing a different version mid-task.

Record `ob --version`, `node --version`, and the subcommands checked in the task evidence.

## Reach: which commands leave the machine

Authorize by class, not by command name.

| Local only - no token, no network | Account and network |
|---|---|
| `sync-list-local`, `sync-status`, `sync-config`, `sync-unlink` | `login`, `logout`, `sync-list-remote`, `sync-create-remote`, `sync-setup`, `sync`, `publish-*` |

`sync-status` reads the token only to decide whether to print `Not logged in.`; it never validates it. `sync-unlink` is local but destructive. Commands that need a token and find none stop with `No account logged in. Run "ob login" first.` (exit 2) before any network call. The `publish-*` family shares the binary and login but targets Obsidian Publish; never run one for a sync request.

## Global behavior

**`--path` matching is lexical.** The value (default: the current directory) goes through `path.resolve`, every stored `config.json` is re-resolved the same way, and they are compared as strings.

- `.`, `..`, and trailing slashes normalize away.
- Letter case does not. On a case-insensitive filesystem `/srv/Vaults/example` and `/srv/vaults/example` are one directory and two vaults to `ob`.
- Symlinks do not resolve: a symlinked parent, or `/tmp/x` where the config stored `/private/tmp/x`, is a different vault.
- The failure is `No sync configuration found for <resolved-path>` (exit 3), never a near-match fallback.

Resolve the root once per host with `pwd -P` and reuse the variable. Never copy an absolute path between machines.

**`--json`** suppresses progress, sends errors to stderr, and **disables every interactive prompt** - so never use it for `sync-setup` on an end-to-end encrypted vault. Its configuration payload is redacted by construction (no host, key, salt, or token), which makes `ob sync-status --path "$ROOT" --json` the way to capture a configuration for evidence.

**Token resolution** checks `OBSIDIAN_AUTH_TOKEN` first, then the token file. That variable is the mechanism for unattended runs; the E2E passphrase has no equivalent and is never supplied non-interactively.

**Credentials never go on a command line.** `login --password`, `sync-setup --password`, and `sync-create-remote --password` exist, and each one puts a secret in the process table and shell history. Let the command prompt in a real terminal.

## Per-command notes

**`login`.** With a valid stored token and no credential flags it only prints `Logged in as <name> (<email>)`. Passing `--email` or `--password` discards the stored token first. A wrong MFA code is not re-prompted. Failure: `Login failed:` (exit 2).

**`sync-list-remote` / `sync-list-local`.** Own and shared vaults are listed separately but selected by the same `--vault` value; record the **ID**, since a name is a mutable, duplicable label. `sync-list-local` is a pure filesystem read and the safe first command of any diagnosis: it enumerates every pairing on this host, which is how a second pairing against a differently spelled path is found.

**`sync-create-remote`.** A remote account mutation, never the answer to `Vault "<name>" not found.` - that error means the identity was wrong, and a replacement vault hides the mistake. Without `--encryption standard` it prompts for an E2E passphrase and treats an empty answer as standard.

**`sync-setup`.**

- Selection: exact **ID** across own and shared vaults first, then exact **name**. Several matches: `Multiple vaults named "<name>". Use the vault ID instead:` (exit 1). None: `Vault "<name>" not found.` (exit 3).
- The passphrase prompt needs a real TTY. Piping, `< /dev/null`, `--json`, and a non-interactive `ssh host 'ob sync-setup ...'` all end in `Password not provided.` (exit 2). A wrong passphrase: `Failed to validate password.` (exit 2).
- A non-empty root gets a warning, not a prompt: `notes in your local vault will be merged ... the most recent version of the note will be preserved.` That is why first contact is staged in `pull-only` - see [Conflict mechanics](#conflict-mechanics). A missing root is created.
- **Setup writes a fresh policy.** It writes `conflictStrategy: "merge"` and no `syncMode`, file types, configs, or excluded folders, so every earlier `sync-config` choice is gone and the pairing is bidirectional again. Re-apply the intended policy before any `ob sync`.
- Re-running setup for an already configured ID overwrites `config.json` but keeps `state.db`. `sync-unlink` then `sync-setup` drops the state database too, so the next run is an initial sync.

**`sync-config`.** With no options it only prints the current configuration. Invalid values are rejected before the write (exit 1). Two effects are invisible in help:

- `--mode bidirectional` **removes** the stored mode rather than storing a word. A config with no `syncMode` key is an armed uploader, not an unconfigured one.
- Changing `--excluded-folders`, `--file-types`, or `--configs` **queues every file that newly enters scope** for download on the next run. Widening scope is a scheduled transfer.

`--config-dir` changes only which in-vault folder the client treats as app configuration; it moves nothing.

**`sync-status`.** Reports **stored configuration only** - no service contact, queue depth, last-success time, or drift. A healthy block is not evidence that the last run worked. `Location:` must match the resolved root character for character, and `Vault:` must carry the intended ID. A leading `Not logged in.` is a credential gap, not a broken pairing.

**`sync-unlink`.** Deletes the whole per-vault directory - `config.json`, `state.db`, **and `sync.log`** - and leaves notes untouched. Copy `sync.log` out first; unlinking mid-incident destroys the only run record. Unlink only the verified-wrong pairing found with `sync-list-local`, never as a remedy for a transport or login error.

**`sync`.**

- Preconditions, in order: a config for the resolved path (exit 3), a token (exit 2), a usable encryption key (`Encryption key not found. Run setup again.`, exit 2), the vault lock.
- It first prints `Starting sync:` and the configuration block. Read it: it is the last chance to catch a wrong mode.
- **Lock**: a directory at `<vault-root>/<config-dir>/.sync.lock`, refreshed every second, stale after 5 seconds and then reclaimed automatically. A second `ob sync` on the same root exits 1 with `Another sync instance is already running for this vault.` Never delete the lock by hand - a fresh lock means a live writer you have not found. It arbitrates only between `ob sync` processes, not the desktop app, a file-sync tool, or a backup job.
- **Termination**: a one-shot run stops at `Fully synced`. It does **not** stop because the network is down - it loops on `Waiting to connect to server` (about every 30 s) in one-shot mode too. Bound one-shot runs with an external timeout. `SIGINT`/`SIGTERM` print `Received signal to shut down...` and release the lock.
- **Reconnect**: exponential backoff from 5 s, 50% jitter, capped at 5 min, reset on success. `Disconnected from server` followed later by `Fully synced` is normal.
- Two errors stop instead of retrying, both as `Sync failed:` (exit 1): `The connected remote vault no longer exists.` and `Your subscription to Obsidian Sync has expired`. Retrying only replays them.

## Mode semantics

| Mode | Remote change | Remote deletion | Local-only file | Locally modified file | Uploads |
|---|---|---|---|---|---|
| `bidirectional` | downloaded | applied locally | kept and uploaded | merged or conflict-copied | yes |
| `pull-only` | downloaded | **applied locally** | kept, never uploaded | overwritten by remote | no |
| `mirror-remote` | downloaded | **applied locally** | **deleted** | **reverted to remote** | no |

Neither download-only mode is read-only. `pull-only` is the staging mode because it keeps local-only files and uploads nothing, not because it cannot delete. `mirror-remote` discards this machine's work; it needs its own approval and a tested restore point, and is never a conflict-resolution shortcut.

## Conflict mechanics

Only a **Markdown** file that exists on both sides with different content, in a mode that uploads, reaches the merge path. Canvas, Bases, and attachments never produce conflicted copies.

| `conflictStrategy` | What happens | Log lines |
|---|---|---|
| `merge` (default) | Three-way merge against the last synced version, in place. With no common base the remote wins if the local file is under 3 minutes old, otherwise only if its mtime is newer. | `Merging conflicted file`, then `Merge successful`, `Merge failed. <error>`, or `Downloading <path>` |
| `conflict` | The **local** version is written as `<name> (Conflicted copy <device-name> <YYYYMMDDHHMM>).<ext>` (local wall-clock time); the **remote** version takes the original path. | `Merging conflicted file`, then `Conflicted copy stored` |

- **The initial reconciliation ignores `conflictStrategy`.** A remote file with a newer mtime simply overwrites the local one. `--conflict-strategy conflict` protects later runs, not first contact; only a restore point does.
- Config JSON is merged key by key; on `Merge failed.` the remote file is downloaded whole.
- Anything else that cannot be reconciled is skipped with `Rejected server change`.

`(Conflicted copy ...)` files are ordinary notes that sync and may be the only surviving copy of one side. Report them with paths and leave them in place.

## Sync scope

- `.md`, `.canvas`, and `.base` are **always** synced; `--file-types` governs attachments only. `unsupported` means every extension not in the other categories.
- Any path segment starting with `.` is excluded outside the config directory, so a `.git` inside the vault is never synced.
- Inside the config directory, `node_modules`, dot-entries, `workspace.json`, and `workspace-mobile.json` are never synced; everything else must map to an enabled `--configs` category.
- `--excluded-folders` entries match a folder exactly or as a path prefix.

## Exit codes

| Code | Class | Examples |
|---|---|---|
| 0 | Success, including "nothing configured" | `No vaults configured.` |
| 1 | Generic failure, invalid value, ambiguous name, lock held, usage error | `Sync failed:`, `Multiple vaults named`, `Another sync instance is already running`, `error: unknown option` |
| 2 | Credentials and encryption | `No account logged in.`, `Login failed:`, `Password not provided.`, `Failed to validate password.`, `Encryption key not found.` |
| 3 | Identity | `No sync configuration found for <path>`, `Vault "<name>" not found.` |

Exit 2 and 3 are terminal for an unattended run; restarting on them is a retry loop that cannot succeed.

## Error strings

| String | Correct response |
|---|---|
| `No sync configuration found for <path>` | Compare with `sync-list-local` and fix the spelling. Do not pair again. |
| `Vault "<name>" not found.` | Re-read `sync-list-remote`. No similar name, no replacement vault. |
| `Password not provided.` | Re-run in a real terminal. Never add `--password`. |
| `Failed to validate password.` | Confirm with the account owner; repeating does not help. |
| `Encryption key not found.` / `End-to-end encryption key missing.` / `Encryption version not supported` | Configuration damage. Go to [recovery.md](recovery.md) before re-pairing - re-pairing resets policy. Never edit the value by hand. |
| `Another sync instance is already running for this vault.` | Find the other writer. Do not delete `.sync.lock`. |
| `The connected remote vault no longer exists.` | Stop; verify against `sync-list-remote` and preserve local state. Identity incident. |
| `Your subscription to Obsidian Sync has expired` | Report it; no client-side fix. |
| `Sync error: <error>` | Per-attempt error; a later `Fully synced` means it recovered. |

## Run-output lines worth reading

Each line is `<Message> <vault-relative-path>` on stdout, mirrored into `sync.log`.

| Line | Meaning |
|---|---|
| `Deleting <path>` | **A remote deletion applied locally** - in every mode, `pull-only` included. Explain each one from the remote side before accepting the run. |
| `Deleting remote file` / `Deleting remote folder` | **A local deletion applied to the remote** (`bidirectional`) |
| `Removing local-only file` / `Reverting <path>` / `Restoring <path>` | `mirror-remote` discarding or restoring local state |
| `Renaming conflicted file` | A local file sat where the remote has a folder; renamed to `<name> (Conflicted copy).<ext>` regardless of strategy |
| `Conflicted copy stored`, `Merging conflicted file`, `Merge failed.` | See [Conflict mechanics](#conflict-mechanics) |
| `Rejected server change` | A change was skipped and stays skipped |
| `Ignoring remote file name with illegal characters` | Remote path unrepresentable locally |
| `Waiting to connect to server` | In the reconnect backoff window |
| `Fully synced` | Converged; a one-shot run stops here |
| `Warning: btime native module failed to load.` | macOS/Windows; creation times not preserved |

## On-disk layout

```
~/.obsidian-headless/                              # macOS, Windows (0700)
${XDG_CONFIG_HOME:-~/.config}/obsidian-headless/   # Linux
  auth_token                   # 0600
  sync/<vault-id>/config.json  # 0600 - holds encryptionKey and encryptionSalt in cleartext
  sync/<vault-id>/state.db
  sync/<vault-id>/sync.log     # append-only run log
<vault-root>/<config-dir>/.sync.lock   # lock directory, never synced
```

Never copy, print, or commit `config.json`; record configuration with `sync-status --json`. `sync-setup` writes the identity and key fields plus `conflictStrategy`, `deviceName`, `configDir`; only `sync-config` writes `syncMode` (absent means bidirectional), `ignoreFolders`, `allowTypes`, `allowSpecialFiles`. That asymmetry is why [recovery.md](recovery.md) captures the effective configuration before any re-pair.

## Boundary

This file documents behavior and grants nothing. Network access, pairing, configuration changes, sync runs, unlinking, and daemon lifecycle are separate authorizations; an unauthorized one is reported as not performed. See [daemon.md](daemon.md) for continuous operation and [recovery.md](recovery.md) for incidents.
