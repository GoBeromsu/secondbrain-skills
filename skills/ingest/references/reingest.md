# Source update and reprocessing

Two different cases. Decide which one applies before writing anything, and say which in the report.

- **Source update:** the original itself changed — a new edition, a revised page, a newer repository commit. Proof is a comparison of newly obtained content against the existing Raw's `## Original Content`, not a date or a title.
- **Reprocessing:** the original is unchanged, but its existing Raw or the Wiki pages compiled from it need another pass — a better extraction of the same version, a missed concept, a Step 6 rule applied afresh.

## Identity

- Find the existing Raw by `source` first, then by any other source address or locator that note already records (an earlier URL, a DOI, a file or page locator). A title never proves sameness.
- Read the identity values as they are. Do not add, rename or migrate identity keys; migration runs only under the explicit authorization in [frontmatter](frontmatter.md).
- When two Raws match, or the match rests only on a weak locator, stop that item and report the candidates.

## Source update

1. Obtain the new version through the per-material reference and compare it with the existing Raw's `## Original Content`.
2. Ask the owner before writing: minor or major change. Without an answer, write nothing for this item.
3. Minor: keep the existing Raw byte-for-byte. Record the difference in the report; update Wiki pages only through Step 6.
4. Major: save a new Raw `{Title}-v2.md` (next free suffix) through Step 5 with the new verbatim content and `supersedes: "[[earlier raw]]"`. In the earlier Raw change only `superseded-by: "[[new raw]]"` and `date_modified`; its body, human notes and every other key stay. Both Raws stay.
5. Compile through Steps 6–8. Pages keep the earlier Raw in `source` and add the new one. A claim the new version changes follows Step 6: keep both, attributed, with `> [!warning] Contradiction` unless the correction is verified; a claim the new version drops is not thereby disproved.

## Reprocessing

1. Never rewrite an existing Raw body or its human notes. A better extraction of the same version becomes a new Raw through Step 5 whose `referenced` points at the earlier Raw, with the reason in `## Ingest Notes`; the earlier Raw stays.
2. Wiki updates use the existing Raw (or the new extraction) as the source and follow Step 6's update process for the selected template, preserving valid content and source history.
3. Changing only metadata of existing notes is not reprocessing; it needs explicit migration authorization.

## Batches

The owner names the batch: which items, in what scope. Each item is one run of the steps above. Run one representative item first and report it; the pilot does not authorize the rest of the batch.

A web-book item needs an owner-selected multi-page source with at least five chapters and two directly fetched chapter URLs; a commercial or offline book follows the file and page locator adaptation in [books](books.md).

## Record

- Every written item updates the wiki index and appends to the wiki log per Step 9, with `reingest` as the operation: `## [YYYY-MM-DD] reingest | {source title}`, naming update or reprocessing, the Raws written and the pages touched. Paths are in [records](records.md).
- The wiki log and the Raws' `supersedes` / `superseded-by` / `referenced` links are the record of what was reprocessed. A commit message or trailer is not evidence that an item was reprocessed; a normal ingest commit is not a reprocessing record.
- An interrupted batch is resumed from the wiki log and readback of the touched notes: finish or report each unfinished item. Never reset, check out or delete to clean up.
- No commit or push. A commit only when the owner separately asks, per [git provenance](git-provenance.md).
