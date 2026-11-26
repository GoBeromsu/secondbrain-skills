# Bases Operations Reference

Error reporting, empty-result triage and verification for a `.base` that already exists. The schema lives in [../SKILL.md](../SKILL.md).

## Writing

- Write through the vault surface the user selected (for example `obsidian-cli`) when there is one; none is required.
- Never assemble `.base` content with shell redirection or stream editors: they mangle the nested quoting in filters and formulas.
- Validate the in-memory document before writing. A document that fails validation is not written, so the previous file stays intact.
- Adding a view: append it unless a position was requested, give it a unique name, and say so when it lands first (that changes what plain embeds render).
- Changing filters: state which rows the change should add or remove. Narrowing hides rows; widening can pull in the whole vault.
- Editing a `base` block inside a note is a note edit: keep the rest of the note exactly.

## Error Conditions

Report these with the exact key path, all in one pass. Do not hide them by deleting the offending construct.

| Condition | Report |
|-----------|--------|
| YAML does not parse | parser line and column; file left unchanged |
| Filter object with zero or several of `and`/`or`/`not` | location and keys found |
| Filter list entry that is neither a string nor a filter object | path and type |
| `formula.X` referenced but not defined | every referencing site |
| Circular formulas | the cycle |
| View without `type` or `name`, or duplicate view names | view indices |
| `groupBy`/`sort` property that no candidate note has | property and where referenced |
| Unknown summary name | property and name |
| Duration used as a number, or unguarded optional property | formula name and expression |
| Unknown view `type` | the type, as a runtime capability question |

A formula referencing a property no note defines is valid; it yields empty values (a data question).

## Empty or Unexpected Results

Investigate; never loosen the schema until something appears. Stop at the first branch that explains it:

1. **Wrong file**: the base open in the app is not the one you edited.
2. **Filters exclude everything**: global and view filters combine with `AND`.
3. **Property mismatch**: spelling or case (`status` vs `Status`), a file property shadowing a note property, string `"2"` vs number `2`, tag with and without `#`.
4. **Scope mismatch**: the folder filter names a path the notes are not in, or the expected rows are non-Markdown files.
5. **Index or refresh**: stale rather than missing rows; reopen the base or the app.
6. **Capability**: the layout needs a newer app or a disabled plugin, or Bases is off in Settings → Core plugins.

Describe the outcome in rows: expected count, observed count, and which rows differ.

## Three Separate Claims

1. **Static validation**: the document is well formed. Says nothing about the vault.
2. **Readback**: re-read the file from the intended path and compare view names in order, the changed keys, and everything that should be unchanged. A successful write call is not readback.
3. **Rendered**: in Obsidian, check the view name, the toolbar result count, group headers, row order against `sort`, columns against `order`, and summaries. Record the app version. When no app is available, report this leg as unverified; never infer it from valid YAML.

An embed is its own rendered claim: inside it `this` is the embedding note, so check the embed itself.

## Report

Name the path written, the effect at the level of views, filters or formulas, the readback result, the rendered observation with app version (or why it is unverified), and anything found but not changed with its key path.
