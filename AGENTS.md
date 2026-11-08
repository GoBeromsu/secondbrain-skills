# Repository contract

This repository owns twenty-four independent Agent Skills, the `secondbrain-skills` collection: seven native Obsidian skills and seventeen knowledge skills, including four independently usable archival principles, `principle-skill-creating`, and the optional `secondbrain-mode` stance.

- Native: Markdown, Bases, visualization (JSON Canvas files, Excalidraw drawings and Pele diagrams), official CLI operations, Web Clipper, plugin/Templater diagnosis, and Headless Sync. Each `skills/obsidian-*/SKILL.md` owns exactly its named feature.
- Knowledge: `capture`, `inbox`, `ingest`, `query`, `verify`, `audit`, `lint`, `status`, `reindex`, `refresh-context`, and `onboard`. Each `skills/<name>/SKILL.md` owns exactly its named task and carries no `obsidian-` prefix.
- Principles: `principle-respect-des-fonds`, `principle-original-order`, `principle-hierarchical-management`, and `principle-collective-description` belong to the knowledge group. They provide contextual guidance and grant no write authorization.
- Authoring: `principle-skill-creating` decides what a package keeps in Markdown and what it hands to templates, thin scripts and agents; read it before changing a package. `secondbrain-mode` is an optional stance for multi-package work; it dispatches nothing and every package still runs directly.

There is no callable root skill, mandatory shared runtime, compatibility alias, or hidden dispatcher. A package name is one lowercase hyphenated segment naming a task (`ingest`) or a format (`obsidian-bases`), never a role or version; native packages keep the `obsidian-` prefix, knowledge packages never use it. Files inside a package are named for their subject without repeating the package or resource kind (`ingest/references/papers.md`), lowercase and hyphenated, with no dates or version suffixes. Each capability has exactly one owning package; checks stay at package format (`claude plugin validate . --strict`). Verify behavior by actually running it; the repository keeps no tests.

## Authoring

- Keep required references, assets, and scripts inside the owning package. Compose neighboring packages by explicit identity only when the task needs them. Define each rule once at its owner and name or invoke that skill instead of copying its procedure.
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
