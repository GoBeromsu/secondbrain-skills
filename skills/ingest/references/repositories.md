# Repositories

A repository is a Product. What the owner keeps is why they need the tool and what it does for their work; a copy of its README answers neither, and the README stays available at its URL. So a repository ingest saves no Raw. It creates or updates the repository's Product Entity with the [product](../../entity/assets/product.md) template and the rules in [`entity`](../../entity/SKILL.md).

How the Steps change:

- **Step 1** matters most here. The collection purpose is the reason the page exists and becomes the centre of its TL;DR and Personal Insights. A star, a fork or a feed event is not a purpose; without one from the owner or the task, ask.
- **Step 2** widens to every owner record that mentions the tool, as `entity`'s Step 3 describes.
- **Step 5** is skipped: no Raw, no `## Original Content`, no Raw pre-flight. An Inbox file that only holds the repository's README or link is the candidate, not evidence to preserve; Inbox cleanup follows its usual authorization.
- **Step 6** writes the Product page. Other Terms, Concepts and Guides are compiled only when the owner's purpose calls for them, each citing the repository link and commit instead of a Raw.
- **Step 9** records the Product page where a Raw link would go.

Reading the repository:

- Read files at one commit through `raw.githubusercontent.com/{owner}/{repo}/{sha}/…`, not a rendered-page scrape, and cite each file by that pinned URL as a `[label](URL)` in References and footnotes. The URL carries the commit; the page's prose and footnotes do not repeat the sha, the branch or a list of files read. A branch name without a read sha is not a pinned source; a file inventory is not the content of its files.
- Beyond the README, read what the owner's purpose depends on: the documentation of that feature, the license file, release notes for the version in use.
- Report not found (deleted, renamed, wrong path), inaccessible (private, rate limit, network) and partial (files or range not read) to the owner. On the page, only a fact the reader needs survives, such as that the repository is gone.
- Do not execute repository scripts, install dependencies or fetch unrelated branches. Quote only what a claim needs, with attribution; do not copy implementation into another product without verified rights.

Naming and identity:

- Title the page with the product's name in the spelling its maker uses. When a different referent already holds that name, use `{name} ({owner}).md`.
- `aliases` holds `owner/repo`; `url` holds the project homepage as a plain URL, or the canonical repository URL when it has none; `source` holds only vault notes (owner records, Raws) as quoted wikilinks.
- Maintainers become `"[[Name]]"` person links only when the repository states them.

A repository Raw the vault already holds stays as it is and may be cited as a source; it is not deleted, moved or rewritten by this recipe.
