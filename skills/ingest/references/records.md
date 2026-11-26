# Wiki records

Use the index and log paths named for the live vault, relative to its root. Read `wiki-index` and `wiki-log` from the vault-root `AGENTS.md`. Pass `--index` or `--log` only for a path the live policy explicitly supplies for this run; it takes precedence over the corresponding `AGENTS.md` line. Persist an owner-approved path in the vault `AGENTS.md` only when authorized to change configuration.

These entries illustrate the configuration syntax only. The resolver never reads them or uses them as fallback paths.

```
wiki-index: 60. AI/index.md
wiki-log: 60. AI/log.md
```

Find the vault root by the nearest ancestor that contains `.obsidian`. If none does, use the nearest ancestor that contains `AGENTS.md`. Do not use `index.md` to find the vault.

Before reading or writing either record, resolve the wiki role from the vault guideline, then check that the record's resolved path is beneath that role. If the wiki role or record path is not configured, or the path resolves outside the wiki role, report that record as unavailable and skip it. Do not guess a replacement.

With a known wiki role, run `python3 "<ingest-scripts>/records.py" --vault "<vault>" --wiki "<wiki-folder>"`. The wiki folder must be vault-relative. The resolver prints one tab-separated row per record: `index|log<TAB>path<TAB><resolved location>` or `index|log<TAB>unavailable<TAB><reason>` (`not configured` for an absent mapping). An invalid vault or wiki folder blocks resolution of both records (exit 2). A `path` row may name a missing file; check existence separately when reading.

Create a missing index or log only at the configured path beneath the wiki role and only when the route authorizes the write. Never create `index.md` or `log.md` at the vault root. A root `index.md` left from an older layout is not the wiki index.
