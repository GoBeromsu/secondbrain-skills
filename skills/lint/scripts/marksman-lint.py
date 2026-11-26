#!/usr/bin/env python3
"""Heading checks and ambiguous links from the marksman language server, in link-lint.py's TSV.

  BROKEN-HEADING  link to a heading the target note does not have (marksman diagnostic code 2)
  AMBIGUOUS-LINK  link that more than one note answers, usually two notes with the same H1 title
                  (marksman diagnostic code 1)
  DUP-HEADING     a heading text the note already used (from marksman's document symbols)

Links to missing notes are link-lint.py's `BROKEN`, which knows the Term template's planned link,
so marksman's "non-existent document" diagnostics are not repeated here.

Needs no Obsidian. marksman treats a folder as a workspace only when it holds `.git` or
`.marksman.toml`; without either, or when marksman fails, this exits 3 and the check is reported
as Not checked.
"""
import argparse
import json
import os
import pathlib
import re
import select
import shutil
import queue
import subprocess
import sys
import threading
import time
import unicodedata
import urllib.parse

NOT_CHECKED = 3
MISSING_HEADING = re.compile(r"^Link to non-existent heading '.*' in document '(.*)'$")
SKIP_DIRS = {".git", ".obsidian", ".trash", "node_modules"}


def nfc(s):
    return unicodedata.normalize("NFC", s)


class Server:
    """A marksman process spoken to over LSP stdio. Every read is bounded by a deadline."""

    def __init__(self, exe):
        self.p = subprocess.Popen([exe, "server"], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                  stderr=subprocess.DEVNULL, bufsize=0)
        self.buf = b""
        # Writes go through a thread so a large didOpen never blocks reading the server's replies.
        self.out = queue.Queue()
        self.writer = threading.Thread(target=self._write, daemon=True)
        self.writer.start()

    def _write(self):
        while True:
            data = self.out.get()
            if data is None:
                return
            try:
                self.p.stdin.write(data)
            except OSError:
                return

    def send(self, msg):
        body = json.dumps(msg).encode()
        self.out.put(b"Content-Length: %d\r\n\r\n" % len(body) + body)

    def _fill(self, deadline):
        left = max(deadline - time.monotonic(), 0)
        if not select.select([self.p.stdout], [], [], left)[0]:
            return False
        chunk = os.read(self.p.stdout.fileno(), 65536)
        if not chunk:
            raise RuntimeError("marksman exited")
        self.buf += chunk
        return True

    def recv(self, timeout):
        """One message, or None if none arrives in `timeout` seconds."""
        deadline = time.monotonic() + timeout
        while b"\r\n\r\n" not in self.buf:
            if not self._fill(deadline):
                return None
        head, rest = self.buf.split(b"\r\n\r\n", 1)
        size = next(int(h.split(b":")[1]) for h in head.split(b"\r\n") if h.lower().startswith(b"content-length"))
        while len(rest) < size:
            if not self._fill(deadline):
                raise RuntimeError("marksman sent a truncated message")
            head, rest = self.buf.split(b"\r\n\r\n", 1)
        self.buf = rest[size:]
        return json.loads(rest[:size])

    def close(self):
        self.out.put(None)
        self.p.kill()
        self.p.wait()


def files_in(root, scope):
    real = os.path.realpath(root)
    for s in scope:
        full = os.path.realpath(os.path.join(root, s))
        if full != real and not full.startswith(real + os.sep):
            raise RuntimeError("scope %r is outside the vault" % s)
        if os.path.isfile(full):
            yield full
            continue
        for d, dirs, names in os.walk(full):
            dirs[:] = sorted(x for x in dirs if x not in SKIP_DIRS)
            for n in sorted(names):
                p = os.path.join(d, n)
                if n.endswith(".md") and not n.endswith(".excalidraw.md") and os.path.realpath(p).startswith(real + os.sep):
                    yield p


def utf16_col(line, col):
    """Python index of LSP UTF-16 column `col` in `line`."""
    units = 0
    for i, ch in enumerate(line):
        if units >= col:
            return i
        units += 2 if ord(ch) > 0xFFFF else 1
    return len(line)


def headings(symbols):
    for s in symbols or []:
        yield s
        yield from headings(s.get("children"))


def collect(exe, root, paths, quiet, limit):
    """({path: diagnostics}, {path: document symbols}) for every path, or raise."""
    uri = pathlib.Path(root).as_uri()
    deadline = time.monotonic() + limit  # one bound for the whole run, launch included
    srv = Server(exe)
    diags, symbols, texts = {}, {}, {}
    try:
        srv.send({"jsonrpc": "2.0", "id": 0, "method": "initialize", "params": {
            "processId": os.getpid(), "rootUri": uri, "workspaceFolders": [{"uri": uri, "name": "vault"}],
            "capabilities": {"textDocument": {"publishDiagnostics": {},
                                              "documentSymbol": {"hierarchicalDocumentSymbolSupport": True}}}}})
        pending = {0: None}

        def pump(timeout):
            left = deadline - time.monotonic()
            if left <= 0:
                raise RuntimeError("marksman did not finish within %gs (--timeout)" % limit)
            msg = srv.recv(min(timeout, left))
            if msg is None:
                return False
            if "method" in msg and "id" in msg:
                srv.send({"jsonrpc": "2.0", "id": msg["id"], "result": None})
            elif msg.get("method") == "textDocument/publishDiagnostics":
                path = urllib.parse.unquote(urllib.parse.urlparse(msg["params"]["uri"]).path)
                diags[path] = msg["params"]["diagnostics"]
            elif msg.get("id") in pending:
                if "error" in msg:
                    raise RuntimeError("marksman: %s" % msg["error"].get("message"))
                path = pending.pop(msg["id"])
                if path:
                    symbols[path] = msg.get("result") or []
            return True

        while 0 in pending:
            pump(1)
        srv.send({"jsonrpc": "2.0", "method": "initialized", "params": {}})
        for i, path in enumerate(paths, start=1):
            with open(path, encoding="utf-8", errors="replace") as f:
                texts[path] = f.read()
            doc = {"uri": pathlib.Path(path).as_uri()}
            srv.send({"jsonrpc": "2.0", "method": "textDocument/didOpen", "params": {"textDocument": dict(
                doc, languageId="markdown", version=1, text=texts[path])}})
            srv.send({"jsonrpc": "2.0", "id": i, "method": "textDocument/documentSymbol", "params": {"textDocument": doc}})
            pending[i] = path
            while pump(0):  # keep reading while the writer thread sends
                pass
        # Every document answered its symbol request, so every open was processed; diagnostics are
        # pushed as each update finishes, so wait until the server goes quiet.
        while pending:
            pump(1)
        # marksman pushes diagnostics only for documents that have some, and LSP gives no "all
        # published" signal; every document has been processed (it answered its symbol request), so
        # wait until the server stays quiet for --quiet seconds.
        while pump(quiet):
            pass
        if time.monotonic() >= deadline:
            raise RuntimeError("marksman did not go quiet within %gs (--timeout)" % limit)
    finally:
        srv.close()
    return diags, symbols, texts


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--vault", required=True)
    ap.add_argument("--scope", nargs="*", default=["."])
    ap.add_argument("--baseline")
    ap.add_argument("--marksman", default=shutil.which("marksman") or os.path.expanduser("~/.local/bin/marksman"))
    ap.add_argument("--quiet", type=float, default=2.0, help="seconds without a message that end the run")
    ap.add_argument("--timeout", type=float, default=600, help="seconds before an unfinished run is Not checked")
    a = ap.parse_args(argv)
    root = os.path.realpath(a.vault)
    if not os.path.isfile(a.marksman) or not os.access(a.marksman, os.X_OK):
        sys.stderr.write("marksman not found; heading links, ambiguous links and duplicate headings are Not checked\n")
        return NOT_CHECKED
    if not any(os.path.exists(os.path.join(root, m)) for m in (".git", ".marksman.toml")):
        sys.stderr.write("%s has no .git or .marksman.toml, so marksman sees no workspace; Not checked\n" % root)
        return NOT_CHECKED
    try:
        paths = sorted(set(files_in(root, a.scope)))
        diags, symbols, texts = collect(a.marksman, root, paths, a.quiet, a.timeout)
        # Documents a link can name: file names and H1 titles of every note in the vault, not only the scope.
        titles = set()
        for path in files_in(root, ["."]):
            titles.add(os.path.basename(path)[:-3])
            with open(path, encoding="utf-8", errors="replace") as f:
                for line in f:
                    if line.startswith("# "):
                        titles.add(line[2:].strip())
                        break
    except (RuntimeError, OSError, ValueError) as e:
        sys.stderr.write("%s; Not checked\n" % e)
        return NOT_CHECKED

    rows = []
    for path in paths:
        lines = texts[path].split("\n")
        rel = nfc(os.path.relpath(path, root))
        for d in diags.get(os.path.realpath(path), diags.get(path, [])):
            code, msg = str(d.get("code")), d.get("message", "")
            if code == "1":
                rule = "AMBIGUOUS-LINK"
            elif code == "2" and MISSING_HEADING.match(msg) and MISSING_HEADING.match(msg).group(1) in titles:
                # A missing document is link-lint.py's BROKEN, fragment or not.
                rule = "BROKEN-HEADING"
            else:
                continue
            r = d["range"]
            line = r["start"]["line"]
            text = lines[line] if line < len(lines) else ""
            end = utf16_col(text, r["end"]["character"]) if r["end"]["line"] == line else len(text)
            rows.append((rel, line + 1, rule, text[utf16_col(text, r["start"]["character"]):end]))
        seen = set()
        for s in sorted(headings(symbols.get(path)), key=lambda s: s["range"]["start"]["line"]):
            title = s["name"].split("\n", 1)[0].strip()
            line = s["selectionRange"]["start"]["line"]
            if title in seen:
                rows.append((rel, line + 1, "DUP-HEADING", lines[line].strip()))
            seen.add(title)

    known = set()
    if a.baseline:
        with open(a.baseline, encoding="utf-8") as f:
            for line in f:
                p = line.rstrip("\n").split("\t")
                if len(p) == 4:
                    known.add((p[0], p[1], p[3]))
    n = 0
    for rel, line, rule, snip in sorted(rows):
        snip = snip[:120].replace("\t", " ").replace("\n", " ")
        if (rule, rel, snip) in known:
            continue
        sys.stdout.write("%s\t%s\t%d\t%s\n" % (rule, rel, line, snip))
        n += 1
    sys.stdout.write("# violations=%d\n" % n)
    return 1 if n else 0


if __name__ == "__main__":
    sys.exit(main())
