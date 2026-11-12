# Repository contract

This repository owns the `secondbrain-skills` collection of independent Agent Skills: native Obsidian skills and knowledge skills, the latter including independently usable principles.

- Native: Markdown, Bases, visualization (JSON Canvas files, Excalidraw drawings and Pele diagrams), official CLI operations, Web Clipper, and Headless Sync. Each of `markdown`, `bases`, `obsidian-visualize`, `obsidian-cli`, `obsidian-clipper` and `obsidian-sync` owns exactly its named feature in `skills/<name>/SKILL.md`.
- Knowledge: `capture`, `inbox`, `ingest`, `query`, `verify`, `audit`, `lint`, `status`, `reindex`, `refresh-context`, and `onboard`. Each `skills/<name>/SKILL.md` owns exactly its named task and carries no `obsidian-` prefix.
- Principles: `principle-respect-des-fonds`, `principle-original-order`, `principle-hierarchical-management`, `principle-collective-description` and `principle-wiki-types` belong to the knowledge group. They provide contextual guidance and grant no write authorization.

There is no callable root skill, mandatory shared runtime, compatibility alias, or hidden dispatcher. A package name is one lowercase hyphenated segment naming a task (`ingest`) or a format (`bases`), never a role or version; only `obsidian-visualize`, `obsidian-cli`, `obsidian-clipper` and `obsidian-sync` carry the `obsidian-` prefix. Files inside a package are named for their subject without repeating the package or resource kind (`ingest/references/papers.md`), lowercase and hyphenated, with no dates or version suffixes. Each capability has exactly one owning package; checks stay at package format (`claude plugin validate . --strict`). Verify behavior by actually running it; the repository keeps no tests.

## Authoring

- Before any work, fetch `origin` and fast-forward the checkout to the latest `main`; never start on a stale base.
- Author and change a package only with the vendor's own skill-creator for the model that will run it (`anthropic-skills:skill-creator` for Claude, OpenAI's for Codex), following that vendor's current prompting guide; then run `claude plugin validate . --strict` and have an independent reviewer read the diff against this file and sibling packages.
- Keep in SKILL.md only what needs judgment: when to apply, trade-offs, what the result must contain, where the task ends. Hand the rest to the part that does it best: a template for exact structure, a thin script for counting, matching or parsing, an agent for a bounded delegated read, and a reference for lookup detail that is not needed on every run. The direction is always Markdown calling code: judgment stays in Markdown, and counting, matching, lookup, identity and hashing, and external actions through their own tool move to code; a script that gates the decision is deleted.
- State the outcome a step must produce, not the command. Keep a prohibition only when breaking it loses something that cannot be restored. Delete before adding. Call a packaged CLI directly rather than through a wrapper script. Packages keep no CHANGELOG or version; checks enforce format only.
- Write each rule as one imperative line naming the tool or the action; the incident, its reasons, and flag-level detail belong in the commit message.
- Two descriptions must not claim the same request; when neighbours are close, say what the neighbour owns in the description's last sentence.
- Keep required references, assets, and scripts inside the owning package. `SKILL.md` is the only file at the package root; everything else lives in a subfolder. `agents/` holds briefs for independent workers that do similar but different work in parallel. Compose neighboring packages by explicit identity only when the task needs them. Define each rule once at its owner and name or invoke that skill instead of copying its procedure.
- `assets/` holds only what a step consumes.
- A script answers one question or performs one action; it never orchestrates steps, carries judgment as flags, or blocks the run, and an existing tool beats a new script.
- When two packages say different things about the same case, decide which one owns it and delete the other statement in the same change.
- Before writing, search the sibling packages for the same trigger, step or rule.
- One request runs to the end; a step that must happen is stated as mandatory and checked in a closing review step, not by a gate.
- The release bumps only the plugin manifest version.
- Never write comments.
- Make the smallest behavioral diff the task needs. Before editing and before submitting, keep a file change only if leaving it unchanged would break the requested behavior; never change a file just for wording consistency. Add no speculative abstraction, unused eval or scaffolding, or example, commentary or report decoration that only repeats a rule.
- Preserve MIT notices for upstream-derived files in `NOTICE`. This repository is its own canonical source: packages state their rules directly, with no upstream comparison or lineage record; history is the Git log.
- Credit every person or project a package draws on, copied or only consulted, in the README Acknowledgements section (both languages) in the same change. Do not add a per-package `LICENSE`.
- Use only synthetic public examples. Never include credentials, private account identifiers, workstation paths, personal notes, internal plans, or raw private logs.
- Respect the destination vault's live policy and exact task authorization. A format skill never grants write permission. Optional policy tools are unused unless explicitly selected; their absence is normal. Vault-specific placement stays in that vault's policy, never in a package.
- Never turn missing app/plugin/network evidence into success. Separate static validation, runtime discovery, materialized readback, and rendered verification.
- For native packages, ground mutable app, CLI, plugin API, and sync facts in official documentation first, then check them against evidence from the installed version. Disclose any conflict and what it affects. A fact that neither settles stays unknown; don't infer compatibility.
- For native package changes, name the official sources and safely observed versions a change relied on in that change's commit message. When a source or version moves, re-check the affected claims and run them again before a package repeats them.
- When evidence shows a native runtime form changed, work in this order: re-check the documentation, run the changed form, update the recipe. The rule is prospective.
- Before shortening a native description, compare it with the routing cases that depend on it and keep every trigger they rely on, non-English phrasing included. Removing a relied-on trigger is a breaking change, never a cosmetic edit.
- Every native operation follows seven steps, stated in the owning package's own procedure: resolve the exact artifact and intended effect, read its current bytes, preserve unrelated content, use the least destructive supported surface the task selected, read back the exact result, report the evidence and any unmet prerequisite, and keep unresolved runtime facts unknown. These steps add no shared runtime, dependency, or permission.

## Effect boundaries

Local candidate tests do not authorize remote publication, deployed installation, consumer changes, or retirement of another source owner. Keep the existing owner intact until an explicitly approved canary and fresh-load verification succeed. Recovery restores exact approved source/configuration versions, never resets, mirrors, deletes, or overwrites user notes or metadata.

Do not modify other worktrees or installed caches. No commit, push, remote creation, host installation, or protected policy change without separate concrete-effect authorization. Unresolved lifecycle decisions remain unresolved.
