# Conformance

Every Wiki page, of any kind, is written to these rules. After writing, check each item against the page and record it as present or absent with the offending line; a page passes only when every item is absent. A check that was not run is reported as not run, never as absent.

| # | Anti-pattern | How to find it | Instead |
| --- | --- | --- | --- |
| 1 | A note in another vault linked as `[[path]]` | a `[[` whose target is not a file in this vault but exists in the mothership | `[title](obsidian://open?vault=<vault>&file=<path>)`, both components URL-encoded |
| 2 | A bare `obsidian://` URL in the body or a property (`moc`, `mainVaultRelated`, any other) | `obsidian://` not preceded by `](` | the same `[title](obsidian://...)` form |
| 3 | A web URL beside a source that has a Raw | `https://` on a line that also links that source's Raw | the Raw link only; the URL lives in the Raw |
| 4 | "According to X" before a citation that already names X | `according to`, `X writes that …` with X cited on the same line | the fact with its citation; attribute in prose only when sources disagree |
| 5 | Acquisition or process notes | could not read or obtain, blocked, bot check, second-hand check, not verified, this run, provided sources | move to the run report; write an unknown fact once as unknown |
| 6 | A claim the run did not check written as fact | a statement whose citation is not a Raw in `source` or the owner's own quoted note | cite a Raw that states it, or leave it out |
| 7 | Field jargon translated | a translated term where the field uses the original (`Schwungklimmzug` for kipping pull-up, `Transformator` for the transformer model, both on a German page) | the original-language name inside sentences in the page's language; quotations stay verbatim |
| 8 | A Term written from one field only | `domain` or Senses missing a sense that dictionaries, vault links or the owner's notes use | collect every sense first, as [terms](terms.md) says |
| 9 | Related links without a reason | a `[[link]]` in Related Terms with no line saying why | group label plus one line per link |
| 10 | Source replay | Details that walk the source in its order, one bullet per passage, or that mostly quote or paraphrase it | explain the idea in the page's own words: what it is, how it works, why it holds, where it applies and where it stops; quote at most a line that carries the idea |

Link a note in this vault as `[[Note Name]]` and a web page as `[title](https://...)`.
