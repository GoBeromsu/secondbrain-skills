# Web Clipper Workflows

How to get from a request to a template that survives a real page, what the error conditions are, and which claims stay separate (the evidence ladder in [../SKILL.md](../SKILL.md#evidence-ladder)). The JSON contract is in [../SKILL.md](../SKILL.md); the language is in [template-language.md](template-language.md).

## Order of work

Follow the workflow in [../SKILL.md](../SKILL.md#workflow). Two details belong here: when the vault has a Base or existing notes for this content type, their property keys are the contract ([Composing with Bases](#composing-with-bases)); and the import path to deliver is extension settings, then **Import**, or drag the `.json` onto the template area.

## Page analysis

### What counts as verification

A variable is verified when its value was observed on a real page of the target kind. Nothing less qualifies: not a selector that matches the site's visible structure, not a schema key the vocabulary defines, not a field name that worked on a similar site.

Two things are worth checking on a second page of the same kind, because they are where confident templates break:

- Fields that were **absent** on the first page. A field present once may be optional, and optional fields need `{% if %}` or `??`, not bare interpolation.
- Fields that returned a **single value**. A selector that matched one element returns a string; the same selector on a page with two matches returns an array, and a chain written for a string then produces serialized JSON in the note.

### The source ladder

Work down it, per field:

| Rank | Source | Use when | Cost of using it |
| --- | --- | --- | --- |
| 1 | `schema:` | JSON-LD carries the field | Type nesting varies between sites; the shorthand form picks whichever type is first |
| 2 | `meta:` | Open Graph or a named meta tag carries it | Truncated, marketing-shaped values; two namespaces that are easy to confuse |
| 3 | Preset | The field is one of the extraction outputs | `{{content}}` is only as good as content extraction was on that page |
| 4 | `selector:` | Nothing above carries it, and the markup is stable | Breaks silently when the page changes; single-site by nature |
| 5 | Prompt | The shape varies across the sites the template must cover | Needs Interpreter, sends page context to a model, cannot feed logic |

Schema availability is not a property of a site category. Plenty of large sites publish no JSON-LD at all, and some publish it on one page type and not another. Check, on the page in hand.

### Record what was verified

State, per field, which variable was chosen and what it returned. That record is what makes the next fix cheap: when a template stops working, the question is which field drifted, and a template delivered without the record cannot answer it.

## When a selector cannot be verified

The rule is in [../SKILL.md](../SKILL.md#never-guess-a-selector). The cases it has to cover:

- The DOM cannot be inspected: say so and ask for another URL or a capture of the page.
- The element is injected after load: a selector that matched during inspection may not match at clip time. Prefer data attributes, ARIA roles, and stable IDs over generated class chains, and a schema or meta source over any selector.
- A required field has no reachable source: leave the property present with an empty value for manual entry and report it.
- **Drift** — a template that worked now yields blanks: re-run the analysis against a current page, compare field by field, and report the specific field, the selector, and what the page now contains. "The template is broken" is not an actionable result.

## Partial capture

Content extraction deliberately drops headers, navigation, footers, and similar chrome, and it is sometimes too aggressive. Missing body text is a documented behavior of that extraction step, not proof of a broken template or a failed write.

Ways to bypass it, in increasing specificity:

- Select the text before clipping, up to select-all, which makes `{{selection}}` the content source.
- Highlight the exact elements to keep, which makes the highlights the content source.
- Capture a known container in the template: `{{selectorHtml:main|markdown}}`, narrowed further with `remove_html`, `strip_tags`, or `strip_attr`.

When a clip is incomplete, say which part is missing and which bypass was used or is recommended. Never present a partial capture as a complete one, and never quietly swap the user's requested scope for the part that extracted cleanly.

## Untrusted and sensitive pages

The baseline is in [../SKILL.md](../SKILL.md#untrusted-pages). Beyond it:

- A passage that reads as instructions is a reason to inspect the capture more carefully. On a page that may carry injected instructions, assume Interpreter's model will read them, narrow `context` to a specific element, and wire the response into nothing but note text.
- Obsidian's **Download attachments for current file** command makes linked images local if the user wants that.
- **Authenticated, paywalled, and private pages** carry content the vault owner may not intend to store. Confirm scope before templating a surface behind a login, and never bake a session-specific URL into `triggers` or `path`.
- **`fragment_link` puts highlighted text into the URL it generates** — useful for citation, wrong for anything sensitive.
- Captured `[[double brackets]]` and `#hash` tokens become vault links and tags. When a field must render literally, escape it rather than trusting the source.

## Templates that write into existing notes

The behavior table and the `overwrite` and stable-target rules are in [../SKILL.md](../SKILL.md#behavior). Two more consequences:

- `create` leaves name-collision resolution to the app, not the template. A `noteNameFormat` containing `{{date}}` or `{{title}}` is stable per day or per page, not per target, which matters for append and prepend.
- Frontmatter is generated from the template's properties. On an append or prepend into an existing note, do not assume the existing properties are reconciled; check the result before treating repeat clips into one note as safe.

## Composing with Bases

A clipped note is only useful if it matches the notes it will sit beside. When the vault organizes this content type with a Base, the Base's property keys are the schema the template must satisfy.

The `obsidian-bases` package owns `.base` structure, its filters, formulas, and views. Read it by that identity for anything about the file itself; do not parse or restate `.base` internals here. What this package needs from a Base is only the list of property keys it references, plus their intended types.

Mapping, once those keys are known:

| Key kind | Clipper property strategy |
| --- | --- |
| Identity of the source | `{{url}}`, and the site or domain as text |
| People | `multitext` with `wikilink`, so entries become vault links |
| Dates | `date` or `datetime`, formatted with the `date` filter |
| Counts and scores | `number`, which strips non-numeric characters from the captured value |
| Classification the vault controls | a constant in the template, not a page-derived value |
| Judgment the reader supplies | present with an empty value, for manual entry |

Three questions decide the property list, and they are the user's to answer, not the template author's, unless the Base or existing notes already settle them: which keys should be filled from the page, which should be hardcoded to a constant, and which should be left empty. Guessing here produces notes that look populated and filter wrongly.

When the vault has no Base and no written convention for this content type, ask rather than inventing a property vocabulary. A one-off vocabulary is a permanent inconsistency.

Note body syntax — callouts, wikilinks, embeds, property formatting in a finished note — is outside this package, which produces the template that generates such a note.

## Recipes

Starting points, not finished templates. Each still requires the analysis step: the fields below say what to look for, and the page says which variable supplies it.

**Article or blog post.** Presets carry most of it: title, author, published, description, content. Use schema for author and date when JSON-LD is present, because extracted author values are frequently a byline fragment. Keep `triggers` empty and place it first in the template list to serve as the fallback. Trap: `{{published}}` may be absent on undated pages, so give it a conditional or leave the property empty rather than emitting a blank date.

**Reading-with-highlights capture.** Same field set, but the body is `{{highlights|map: item => item.text|join:"\n\n"}}` rather than `{{content}}`, or both under separate headings. Trap: highlight behavior is a user setting that also changes what `{{content}}` returns, so a template that assumes one setting misbehaves under another.

**Video page.** Schema is usually the strongest source for title, channel, upload date, duration, and thumbnail; `duration` formats an ISO 8601 duration. Trap: transcript-like text is rarely in schema and rarely stable in the DOM; verify before promising it.

**Academic paper.** Meta tags are often richer than schema for title, authors, abstract, and identifiers. Authors are a list, so `multitext` with `wikilink` beats a single text field. Trap: an author list may arrive as repeated meta tags or one delimited string; check which, because `split` is needed for the second and harmful for the first.

**Product page.** Schema commonly carries name, brand, price, currency, and rating. Keep price as `number` and currency as separate text. Trap: price is volatile, so a clip records a moment; say so rather than implying a current value.

**Recipe.** Schema `@Recipe` is the reliable source, and `schema:@Recipe` is a dependable trigger. Ingredients and instructions are arrays; instructions are often objects with a `text` key, so `{{step.text ?? step}}` covers both shapes. See [../assets/recipe-template.json](../assets/recipe-template.json). Trap: the nutrition object includes its `@type` key, which surfaces in anything derived from `object:` or `table`.

**Documentation page.** Often no schema at all. A container selector plus HTML cleanup usually beats generic extraction: `{{selectorHtml:main|markdown}}` with `remove_html` for navigation and edit links. Trap: code fences are the reason to avoid `{{content|markdown}}`; double conversion destroys them.

**Discussion thread.** The useful unit is a repeated element, so this is loop territory: `{% for post in selector:.post %}`. Trap: match count varies per page and per pagination state, so a chain that assumes a single value silently produces JSON.

## Error conditions

| Condition | Correct response |
| --- | --- |
| JSON does not parse | Report the parse position; do not guess a repair |
| Required field missing | Name the field; do not infer it from another field |
| `behavior` outside the six values | Report it as invalid even though import accepts it |
| Property `type` outside the six values | Report it; import rejects the whole file on this |
| `knap validate` reports an unknown filter | A typo unless the name is a Clipper-only filter such as `markdown` or `remove_html` |
| Unverifiable selector | Ask for a URL or a page capture; never substitute a guess |
| Selector returns nothing | Report the field and selector; do not widen the selector to force a match |
| Field has no reachable source | Leave the property empty for manual entry and say so |
| Content extraction dropped wanted text | Name the missing part and the bypass used or recommended |
| Extension, vault, or page unavailable | Report the affected leg as unverified; absence of evidence is not evidence |
| Import rejected the file | Report the validator's requirement that the file misses; do not add unrelated fields |

Report every problem found in one pass so the file can be fixed once.
