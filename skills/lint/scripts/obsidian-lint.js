/* Body of `obsidian eval code='...'`, run by obsidian-lint.py, which replaces __ARGS_FILE__ with the
   JSON-quoted path of a temp file holding the arguments. Reads Obsidian's metadataCache.
   Mirrors find_policy() in link-lint.py rule for rule: change both together.
   Block comments only: the code is passed on one command line. */
(async () => {
  const A = JSON.parse(require("fs").readFileSync(__ARGS_FILE__, "utf8"));
  const files = app.vault.getMarkdownFiles().filter((f) => !f.path.endsWith(".excalidraw.md"));
  const first = (v) => (v == null ? [] : [].concat(v));
  const under = (p, d) => d === "." || p === d || p.startsWith(d.replace(/\/$/, "") + "/");
  if (A.mode === "index") {
    const entities = files
      .filter((f) => A.entityFolders.some((d) => under(f.path.normalize("NFC"), d)) ||
        first((app.metadataCache.getFileCache(f) || {}).frontmatter?.layer)[0] === "entities")
      .map((f) => f.path);
    return JSON.stringify({ entities, files: app.vault.getFiles().map((f) => f.path) });
  }

  const KEY = /^([^\s#:\-][^:]*?):(?:[ \t]+(.*?))?[ \t]*$/;
  const PLAIN_URL = /^https?:\/\/[^\s<>\[\]()]+$/i;
  const ANY_URL = /https?:\/\//i;
  const LEGACY = new Set(["youtube", "x"]);
  const AUTO_ZONES = new Set(["Wiki", "From Sources"]);
  const NAME_SKIP = new Set(["aliases", "tags"]);
  const WORD = "A-Za-z0-9_가-힣";
  const PARTICLES =
    "에서는|에게는|으로는|에서도|에게도|으로도|까지는|부터는|에서|에게|으로|이랑|이나|처럼|보다|까지|부터|" +
    "에는|에도|와는|과는|로는|은|는|이|가|을|를|의|에|와|과|로|도|만|랑|나|께";
  const MASKS = [
    /<!--[\s\S]*?-->/g,
    /%%[\s\S]*?%%/g,
    /(`+)[^`\n]+?\1/g,
    /(!?)\[\[([^\]\n]+)\]\]/g,
    /<https?:\/\/[^\s<>]+>/g,
    /(?<![\w/\[<"'=@])https?:\/\/[^\s<>\[\]()"']+/g,
  ];
  const MD_LINK = /(!?)\[([^\]\n]*)\]\(([^)\n]*)\)/dg;
  const lifecycle = new Set(A.lifecycle);
  const bookTypes = new Set(A.bookTypes);
  const entities = new Map(Object.entries(A.entities));
  const unresolved = new Map(Object.entries(A.unresolved || {}));
  const plannedDailyNotes = new Set(A.plannedDailyNotes);
  const esc = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const names = [...entities.keys()].sort((a, b) => b.length - a.length || (a < b ? -1 : a > b ? 1 : 0));
  const pattern = names.length
    ? new RegExp(
        "(?<![" + WORD + "])(?:" + names.map(esc).join("|") + ")(?:(?![" + WORD + "])|(?=(?:" + PARTICLES + ")(?![" + WORD + "])))",
        "g",
      )
    : null;
  const entityText = (name, targets) =>
    name +
    " -> " +
    (targets.length > 1 ? "ambiguous " : "") +
    targets.map((t) => "[[" + (targets.length > 1 ? t : t.split("/").pop()).replace(/\.md$/, "") + "]]").join(" ");
  /* Scalars as strings, as link-lint.py reads them; nested maps are not read. */
  const vals = (v) => first(v).filter((x) => x != null && typeof x !== "object").map(String);
  const byName = new Map();
  for (const f of app.vault.getFiles()) {
    const key = f.name.replace(/\.md$/, "").normalize("NFC");
    if (!byName.has(key)) byName.set(key, []);
    byName.get(key).push(f.path.normalize("NFC"));
  }
  /* Every file a wikilink target names, as link-lint.py's resolve_path() decides it. */
  const resolve = (target) => {
    const t = target.trim().replace(/^\/+|\/+$/g, "").normalize("NFC");
    const base = t.split("/").pop().replace(/\.md$/, "");
    const cands = byName.get(base) || [];
    if (!t.includes("/")) return cands;
    return cands.filter((p) => p === t || p === t + ".md" || p.endsWith("/" + t) || p.endsWith("/" + t + ".md"));
  };
  const unquote = (k) => k.trim().replace(/^"(.*)"$|^'(.*)'$/, "$1$2");
  const out = [];

  for (const f of files) {
    if (!A.scope.some((s) => under(f.path, s))) continue;
    const c = app.metadataCache.getFileCache(f) || {};
    const text = await app.vault.cachedRead(f);
    const lines = text.split("\n");
    const own = f.path.normalize("NFC");
    const push = (rule, line, snip) => out.push([rule, f.path, line, snip]);
    const isWiki = A.wiki.some((d) => under(f.path, d));
    const fm = c.frontmatter || null;
    /* Invalid YAML leaves no frontmatterPosition, but the block is still a yaml section. */
    const fp = c.frontmatterPosition || (c.sections || []).find((s) => s.type === "yaml")?.position;
    const keyLine = new Map();
    if (fp) {
      for (let i = 1; i < fp.end.line; i++) {
        const m = KEY.exec(lines[i] ?? "");
        if (m && !keyLine.has(unquote(m[1]))) keyLine.set(unquote(m[1]), i + 1);
      }
    }
    const content = fp ? lines.slice(1, fp.end.line).some((l) => l.replace(/(^|[ \t])#.*$/, "").trim()) : false;
    if (!fm && content) push("FM-INVALID", 1, "frontmatter does not parse");
    /* Source order, not Object.keys, which moves integer-like keys first. */
    const keys = fm ? [...keyLine.keys()].filter((k) => Object.prototype.hasOwnProperty.call(fm, k)) : [];

    for (let i = 1; i < keys.length; i++) {
      if (keys[i - 1].toLowerCase() > keys[i].toLowerCase()) {
        push("FM-KEY-ORDER", keyLine.get(keys[i]), keys[i - 1] + " > " + keys[i]);
      }
    }
    for (const k of keys) {
      if (LEGACY.has(k)) {
        push("FM-LEGACY-KEY", keyLine.get(k), k);
        continue;
      }
      for (const v of vals(fm[k])) {
        if (k === "url" || k.endsWith("_url")) {
          if (v.trim() && !PLAIN_URL.test(v.trim())) push("FM-URL-FORM", keyLine.get(k), k + ": " + v);
        } else if (isWiki && ANY_URL.test(v)) {
          push("FM-URL-KEY", keyLine.get(k), k + ": " + v);
        }
      }
    }
    let headings = c.headings || [];
    const type = vals(fm?.type);
    if ((type.length === 1 && type[0] === "raw-source") || (vals(fm?.source).length && vals(fm?.tags).includes("raw"))) {
      const original = headings.find((h) => /^ {0,3}## Original Content$/.test((lines[h.position.start.line] ?? "").trimEnd()));
      if (original) {
        const start = original.position.end.line + 1;
        let stop = lines.length;
        for (let i = start; i < lines.length; i++) {
          if (/^<!-- end-original-content -->[ \t]*\r?$/.test(lines[i])) stop = i;
        }
        headings = headings.filter((h) => h.position.start.line < start || h.position.start.line >= stop);
      }
    }
    if (fm && Object.prototype.hasOwnProperty.call(fm, "status")) {
      const kind = first(fm.type).map(String)[0] || "";
      const readingBook = bookTypes.has(kind) && A.entityFolders.some((d) => under(own, d)) &&
        headings.some((h) => h.level === 2 && h.heading === "Reading Progress" &&
          /^ {0,3}##[ \t]/.test(lines[h.position.start.line] ?? ""));
      if (!lifecycle.has(kind) && !readingBook) {
        push("STATUS-NOT-LIFECYCLE", keyLine.get("status"), "status: " + first(fm.status).map(String).join(", "));
      }
    }

    const seen = new Set();
    for (const h of headings) {
      const line = h.position.start.line;
      const snip = (lines[line] ?? "").trim();
      if (seen.has(h.heading)) push("DUP-HEADING", line + 1, snip);
      seen.add(h.heading);
      if (isWiki && AUTO_ZONES.has(h.heading)) push("AUTO-ZONE", line + 1, snip);
    }

    /* Body BROKEN comes from link-lint.py, including its planned-link rules. */
    const missing = new Set(unresolved.get(f.path) || []);
    const isTerm = first(fm?.layer)[0] === "terms";
    for (const l of c.frontmatterLinks || []) {
      const key = l.key.split(".")[0];
      /* As in Step 3: author names and a Term's domain vocabulary may stay unresolved. */
      if (key === "author" || (key === "domain" && isTerm)) continue;
      if (/^\[\[[^#|\]]+(?:\|[^\]]*)?\]\]$/.test(l.original) && plannedDailyNotes.has(l.link)) continue;
      if (missing.has(l.link)) push("BROKEN", keyLine.get(key), l.original);
    }

    if (!isWiki) continue;
    for (const s of c.sections || []) {
      if (s.type === "thematicBreak") push("HR-IN-WIKI", s.position.start.line + 1, (lines[s.position.start.line] ?? "").trim());
    }

    if (!pattern) continue;
    for (const k of keys) {
      if (NAME_SKIP.has(k)) continue;
      for (const v of vals(fm[k])) {
        const targets = (entities.get(v.trim().normalize("NFC")) || []).filter((t) => t !== own);
        if (targets.length) push("ENTITY-UNLINKED", keyLine.get(k), k + ": " + entityText(v, targets));
      }
    }
    /* Only body wikilinks count as linking a body mention. */
    const linked = new Set();
    for (const l of [...(c.links || []), ...(c.embeds || [])]) {
      if (l.position.start.offset < (fp?.end.offset ?? 0) || !/^!?\[\[/.test(l.original)) continue;
      for (const p of resolve(l.link.split("#")[0])) linked.add(p);
    }
    const masked = [];
    if (fp) masked.push([0, fp.end.offset]);
    for (const s of c.sections || []) {
      if (s.type === "code" || s.type === "blockquote" || s.type === "callout") masked.push([s.position.start.offset, s.position.end.offset]);
    }
    for (const h of c.headings || []) masked.push([h.position.start.offset, h.position.end.offset]);
    for (const rx of MASKS) {
      for (const m of text.matchAll(rx)) masked.push([m.index, m.index + m[0].length]);
    }
    for (const m of text.matchAll(MD_LINK)) {
      const externalLabel = !m[1] && /^https?:\/\//i.test(m[3].trim());
      masked.push([externalLabel ? m.indices[2][1] : m.index, m.index + m[0].length]);
    }
    const hidden = (s, e) => masked.some(([a, b]) => a < e && b > s);
    const reported = new Set();
    for (const m of text.matchAll(pattern)) {
      const targets = (entities.get(m[0].normalize("NFC")) || []).filter((t) => t !== own);
      const key = targets.join("\n");
      if (!targets.length || targets.some((t) => linked.has(t)) || reported.has(key) || hidden(m.index, m.index + m[0].length)) continue;
      reported.add(key);
      push("ENTITY-UNLINKED", text.slice(0, m.index).split("\n").length, entityText(m[0], targets));
    }
  }
  return JSON.stringify(out);
})()
