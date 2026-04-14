from __future__ import annotations

import json
import re
from typing import Any

from haiku_cli.ai import AIResponseError

_FENCE_RE = re.compile(r"```(?:json)?\s*([\s\S]*?)\s*```", re.IGNORECASE)
def _normalize_llm_json_text(text: str) -> str:
    """Repair common non-standard JSON emitted by local LLMs before json.loads."""
    t = text.strip()
    t = (
        t.replace("\u201c", '"')
        .replace("\u201d", '"')
        .replace("\u201e", '"')
        .replace("\u201a", "'")
        .replace("\u2018", "'")
        .replace("\u2019", "'")
    )
    t = re.sub(r"\bTrue\b", "true", t)
    t = re.sub(r"\bFalse\b", "false", t)
    t = re.sub(r"\bNone\b", "null", t)
    t = re.sub(r"\bundefined\b", "null", t)
    prev = None
    while prev != t:
        prev = t
        t = re.sub(r",(\s*})", r"\1", t)
        t = re.sub(r",(\s*])", r"\1", t)
    return t


def _coerce_parsed_json(parsed: Any) -> dict[str, Any] | None:
    """Accept a dict, or a one-element list wrapping a dict, or a JSON string of an object."""
    if isinstance(parsed, dict):
        return parsed
    if isinstance(parsed, list) and len(parsed) == 1 and isinstance(parsed[0], dict):
        return parsed[0]
    if isinstance(parsed, str):
        s = parsed.strip()
        if s.startswith("{"):
            try:
                inner = json.loads(_normalize_llm_json_text(s))
            except json.JSONDecodeError:
                return None
            return _coerce_parsed_json(inner)
    return None


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
        normalized = _normalize_llm_json_text(candidate)
        try:
            parsed = json.loads(normalized)
        except json.JSONDecodeError:
            continue
        coerced = _coerce_parsed_json(parsed)
        if coerced is not None:
            return coerced

    extracted = _extract_first_json_object(cleaned)
    if extracted:
        normalized = _normalize_llm_json_text(extracted)
        try:
            parsed = json.loads(normalized)
        except json.JSONDecodeError as exc:
            raise AIResponseError(f"{source} hat kein gültiges JSON geliefert.") from exc
        coerced = _coerce_parsed_json(parsed)
        if coerced is not None:
            return coerced

    raise AIResponseError(f"{source} hat kein gültiges JSON geliefert.")
