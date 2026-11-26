#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path


class RecordError(Exception):
    pass


@dataclass(frozen=True)
class PathOverride:
    index: str | None
    log: str | None


@dataclass(frozen=True)
class RecordLocation:
    path: Path | None
    reason: str = ""


@dataclass(frozen=True)
class WikiRecords:
    index: RecordLocation
    log: RecordLocation


def parse_record_keys(text: str, index_required: bool, log_required: bool) -> PathOverride:
    if text.startswith("\ufeff"):
        text = text[1:]
    index: str | None = None
    log: str | None = None
    seen_index = False
    seen_log = False
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("wiki-index:"):
            if not index_required:
                continue
            if seen_index:
                raise RecordError("wiki-index appears twice")
            seen_index = True
            index = line.split(":", 1)[1].strip()
            if index == "":
                raise RecordError("wiki-index is empty")
        elif line.startswith("wiki-log:"):
            if not log_required:
                continue
            if seen_log:
                raise RecordError("wiki-log appears twice")
            seen_log = True
            log = line.split(":", 1)[1].strip()
            if log == "":
                raise RecordError("wiki-log is empty")
    return PathOverride(index=index, log=log)


def find_vault_root(start: Path) -> Path:
    current = start.expanduser()
    if not current.is_absolute():
        current = Path.cwd() / current
    chain = [current]
    chain.extend(current.parents)
    for ancestor in chain:
        if (ancestor / ".obsidian").is_dir():
            return ancestor.resolve()
    for ancestor in chain:
        if (ancestor / "AGENTS.md").is_file():
            return ancestor.resolve()
    raise RecordError("no ancestor contains .obsidian or AGENTS.md; pass --vault VAULT")


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError as exc:
        raise RecordError(f"cannot read {path.name} as UTF-8") from exc


def _place(vault: Path, value: str, label: str) -> Path:
    if not value.strip() or any(char in value for char in "\t\r\n\0"):
        raise RecordError(f"{label} must be a nonempty relative path without control characters")
    raw = Path(value)
    if not raw.parts or raw.is_absolute() or ".." in raw.parts:
        raise RecordError(f"{label} must be a relative path inside the vault")
    placed = vault / raw
    real = placed.resolve()
    if not real.is_relative_to(vault) or real == vault:
        raise RecordError(f"{label} must stay strictly inside the vault")
    return placed


def resolve_wiki_records(
    vault: Path,
    wiki_folder: str,
    index_override: str | None = None,
    log_override: str | None = None,
) -> WikiRecords:
    vault = vault.resolve()
    if not vault.is_dir():
        raise RecordError(f"vault {vault} is not a directory")
    wiki = _place(vault, wiki_folder, "wiki role")
    wiki_real = wiki.resolve()
    if wiki.exists() and not wiki.is_dir():
        raise RecordError("wiki role must name a folder")
    agents_path = vault / "AGENTS.md"

    def locate(label: str, override: str | None) -> RecordLocation:
        try:
            value = override
            if value is None and agents_path.is_file():
                _place(vault, "AGENTS.md", "vault configuration")
                keys = parse_record_keys(_read_text(agents_path), label == "index", label == "log")
                value = keys.index if label == "index" else keys.log
            if value is None:
                return RecordLocation(None, "not configured")
            path = _place(vault, value, f"wiki-{label}")
            real = path.resolve()
            if not path.is_relative_to(wiki) or not real.is_relative_to(wiki_real) or real == wiki_real:
                raise RecordError(f"wiki-{label} must stay strictly beneath the wiki role")
            if path.exists() and not path.is_file():
                raise RecordError(f"wiki-{label} must name a file")
            return RecordLocation(path)
        except (RecordError, OSError, RuntimeError) as exc:
            return RecordLocation(None, str(exc))

    return WikiRecords(
        index=locate("index", index_override),
        log=locate("log", log_override),
    )


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Print the wiki index and log paths.")
    parser.add_argument("--vault", required=True)
    parser.add_argument("--wiki", required=True, help="Vault-relative wiki folder from the live guideline.")
    parser.add_argument("--index")
    parser.add_argument("--log")
    args = parser.parse_args(argv)
    try:
        located = resolve_wiki_records(
            Path(args.vault).expanduser().resolve(),
            args.wiki,
            args.index,
            args.log,
        )
    except (RecordError, OSError, RuntimeError) as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        return 2
    for label, record in (("index", located.index), ("log", located.log)):
        if record.path is None:
            reason = " ".join(record.reason.split())
            print(f"{label}\tunavailable\t{reason}")
        else:
            print(f"{label}\tpath\t{record.path}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
