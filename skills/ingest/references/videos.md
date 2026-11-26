# Videos

For YouTube, `defuddle parse "$URL" --md -f` returns the whole timestamped transcript under `## Transcript`, with chapter headings, plus `title`, `author` (the channel) and `published` hints in one call. Copy that transcript verbatim, timestamps and chapter headings included, into `## Original Content`. Fall back to `yt-dlp` (options from its current help, spoken-language captions) only when defuddle returns no transcript; keep no caption file in the vault. Other video hosts: `yt-dlp`. A local audio or video file: a transcription tool, leaving the media in place and recording its location, duration and tool in `## Ingest Notes`. A supplied transcript is ingested directly.

- `source` is the canonical video URL; the channel or speaker goes in `author` as `"[[Name]]"`, the upload date in `date_published` when stated.
- Record the tool, the caption track (manual or auto-generated) and its language in `## Ingest Notes`; a translation is a separate, labelled step.
- A description, metadata or summary is not a transcript; never reconstruct words from one. No transcript means no Raw claiming one. Name the outcome: not found, inaccessible, or partial (with the missing timestamps).
- A highlight reel or another programme's trailer is noted, not counted as separate evidence. Live policy decides whether the destination is a video or YouTube leaf.
