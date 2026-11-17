# Wiki records

The wiki index and the wiki log live at the paths below, relative to the vault root. `skills/ingest/scripts/records.py` reads these lines. A `wiki-index` or `wiki-log` line in the vault `AGENTS.md` replaces the matching line. A `--index` or `--log` argument replaces that one path for this run. Write a path into the vault `AGENTS.md` when it should persist.

```
wiki-index: 60. AI/index.md
wiki-log: 60. AI/log.md
```

Find the vault root by the nearest ancestor that contains `.obsidian`. If none does, use the nearest ancestor that contains `AGENTS.md`. Do not use `index.md` to find the vault.

Create a missing index or log only at the resolved path. Never create `index.md` or `log.md` at the vault root. A resolved path that is the vault root stops the run. Report the path and write nothing there. A root `index.md` left from an older layout is not the wiki index.
