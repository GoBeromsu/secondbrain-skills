# Lint one-liners

Starting points, not a pipeline. Replace `<scope>` and `<vault>` with live paths, always quoted. Prefer `obsidian-cli` for link questions when Obsidian is running; it resolves aliases and headings that `rg` cannot.

Filenames may contain spaces, emoji and newlines: pass paths NUL-separated (`rg --null`/`-0`, `find -print0`, `xargs -0`, `while IFS= read -r -d ''`). In ripgrep `-L` means `--follow`, not "files without match" — use `--files-without-match`.

```bash
# Inventory (count, NUL-safe)
rg --files -0 -g '*.md' "<scope>" | tr -cd '\0' | wc -c

# Link targets used in scope (strip alias and heading)
rg -o --no-filename '\[\[[^]|#]+' "<scope>" | sort -u

# Does a target exist anywhere in the vault
rg --files -g '<name>.md' "<vault>"

# Inbound links to one page from the whole vault
rg -l "\[\[<basename>(\||#|\]\])" "<vault>"

# Link targets per frontmatter key: use the PyYAML recipe below; use link-lint.py for the body

# Contradiction callouts
rg -n '> \[!warning\] Contradiction' "<scope>"

# Field presence: notes lacking the field
rg --files-without-match '^collectionPurpose:' "<raw-scope>"
rg --files-without-match '^explored:' "<wiki-scope>"
rg --files-without-match '^verificationStatus:' "<wiki-scope>"
rg --files-without-match '^claimType:' "<wiki-scope>"
rg --files-without-match '^evidenceScope:' "<wiki-scope>"

# Values outside the allowed set
rg -n '^confidence:' "<wiki-scope>" | rg -v 'confidence: "?(high|medium|low)"?$'
rg -n '^verificationStatus:' "<wiki-scope>" | rg -v 'verificationStatus: "?(verified|partial|unverified|disputed)"?$'

# Restrict this to notes with a lifecycle; use the values allowed by live policy.
rg -n '^status:' "<lifecycle-scope>" | rg -v 'status: "?(todo|inprogress|done|stop)"?$'

# Disputed queue
rg -l '^(verificationStatus: "?disputed"?|disputed: true)$' "<wiki-scope>"

# High confidence without a Bias Check (NUL-safe pipe)
rg -l0 '^confidence: "?high"?$' "<wiki-scope>" \
  | xargs -0 -r rg --files-without-match 'Bias Check'

# explored: true missing exploredBy or exploredDate
rg -l0 '^explored: true$' "<wiki-scope>" \
  | xargs -0 -r rg --files-without-match '^exploredDate:'
rg -l0 '^explored: true$' "<wiki-scope>" \
  | xargs -0 -r rg --files-without-match '^exploredBy:'

# Stale: confidence low with date_modified (compare dates against today - 30)
rg -l0 '^confidence: "?low"?$' "<wiki-scope>" \
  | xargs -0 -r rg -H '^date_modified:'

# Fallback age when date_modified is absent
git log -1 --format=%cs -- "<page>"

# Index catalog vs files: use the index recipe below (all sections, all roles)

# wiki log latest entry. Resolve the path with records.py. Do not read <vault>/log.md.
log=$(python3 "<ingest-scripts>/records.py" --vault "<vault>" --records "<ingest-references>/records.md" | awk -F '\t' '$1=="log"{print $2}')
rg -n '^## \[[0-9]{4}-[0-9]{2}-[0-9]{2}\]' "$log" | tail -n 1

# Backticked URLs (drop hits inside fences, commands, quotations, frontmatter and Raw `## Original Content`)
rg -n -g '*.md' '`https?://[^\s)`]+`' "<scope>"

# Link form (deterministic, offline); keep the output to pass as --baseline next time
python3 "<skill-dir>/scripts/link-lint.py" --vault "<vault>" --scope "<scope>" > link-lint.tsv

# Frontmatter and structure (Step 12). Wiki folder(s) and lifecycle types come from live policy.
# Obsidian already running with this vault open; exit 3 means it is not, so use the next line.
python3 "<skill-dir>/scripts/obsidian-lint.py" --vault "<vault>" --scope "<scope>" \
  --wiki "<wiki-folder>" --lifecycle "<type>,<type>" > policy-lint.tsv
python3 "<skill-dir>/scripts/link-lint.py" --vault "<vault>" --scope "<scope>" --checks policy \
  --wiki "<wiki-folder>" --lifecycle "<type>,<type>" > policy-lint.tsv

# Links to missing headings, ambiguous links, duplicate headings. Needs .git or .marksman.toml at the vault root.
python3 "<skill-dir>/scripts/marksman-lint.py" --vault "<vault>" --scope "<scope>" > marksman-lint.tsv
```

`obsidian eval` needs an IIFE (`code='(()=>{...})()'`, async allowed); `obsidian-lint.py` builds it from `obsidian-lint.js` and passes its arguments in a temp file outside the vault. Run Obsidian CLI commands only through `obsidian-lint.py`: it checks that Obsidian is already running with this vault open before it calls the CLI, and a bare `obsidian` command can launch the app. Its `# properties` line gives the vault-wide counts of `status` and the retired keys.

Link targets by key (read-only, needs PyYAML). Feed NUL-delimited paths: `rg --files -0 -g '*.md' "<scope>" | python3 links.py "<vault>"` (run the snippet from stdin or a temp file outside the vault). If `import yaml` fails, do not run the check and do not substitute a regex: report frontmatter links as **Not checked — PyYAML unavailable**; body links still come from `link-lint.py`.

```python
import sys, os, re
import yaml
vault = sys.argv[1]
LINK = re.compile(r'\[\[([^\]|#]+)')
names, paths = set(), set()
for d, ds, fs in os.walk(vault):
    ds[:] = [x for x in ds if not x.startswith('.')]
    for f in fs:
        rel = os.path.relpath(os.path.join(d, f), vault)
        stem = rel[:-3] if rel.endswith('.md') else rel
        paths.add(stem); paths.add(rel)
        names.add(os.path.basename(stem)); names.add(f)
def resolves(t):
    t = t.strip()
    return t in names or t.lstrip('/') in paths
def walk(v):
    if isinstance(v, str):
        yield from LINK.findall(v)
    elif isinstance(v, list):
        for x in v: yield from walk(x)
    elif isinstance(v, dict):
        for x in v.values(): yield from walk(x)
for p in sys.stdin.buffer.read().split(b'\0'):
    if not p: continue
    p = p.decode()
    text = open(p, encoding='utf-8').read()
    fm = {}
    m = re.match(r'---\n(.*?)\n---\n?', text, re.S)
    if m:
        try:
            fm = yaml.safe_load(m.group(1)) or {}
        except yaml.YAMLError as e:
            print(p, 'frontmatter', 'yaml-error', e, sep='\t'); fm = {}
    for key, val in (fm.items() if isinstance(fm, dict) else []):
        if key == 'author' or (key == 'domain' and fm.get('layer') == 'terms'):
            continue
        for t in walk(val):
            if not resolves(t): print(p, key, t, sep='\t')
```

Use the body `BROKEN` findings from `link-lint.py`. Other keys checked here include `source`, `related`, `book`, `chapterPrev`, `chapterNext`, `personaOf`, and any key the live schema adds. Output is `path<TAB>key<TAB>missing target`.

Index catalog check (read-only): resolves every `[[...]]` in the wiki index against the vault's actual files — Raw, Wiki, Queries, Maps, Personas and whatever sections the live index has — and recounts files per catalogued section. The index path comes from `skills/ingest/scripts/records.py`. `python3 index_check.py "<vault>"`:

```python
import sys, os, re
from pathlib import Path
sys.path.insert(0, "<ingest-scripts>")
from records import resolve_wiki_records
vault = sys.argv[1]
located = resolve_wiki_records(Path(vault), Path("<ingest-references>/records.md"), None, None)
LINK = re.compile(r'\[\[([^\]|#]+)')
names, paths = {}, set()
for d, ds, fs in os.walk(vault):
    ds[:] = [x for x in ds if not x.startswith('.')]
    for f in fs:
        rel = os.path.relpath(os.path.join(d, f), vault)
        stem = rel[:-3] if rel.endswith('.md') else rel
        paths.update((stem, rel))
        names.setdefault(os.path.basename(stem), []).append(rel); names.setdefault(f, []).append(rel)
section, seen = '(top)', {}
for line in open(located.index, encoding='utf-8'):
    h = re.match(r'#{1,6}\s+(.*)', line)
    if h: section = h.group(1).strip(); continue
    for t in LINK.findall(line):
        t = t.strip()
        hit = names.get(t) or ([t] if t.lstrip('/') in paths else [])
        seen.setdefault(section, set()).update(hit)
        if not hit: print('missing', section, t, sep='\t')
        elif len(hit) > 1: print('ambiguous', section, t, *hit, sep='\t')
for s, hits in seen.items():
    print('catalogued', s, len(hits), sep='\t')
```

Then compare each section with its folder on disk (from the live index and vault layout, not assumed names): files present in the folder but in no section are uncatalogued. Recount Stats from these folder counts, never from the old table. A link that resolves to two files with the same basename is ambiguous — report it rather than picking one.

Policy conformance (read-only). Build `policy.json` from the live policy by hand — never guess values: `{"lanes": {"<raw folder>": {"type": "raw-source", "category": "<value>"}}, "retired": ["<key>"], "pairs": [["date modified", "date_modified"]]}`. Then `python3 conform.py "<vault>/10. Raw Sources" policy.json`:

```python
import sys, os, re, json, collections
root, pol = sys.argv[1], json.load(open(sys.argv[2]))
KEY = re.compile(r'^([^\s:#-][^:\n]*):[ \t]*(.*)$', re.M)
groups = collections.defaultdict(list)
for lane in sorted(os.listdir(root)):
    p = os.path.join(root, lane)
    if not os.path.isdir(p) or lane.startswith(('.', '_')): continue
    want = pol['lanes'].get(lane)
    for d, ds, fs in os.walk(p):
        for f in fs:
            if not f.endswith('.md'): continue
            path = os.path.join(d, f)
            m = re.match(r'---\n(.*?)\n---', open(path, encoding='utf-8', errors='replace').read(), re.S)
            fm = {}
            for k, v in KEY.findall(m.group(1) if m else ''):
                fm.setdefault(k.strip().strip('"\''), []).append(v.strip().strip('"\''))
            out = []
            if want is None: out.append('unregistered-folder')
            else:
                for k, v in want.items():
                    if fm.get(k, [None])[0] != v: out.append(f'{k}={fm.get(k, [None])[0]} want {v}')
            out += [f'retired:{k}' for k in pol.get('retired', []) if k in fm]
            out += [f'duplicate:{a}|{b}' for a, b in pol.get('pairs', []) if a in fm and b in fm]
            out += [f'repeated:{k}' for k, v in fm.items() if len(v) > 1]
            if out:
                print(os.path.relpath(path, root), *out, sep='\t')
                prov = tuple(fm.get(k, [''])[0] for k in ('source_extraction', 'ingest_kind', 'store', 'source_kind'))
                groups[prov].append(fm.get('date_created', [''])[0])
for prov, dates in sorted(groups.items(), key=lambda x: -len(x[1])):
    print('group', *prov, len(dates), 'newest', max(dates), sep='\t')
```

The line parser reads only top-level keys; use the PyYAML recipe above when nested values matter.

`--files-without-match` cannot tell frontmatter from body: a field written in the body hides a gap, so spot-read a few results.
