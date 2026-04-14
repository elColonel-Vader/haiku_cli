from __future__ import annotations

import re
import unicodedata

WHITESPACE_RE = re.compile(r"\s+")


class ParseError(ValueError):
    pass


def normalize_line(line: str) -> str:
    normalized = unicodedata.normalize("NFC", line).strip()
    return WHITESPACE_RE.sub(" ", normalized)


def parse_haiku(text: str) -> tuple[str, str, str]:
    raw_lines = [normalize_line(line) for line in text.splitlines()]
    lines = [line for line in raw_lines if line]
    if len(lines) != 3:
        raise ParseError("Bitte genau drei nicht-leere Zeilen eingeben.")
    return tuple(lines)  # type: ignore[return-value]
