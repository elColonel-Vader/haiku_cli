from __future__ import annotations

import json
import re
from typing import Any

from haiku_cli.ai import AIResponseError

_FENCE_RE = re.compile(r"```(?:json)?\s*([\s\S]*?)\s*```", re.IGNORECASE)


def _candidates_from_fences(text: str) -> list[str]:
    return [m.group(1).strip() for m in _FENCE_RE.finditer(text)]


def _extract_first_json_object(text: str) -> str | None:
    start = text.find("{")
    if start == -1:
        return None

    depth = 0
    in_string = False
    escape = False
    quote = ""

    for i in range(start, len(text)):
        ch = text[i]

        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == quote:
                in_string = False
            continue

        if ch in "\"'":
            in_string = True
            quote = ch
            continue

        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start : i + 1]

    return None


def parse_model_json_dict(raw: str, *, source: str) -> dict[str, Any]:
    if not raw or not raw.strip():
        raise AIResponseError(f"{source} hat kein gültiges JSON geliefert.")

    cleaned = raw.strip()
    try_list: list[str] = [cleaned]
    try_list.extend(_candidates_from_fences(cleaned))

    for candidate in try_list:
        candidate = candidate.strip()
        if not candidate:
            continue
        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            return parsed

    extracted = _extract_first_json_object(cleaned)
    if extracted:
        try:
            parsed = json.loads(extracted)
        except json.JSONDecodeError as exc:
            raise AIResponseError(f"{source} hat kein gültiges JSON geliefert.") from exc
        if isinstance(parsed, dict):
            return parsed

    raise AIResponseError(f"{source} hat kein gültiges JSON geliefert.")
