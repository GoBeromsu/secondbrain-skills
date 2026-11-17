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
class WikiRecords:
    vault: Path
    index: Path
    log: Path


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
    raw = Path(value)
    if raw.is_absolute() or any(part == ".." for part in raw.parts):
        raise RecordError(f"{label} must be a relative path inside the vault")
    if len(raw.parts) < 2:
        raise RecordError(f"{label} must not be the vault root")
    placed = vault / raw
    vault_real = vault.resolve()
    placed_real = placed.resolve()
    if not placed_real.is_relative_to(vault_real) or placed_real.parent == vault_real:
        raise RecordError(f"{label} must stay inside the vault and not at its root")
    return placed


def _choose(caller: str | None, agents: str | None, default: str) -> str:
    if caller is not None:
        if caller.strip() == "":
            raise RecordError("a caller path is empty")
        return caller
    if agents is not None:
        return agents
    return default


def resolve_wiki_records(
    vault: Path,
    records_file: Path,
    index_override: str | None,
    log_override: str | None,
) -> WikiRecords:
    if not vault.is_dir():
        raise RecordError(f"vault {vault} is not a directory")
    if not records_file.is_file():
        raise RecordError(f"records file {records_file} is missing")
    defaults = parse_record_keys(_read_text(records_file), True, True)
    if defaults.index is None or defaults.log is None:
        raise RecordError("records file is missing wiki-index or wiki-log")
    agents = PathOverride(index=None, log=None)
    agents_path = vault / "AGENTS.md"
    need_index = index_override is None
    need_log = log_override is None
    if agents_path.is_file() and (need_index or need_log):
        agents = parse_record_keys(_read_text(agents_path), need_index, need_log)
    index_value = _choose(index_override, agents.index, defaults.index)
    log_value = _choose(log_override, agents.log, defaults.log)
    return WikiRecords(
        vault=vault,
        index=_place(vault, index_value, "wiki-index"),
        log=_place(vault, log_value, "wiki-log"),
    )


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Print the wiki index and log paths.")
    parser.add_argument("--vault", required=True)
    parser.add_argument("--records", required=True)
    parser.add_argument("--index")
    parser.add_argument("--log")
    args = parser.parse_args(argv)
    try:
        located = resolve_wiki_records(
            Path(args.vault).expanduser().resolve(),
            Path(args.records).expanduser(),
            args.index,
            args.log,
        )
    except RecordError as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        return 2
    print(f"index\t{located.index}")
    print(f"log\t{located.log}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
