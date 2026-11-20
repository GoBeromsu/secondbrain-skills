# Conformance

Every Wiki page, of any kind, is written to these rules. After writing, check each item against the page and record it as present or absent with the offending line; a page passes only when every item is absent. A check that was not run is reported as not run, never as absent.

| # | Anti-pattern | How to find it | Instead |
| --- | --- | --- | --- |
| 1 | An `obsidian://` link, or a Markdown link or path to a note in this vault | `obsidian://` anywhere; `](` followed by a note path or `.md` | `[[Note Name]]`, with a folder path only when the basename collides |
| 2 | A bare, angle-bracket or empty-label external URL | `https://` not inside `[label](URL)` | `[label](URL)` with a non-empty label |
| 3 | A redundant web link beside an inline Raw citation | a web URL beside its Raw, except DOI and original access links in a Term source entry | cite the Raw with a locator; a Term's source entry also gives its DOI and direct original access link |
| 4 | "According to X" before a citation that already names X | `according to`, `X writes that …` with X cited on the same line | the fact with its citation; attribute in prose only when sources disagree |
| 5 | Acquisition or process notes | acquisition logs or boilerplate in the page; exclude evidence access scope in Term source entries | keep operational details in the run report; retain the inspected scope and material access limitation in each Term source entry |
| 6 | A claim the run did not check written as fact | a factual assertion without supporting content in a cited Raw, or an owner observation presented as research | cite the evidence for the assertion; attribute personal context to its linked note |
| 7 | Field jargon translated | a translated term where the field uses the original (`Schwungklimmzug` for kipping pull-up, `Transformator` for the transformer model, both on a German page) | the original-language name inside sentences in the page's language; quotations stay verbatim |
| 8 | A Term missing a documented sense | compare the definition and uses with relevant field and vault evidence | check senses against the [Term template](../templates/term.md) |
| 9 | Related links without a reason | a related link with no discernible relationship | explain the relationship once where the link is used |
| 10 | Source replay | Details that walk the source in its order, one bullet per passage, or that mostly quote or paraphrase it | explain the idea in the page's own words: what it is, how it works, why it holds, where it applies and where it stops; quote at most a line that carries the idea |

Link a note in this vault as `[[Note Name]]` and a web page as `[title](https://...)`; `lint`'s `scripts/link-lint.py` checks both.
