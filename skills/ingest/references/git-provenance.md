# Git provenance

Ingest never commits or pushes. The wiki index and the append-only wiki log in [records](records.md) record every ingest; Git history does not replace them.

When the owner separately asks for a commit of an ingest:

- stage exactly the paths that ingest touched (Raw, Wiki pages, Maps, hub and atoms, the resolved wiki index, the resolved wiki log, any retained attachment), by exact path, never a glob;
- use the subject `ingest: {source title}`;
- check the Git index first: entries already staged before the ingest belong to someone else, so stop and report;
- leave unrelated dirty files unstaged and byte-unchanged.

Never hard reset, check out to settle content, amend an earlier commit, or force push. Push only on a separate owner request; when the remote has moved on, stop and report instead of rewriting history. A vault that is not a Git repository has nothing to commit; say so.
