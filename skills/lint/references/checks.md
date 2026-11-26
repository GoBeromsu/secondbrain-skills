# Lint recipes

Starting points, not a pipeline. Quote every `<scope>` and `<vault>`. Filenames may contain spaces, emoji and newlines: pass paths NUL-separated (`rg --null`/`-0`, `find -print0`, `xargs -0 -r`). In ripgrep `-L` means `--follow`; use `--files-without-match`, which cannot tell frontmatter from body, so spot-read a few results.

```bash
# Notes carrying a property (Status mode), one count per key
for k in status youtube x; do printf '%s\t' "$k"; rg -l0 -PU '\A---\n(?:(?!---$).*\n)*?'"$k:" -g '*.md' "<vault>" | tr -cd '\0' | wc -c; done

# High confidence without a Bias Check
rg -l0 '^confidence: "?high"?$' "<wiki-scope>" | xargs -0 -r rg --files-without-match 'Bias Check'

# Wiki log latest entry (vault-relative wiki folder from live policy; without one, the log is unavailable)
if records=$(python3 "<ingest-scripts>/records.py" --vault "<vault>" --wiki "<wiki-folder>"); then
  log=$(printf '%s\n' "$records" | awk -F '\t' '$1=="log" && $2=="path"{print $3}')
  if [ -z "$log" ]; then
    printf '%s\n' "$records" | awk -F '\t' '$1=="log" && $2=="unavailable"{print "Wiki log unavailable: " $3}'
  elif [ ! -f "$log" ]; then
    printf 'Wiki log missing: %s\n' "$log"
  else
    rg -n '^## \[[0-9]{4}-[0-9]{2}-[0-9]{2}\]' "$log" | tail -n 1
  fi
else
  printf 'Wiki log unavailable: record resolution blocked\n'
fi

# Scripts; keep each output to pass as --baseline next time
python3 "<skill-dir>/scripts/link-lint.py" --vault "<vault>" --scope "<scope>" > link-lint.tsv
python3 "<skill-dir>/scripts/link-lint.py" --vault "<vault>" --scope "<scope>" --checks policy --orphans <policy flags> > policy-lint.tsv
python3 "<skill-dir>/scripts/marksman-lint.py" --vault "<vault>" --scope "<scope>" > marksman-lint.tsv  # needs .git or .marksman.toml at the vault root
```

Index catalog check (read-only, Step 6): resolves every `[[...]]` per index section and counts the files each catalogues. Without a wiki folder in the live guideline, report the index as unavailable instead. `python3 index_check.py "<vault>" "<wiki-folder>"`:

```python
import sys, os, re
from pathlib import Path
sys.path.insert(0, "<ingest-scripts>")
from records import RecordError, resolve_wiki_records
vault = sys.argv[1]
try:
    index = resolve_wiki_records(Path(vault), sys.argv[2]).index
except (RecordError, OSError, RuntimeError) as exc:
    sys.exit(f'Wiki index unavailable: {exc}')
if index.path is None:
    sys.exit(f'Wiki index unavailable: {index.reason}')
if not index.path.is_file():
    sys.exit(f'Wiki index missing: {index.path}')
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
for line in open(index.path, encoding='utf-8'):
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

Then compare each section with its folder on disk (from the live index and vault layout, not assumed names). A link resolving to two files is ambiguous: report it rather than picking one.

Policy conformance (read-only). Build `policy.json` from the live policy by hand — never guess values: `{"lanes": {"<raw folder>": {"type": "raw-source", "category": "<value>"}}, "retired": ["<key>"], "pairs": [["date modified", "date_modified"]]}`. Then `python3 conform.py "<raw-root>" policy.json`:

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

The line parser reads only top-level keys.
