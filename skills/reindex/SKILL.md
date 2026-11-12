---
name: "reindex"
description: "Refreshes the qmd search index (BM25 and embeddings) after notes change. Use for a search-index refresh, at the end of an ingest, or after bulk edits made outside the agent. Not for creating collections, changing qmd configuration or searching notes."
license: MIT
---

# Reindex

Refresh the configured qmd index so new and changed notes are searchable. The
index and its collections are whatever qmd is already configured with; this
skill does not create, rename, or edit them.

Done means:

- the changed notes are in the index and a search finds them;
- no embedding the index needs is left pending, or the pending count is
  reported as unfinished;
- the report names the collections refreshed, the document and vector counts
  from qmd's own status, and anything qmd reported as failed.

Run `qmd update`, `qmd embed`, `qmd status` over the registered collections,
usually `wiki`, `raw_sources` and `queries` (Inbox excluded until ingest).
Refresh only the collections the live qmd configuration already registers; confirm
command names with `qmd --help` on this host. Do not change qmd models, the
embedding model or its environment variable, network access, or the collections
config without the owner's approval; live policy wins and anything unknown is
reported as unknown. Force a full re-embed (`qmd embed -f`) only after an
approved embedding-model change. A non-zero exit or a status you cannot read is
unfinished, never zero pending. When `qmd` is not installed, report that and stop.

This procedure is the qmd CLI itself: run `qmd update`, then `qmd embed`, then
`qmd status`, and read the counts and any `Pending: N need embedding` line from
that status (qmd 2.8.3 prints the line only when N is above 0; vectors count
embedded chunks, not files). A failed command or an empty or unrecognized status
is unfinished.

There is no edit hook or background reindex: qmd has no file watcher, and this
package does not wrap qmd to add one. Run the three commands above at the end of
the workflow that changed notes, or when the owner asks.
