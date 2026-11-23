# Contributing to secondbrain-skills

Thanks for helping keep the library. This page covers how a change gets onto the shelf. Everyone taking part follows the [Code of Conduct](CODE_OF_CONDUCT.md).

## Ground rules

- **One job per package.** A package is one `skills/<name>/SKILL.md`. If a change makes a package do a second job, it belongs in another package.
- **Judgment lives in Markdown.** Selection, classification and stopping rules are written in `SKILL.md`. A script answers one question and never gates a run.
- **No shared runtime.** No package may require a sibling package, a router or a root skill.
- **Evidence over claims.** Say which level a change reached (parsed, validated, rendered, run) and what it was run against. A passing check is not a runtime load.
- **Original or recorded.** Every image is listed in [`assets/asset-ledger.json`](assets/asset-ledger.json). Upstream text or code needs a licence that permits it and an entry in [`NOTICE`](NOTICE) and [`ACKNOWLEDGEMENTS.md`](ACKNOWLEDGEMENTS.md).

## Making a change

1. Fork, then branch from `main`.
2. Edit the package. Keep `name` equal to its folder and the `description` within 1,024 characters; the description is what an agent matches on.
3. Adding or renaming a package? Add a row to the package table in both `README.md` and `README.ko.md`.
4. Run the checks:

   ```sh
   python3 scripts/validate.py
   claude plugin validate . --strict   # optional locally; CI runs it
   ```

5. Open a pull request. The template asks what you changed, why, and what you ran it against. CI runs the same checks on every pull request.

## Commit messages

Use [Conventional Commits](https://www.conventionalcommits.org/): `feat(ingest): …`, `fix(lint): …`, `docs: …`. Mark breaking changes with `!`. Release notes are grouped from pull request labels (see [`.github/release.yml`](.github/release.yml)).

## Art

Renders in `assets/` come from [`scripts/art/library.py`](scripts/art/library.py), a procedural Blender scene with no external assets:

```sh
blender -b -P scripts/art/library.py -- nightsky out.png 128
```

Record any new or changed image in the asset ledger with how it was made.

## Releases

Maintainers release from `main` with `scripts/release.sh <version>`, which sets every manifest version, runs the validator, tags and publishes a prerelease.

## Reporting

- Bugs and package ideas: [open an issue](https://github.com/GoBeromsu/secondbrain-skills/issues/new/choose).
- Security problems: see [SECURITY.md](SECURITY.md); please do not file them publicly.
