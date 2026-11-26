<p align="center">
  <img src="assets/brand/splash.jpg" alt="A Blender render: from a candlelit desk on a moonlit stone terrace, open books fly out under the Milky Way, linked to one another by fine lines of light that run on into a constellation" width="100%">
</p>

<p align="center">
  <a href="https://github.com/GoBeromsu/secondbrain-skills/actions/workflows/validate.yml"><img alt="validate" src="https://github.com/GoBeromsu/secondbrain-skills/actions/workflows/validate.yml/badge.svg"></a>
  <a href="https://github.com/GoBeromsu/secondbrain-skills/releases"><img alt="release" src="https://img.shields.io/github/v/release/GoBeromsu/secondbrain-skills?include_prereleases&amp;label=release&amp;color=7c3aed"></a>
  <a href="LICENSE"><img alt="MIT license" src="https://img.shields.io/badge/license-MIT-f0b85a"></a>
  <a href="https://agentskills.io"><img alt="Agent Skills" src="https://img.shields.io/badge/format-Agent%20Skills-1d1936"></a>
  <a href="CODE_OF_CONDUCT.md"><img alt="Contributor Covenant 2.1" src="https://img.shields.io/badge/Contributor%20Covenant-2.1-4f8f7a"></a>
</p>

<p align="center">
  <b>English</b> · <a href="README.ko.md">한국어</a>
  <br>
  <a href="#quick-start">Quick start</a> · <a href="#how-it-works">How it works</a> · <a href="#packages">Packages</a> · <a href="#install">Install</a> · <a href="CONTRIBUTING.md">Contributing</a> · <a href="ACKNOWLEDGEMENTS.md">Acknowledgements</a>
</p>

**secondbrain-skills** lets an agent run an Obsidian vault the way a librarian runs a library, and then connects it. Sources come in through the book drop and the original goes into the archive untouched. Every page compiled from it is linked to the pages, people and works it touches, until scattered notes read as one constellation. Questions are answered by following those links, with citations back to the shelf.

A second brain is not a pile of notes; it is the connections between them. That is what these skills build and keep.

Each package is one `SKILL.md` that owns one job. There is no root skill and no shared runtime: your agent loads the package the task needs and nothing else. The one dispatcher, `secondbrain-mode`, runs only when you turn it on.

## Quick start

```sh
claude plugin marketplace add GoBeromsu/secondbrain-skills
claude plugin install secondbrain-skills@secondbrain-skills
```

> [!TIP]
> Then ask in plain language: *"Capture these tabs."* · *"Ingest this article."* · *"What does my vault say about spaced repetition?"* · *"Lint the AI folder."*

Other runtimes are under [Install](#install).

## How it works

<p align="center">
  <img src="assets/demo/workflow.svg" alt="Four stations: Book drop (capture, inbox), Archive (ingest keeps the Raw source verbatim), Constellation (wiki pages, Entities and Maps linked into one network) and Reading room (query answers by following the links, with citations), with a Shelf care loop of lint, audit, verify, status and reindex" width="100%">
</p>

| Principle | What it means in practice |
| --- | --- |
| **The skill carries the judgment.** | What to select, how to classify and when to stop are written in Markdown. Scripts answer a single question and never gate a run. |
| **The original survives.** | A source you hand over to ingest or save is preserved verbatim as a Raw note before anything is written about it; a web page read while researching stays a link. |
| **Knowing a format is not permission.** | A package writes only to an exact destination the task authorized, then reads the result back. |
| **Missing evidence is never success.** | A parse is not a render, and an exit code is not a write. Each package says which level it reached. |

## Packages

Forty-one independent packages. Every row links to the `SKILL.md` that defines it; its `description` is what an agent matches on. A `principle-*` leaf is never picked on its own; it is read when a package step or `secondbrain-mode` names it.

| Shelf | Package | Job |
| --- | --- | --- |
| **Collect** | [`capture`](skills/capture/SKILL.md) | Save tabs, URLs, files, conversations or agent sessions as Inbox candidates. |
| | [`inbox`](skills/inbox/SKILL.md) | Review the Inbox and route a selected scope through `ingest`. |
| **Compile** | [`ingest`](skills/ingest/SKILL.md) | Turn one source into a preserved Raw note plus Wiki pages, Entities and Maps. |
| | [`onboard`](skills/onboard/SKILL.md) | Set up a fresh vault through an owner interview, or diagnose an existing one. |
| | [`refresh-context`](skills/refresh-context/SKILL.md) | Refresh the Core Context snapshot the agent keeps about the owner. |
| | [`reindex`](skills/reindex/SKILL.md) | Refresh the qmd search index after notes change. |
| | [`term`](skills/term/SKILL.md) | Research a field term and write or update its Term page. |
| | [`concept`](skills/concept/SKILL.md) | Research an idea or method and write or update its Concept page. |
| | [`entity`](skills/entity/SKILL.md) | Research a named thing and write or update its Entity page from its type template. |
| **Ask** | [`query`](skills/query/SKILL.md) | Answer from the Wiki with citations, and feed gaps back into it. |
| **Mode** | [`secondbrain-mode`](skills/secondbrain-mode/SKILL.md) | While on, route new words, methods and named things to wiki workers. One runs in the foreground; two or more run in the background. The parent waits silently and reports writes in one line. |
| **Shelf care** | [`lint`](skills/lint/SKILL.md) | Mechanical health: links, placement, frontmatter, index and log sync. |
| | [`audit`](skills/audit/SKILL.md) | Sample Wiki pages per Map cluster and score their quality, read-only. |
| | [`verify`](skills/verify/SKILL.md) | Check one page's claims against its cited evidence. |
| | [`status`](skills/status/SKILL.md) | A read-only snapshot of counts, backlog and coverage. |
| **Principles** | [`principle-vault-roles`](skills/principle-vault-roles/SKILL.md) | Which writes each vault area allows: wiki, source and work. |
| | [`principle-resolve-target`](skills/principle-resolve-target/SKILL.md) | State the vault, note, effect and authority before any write. |
| | [`principle-preserve-unrequested`](skills/principle-preserve-unrequested/SKILL.md) | Change only what was asked; keep the rest byte-identical. |
| | [`principle-read-back`](skills/principle-read-back/SKILL.md) | Re-read and resolve every write before calling it done. |
| | [`principle-provenance`](skills/principle-provenance/SKILL.md) | Find and keep the true creator of a record. |
| | [`principle-original-order`](skills/principle-original-order/SKILL.md) | Keep a source's own order and wording. |
| | [`principle-hierarchy`](skills/principle-hierarchy/SKILL.md) | Place an item under the whole it belongs to. |
| | [`principle-collective-description`](skills/principle-collective-description/SKILL.md) | Describe a collection's scope, coverage and gaps at its hub. |
| | [`principle-note-kinds`](skills/principle-note-kinds/SKILL.md) | Decide whether knowledge is a Term, Concept, Guide or Entity. |
| | [`principle-entity-types`](skills/principle-entity-types/SKILL.md) | Pick an Entity's type, template and folder. |
| | [`principle-revise-and-consolidate`](skills/principle-revise-and-consolidate/SKILL.md) | Update an existing page without losing anything valid on it. |
| | [`principle-not-a-research-log`](skills/principle-not-a-research-log/SKILL.md) | Keep the research process off the page. |
| | [`principle-plain-tldr`](skills/principle-plain-tldr/SKILL.md) | Write the TL;DR as plain sentences. |
| | [`principle-draw-structure`](skills/principle-draw-structure/SKILL.md) | Draw a diagram where prose makes the reader rebuild a structure. |
| | [`principle-standalone-note`](skills/principle-standalone-note/SKILL.md) | Write for a reader who never saw the conversation. |
| | [`principle-quotation-attribution`](skills/principle-quotation-attribution/SKILL.md) | Keep quotation, translation, interpretation and own words apart. |
| | [`principle-preserve-voice`](skills/principle-preserve-voice/SKILL.md) | Keep the author's sentences when revising around them. |
| | [`principle-note-shape`](skills/principle-note-shape/SKILL.md) | Headings, lists, tables, bold and one term per concept. |
| | [`principle-frontmatter`](skills/principle-frontmatter/SKILL.md) | Key order, URL keys, links and status in frontmatter. |
| | [`principle-link-form`](skills/principle-link-form/SKILL.md) | Wikilinks, external links, first-mention links and embeds. |
| | [`principle-markdown-blocks`](skills/principle-markdown-blocks/SKILL.md) | Nested lists, code fences, emphasis, callouts and other blocks. |
| **Obsidian** | [`bases`](skills/bases/SKILL.md) | Obsidian Bases: `.base` files and embedded base blocks. |
| | [`obsidian-cli`](skills/obsidian-cli/SKILL.md) | Drive the running desktop app through the official `obsidian` CLI. |
| | [`obsidian-clipper`](skills/obsidian-clipper/SKILL.md) | Author and repair Web Clipper template JSON. |
| | [`obsidian-sync`](skills/obsidian-sync/SKILL.md) | Headless Obsidian Sync with the `ob` client. |
| | [`obsidian-visualize`](skills/obsidian-visualize/SKILL.md) | JSON Canvas, Excalidraw and Pele mermaid visuals. |

## Install

Install through each runtime's own plugin or skill registry, and update the same way. This repository ships no installer script, and a directory copy next to a plugin install shadows the plugin.

<details open>
<summary><b>Claude Code</b></summary>

```sh
claude plugin marketplace add GoBeromsu/secondbrain-skills
claude plugin install secondbrain-skills@secondbrain-skills
# update
claude plugin marketplace update secondbrain-skills
claude plugin update secondbrain-skills@secondbrain-skills
```
</details>

<details>
<summary><b>Codex</b></summary>

```sh
codex plugin marketplace add GoBeromsu/secondbrain-skills
codex plugin add secondbrain-skills@secondbrain-skills
# update
codex plugin marketplace upgrade secondbrain-skills
codex plugin add secondbrain-skills@secondbrain-skills
```
</details>

<details>
<summary><b>GJC</b></summary>

```sh
gjc plugin marketplace add GoBeromsu/secondbrain-skills
gjc plugin install secondbrain-skills@secondbrain-skills
# update
gjc plugin marketplace update secondbrain-skills
gjc plugin upgrade secondbrain-skills@secondbrain-skills
```
</details>

<details>
<summary><b>Grok Build</b></summary>

```sh
grok plugin marketplace add GoBeromsu/secondbrain-skills
```

Then install and update from the Marketplace tab.
</details>

<details>
<summary><b>Hermes</b></summary>

```sh
hermes plugins install GoBeromsu/secondbrain-skills --enable
```

A portable plugin; skills resolve as `<namespace>:<name>` and update automatically with `plugins.auto_apply: true`. Do not install the `v0.1.0` tag on Hermes.
</details>

<details>
<summary><b>Other runtimes</b> (Cursor, generic Agent Skills, Aside)</summary>

Runtimes without a plugin registry read `skills/<name>/` folders from their skill directory; use their own documented import. Aside reads `<account root>/skills/user/<name>/SKILL.md`.
</details>

## What is verified

Every push and pull request runs [`validate`](.github/workflows/validate.yml) in CI:

| Check | Tool |
| --- | --- |
| Plugin format | `claude plugin validate . --strict` |
| Manifests parse, share one name and one version | [`scripts/validate.py`](scripts/validate.py) |
| Each `skills/<name>/SKILL.md` has frontmatter whose `name` is its folder and a description within 1,024 characters | `scripts/validate.py` |
| Every package is listed in both READMEs, and every relative link resolves | `scripts/validate.py` |
| Every image is recorded in the [asset ledger](assets/asset-ledger.json); SVGs carry no scripts or external references; the icon is a square PNG | `scripts/validate.py` |
| Bundled scripts compile; optionally, `link-lint.py` reproduces its [eval](evals/README.md) | `scripts/validate.py` |

Run the same checks locally with `python3 scripts/validate.py`.

Fixtures live outside the repository in `<dir>/fixture-vault/` and `<dir>/lint-links/`. To opt in to the lint regression, run `SB_EVAL_FIXTURES="<dir>" python3 scripts/validate.py`. The [fixture-based eval runners](evals/README.md) also accept `--fixtures <dir>`, which overrides the environment variable.

> [!NOTE]
> These are static checks: they claim no runtime load. What a change was run against is named in that change's commit message.

Releases: `scripts/release.sh <version>` on `main` sets the version in every manifest (skills carry none), runs the validator, tags, pushes and publishes the prerelease.

## Contributing and credits

Issues and pull requests are welcome: start with [CONTRIBUTING.md](CONTRIBUTING.md), and report security problems privately as described in [SECURITY.md](SECURITY.md). Everyone taking part follows the [Code of Conduct](CODE_OF_CONDUCT.md).

This library stands on other people's shelves: kepano's obsidian-skills, Yohan Koo's cmds-llm-wiki, Andrej Karpathy's LLM Wiki pattern and more. Who contributed what, under which licence, is in [ACKNOWLEDGEMENTS.md](ACKNOWLEDGEMENTS.md); upstream notices are in [NOTICE](NOTICE).

## License

[MIT](LICENSE). Upstream grants are reproduced in [NOTICE](NOTICE). All art in `assets/` is original work recorded in the [asset ledger](assets/asset-ledger.json). The banner is rendered in Blender Cycles from [`scripts/art/showcase.py`](scripts/art/showcase.py), a procedural scene with no external assets; none of the art is a screenshot.
