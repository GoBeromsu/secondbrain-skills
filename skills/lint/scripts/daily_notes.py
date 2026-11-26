"""The optional daily-notes role in a vault's live policy."""

from datetime import date
from pathlib import Path
import re
import unicodedata

ROLE = re.compile(r"^\|[ \t]*daily-notes[ \t]*\|[ \t]*`([^`\n]+)`[ \t]*\|[ \t]*`YYYY-MM-DD`(?=[ \t|])", re.M)
ISO_DATE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")


def daily_notes_folder(vault):
    root = Path(vault).resolve()
    for name in ("AGENTS.md", "Guideline.md"):
        policy = root / name
        if not policy.is_file() or not policy.resolve().is_relative_to(root):
            continue
        matches = ROLE.findall(policy.read_text(encoding="utf-8"))
        if matches:
            folder = matches[0].strip().rstrip("/")
            if len(matches) == 1 and all(part not in ("", ".", "..") for part in folder.split("/")):
                return unicodedata.normalize("NFC", folder)
            return None
    return None


def planned_daily_note(target, folder):
    if folder is None:
        return False
    target = unicodedata.normalize("NFC", target.split("|", 1)[0].strip())
    parent, _, basename = target.lstrip("/").rpartition("/")
    stem = basename.removesuffix(".md")
    if ("/" in target and parent != folder) or not ISO_DATE.fullmatch(stem):
        return False
    try:
        date.fromisoformat(stem)
    except ValueError:
        return False
    return True
