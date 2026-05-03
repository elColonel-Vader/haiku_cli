from __future__ import annotations

import json
import os
from typing import Any
from urllib import request

from haiku_cli.ai import AIResponseError, ProviderUnavailable
from haiku_cli.ai.json_response import parse_model_json_dict
from haiku_cli.ai.prompts import build_system_prompt

# 127.0.0.1 avoids macOS resolving "localhost" to ::1 while the server listens on IPv4 only.
# Override with LMSTUDIO_BASE_URL, e.g. http://192.168.x.x:1234/v1
# when the CLI runs on another host.
DEFAULT_LMSTUDIO_BASE_URL = "http://127.0.0.1:1234/v1"
DEFAULT_LMSTUDIO_API_KEY = "lm-studio"
# Identifier as shown under LM Studio "Loaded Models" (OpenAI-compatible /v1/chat/completions).
DEFAULT_LMSTUDIO_MODEL = "google/gemma-4-e4b"
DEFAULT_LMSTUDIO_MAX_TOKENS = 1800

_SCORE_0_TO_3 = {"type": "integer", "minimum": 0, "maximum": 3}
_SCORE_0_TO_2 = {"type": "integer", "minimum": 0, "maximum": 2}
_STRING_OR_NULL = {"type": ["string", "null"]}
_STRING_ARRAY = {"type": "array", "items": {"type": "string"}}
_NOTE = {"type": "string"}
_LMSTUDIO_RESPONSE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "reasoning",
        "kigo",
        "kireji",
        "bild",
        "gegenwart",
        "natur",
        "verdichtung",
        "hard_fail",
        "overall_score",
        "verdict",
        "suggestions",
    ],
    "properties": {
        "reasoning": {"type": "string"},
        "kigo": {
            "type": "object",
            "additionalProperties": False,
            "required": ["score", "word", "season", "note"],
            "properties": {
                "score": _SCORE_0_TO_3,
                "word": _STRING_OR_NULL,
                "season": _STRING_OR_NULL,
                "note": _NOTE,
            },
        },
        "kireji": {
            "type": "object",
            "additionalProperties": False,
            "required": ["score", "cut_point", "note"],
            "properties": {
                "score": _SCORE_0_TO_3,
                "cut_point": _STRING_OR_NULL,
                "note": _NOTE,
            },
        },
        "bild": {
            "type": "object",
            "additionalProperties": False,
            "required": ["score", "concrete_images", "abstract_words", "note"],
            "properties": {
                "score": _SCORE_0_TO_3,
                "concrete_images": _STRING_ARRAY,
                "abstract_words": _STRING_ARRAY,
                "note": _NOTE,
            },
        },
        "gegenwart": {
            "type": "object",
            "additionalProperties": False,
            "required": ["score", "tense_issues", "note"],
            "properties": {
                "score": _SCORE_0_TO_2,
                "tense_issues": _STRING_ARRAY,
                "note": _NOTE,
            },
        },
        "natur": {
            "type": "object",
            "additionalProperties": False,
            "required": ["score", "elements", "note"],
            "properties": {
                "score": _SCORE_0_TO_2,
                "elements": _STRING_ARRAY,
                "note": _NOTE,
            },
        },
        "verdichtung": {
            "type": "object",
            "additionalProperties": False,
            "required": ["score", "filler_words", "note"],
            "properties": {
                "score": _SCORE_0_TO_2,
                "filler_words": _STRING_ARRAY,
                "note": _NOTE,
            },
        },
        "hard_fail": {
            "type": "object",
            "additionalProperties": False,
            "required": ["triggered", "reason"],
            "properties": {
                "triggered": {"type": "boolean"},
                "reason": _STRING_OR_NULL,
            },
        },
        "overall_score": {"type": "number", "minimum": 0, "maximum": 10},
        "verdict": {
            "type": "string",
            "enum": ["MEISTERHAFT", "GUT", "ORDENTLICH", "SCHWACH", "UNGENÜGEND"],
        },
        "suggestions": _STRING_ARRAY,
    },
}


def _base_url() -> str:
    base_url = os.environ.get("LMSTUDIO_BASE_URL", DEFAULT_LMSTUDIO_BASE_URL).rstrip("/")
    if base_url.endswith("/v1"):
        return base_url
    return f"{base_url}/v1"


def _request_json(
    url: str,
    *,
    method: str = "GET",
    payload: dict[str, Any] | None = None,
    timeout: int = 5,
) -> dict[str, Any]:
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {DEFAULT_LMSTUDIO_API_KEY}",
    }
    data = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(payload).encode("utf-8")

    candidates = [url]
    if "localhost" in url:
        alt = url.replace("localhost", "127.0.0.1", 1)
        if alt != url:
            candidates.append(alt)

    last_exc: OSError | None = None
    raw = ""
    for attempt_url in candidates:
        req = request.Request(attempt_url, data=data, headers=headers, method=method)
        try:
            with request.urlopen(req, timeout=timeout) as response:
                raw = response.read().decode("utf-8")
            break
        except OSError as exc:
            last_exc = exc
    else:
        hint = (
            " Server muss auf demselben Rechner laufen wie dieses Terminal "
            "(bei SSH/Remote: LMSTUDIO_BASE_URL auf die IP des Macs setzen, "
            "Port und Firewall prüfen). Siehe "
            "https://lmstudio.ai/docs/developer/openai-compat (Base URL /v1)."
        )
        raise ProviderUnavailable(
            "LM Studio ist nicht erreichbar. Prüfe, ob der Local Server läuft "
            f"({url}).{hint}"
        ) from last_exc

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ProviderUnavailable("LM Studio hat keine gültige JSON-Antwort geliefert.") from exc

    if not isinstance(parsed, dict):
        raise ProviderUnavailable("LM Studio hat eine unerwartete API-Antwort geliefert.")
    return parsed


def _select_model(model: str | None) -> str:
    if model:
        return model
    return DEFAULT_LMSTUDIO_MODEL


def _max_tokens() -> int:
    raw = os.environ.get("LMSTUDIO_MAX_TOKENS")
    if raw is None:
        return DEFAULT_LMSTUDIO_MAX_TOKENS

    try:
        value = int(raw)
    except ValueError:
        return DEFAULT_LMSTUDIO_MAX_TOKENS

    return value if value > 0 else DEFAULT_LMSTUDIO_MAX_TOKENS


def run_lmstudio_check(
    user_content: str,
    *,
    strict: bool,
    fix: bool,
    model: str | None = None,
) -> dict[str, Any]:
    selected_model = _select_model(model)
    payload = {
        "model": selected_model,
        "messages": [
            {"role": "system", "content": build_system_prompt(strict=strict, fix=fix)},
            {"role": "user", "content": user_content},
        ],
        "temperature": 0.1,
        "max_tokens": _max_tokens(),
        "stream": False,
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "haiku_cli_feedback",
                "strict": True,
                "schema": _LMSTUDIO_RESPONSE_SCHEMA,
            },
        },
    }
    response = _request_json(
        f"{_base_url()}/chat/completions",
        method="POST",
        payload=payload,
        timeout=120,
    )
    try:
        choice = response["choices"][0]
        finish_reason = choice.get("finish_reason")
        content = choice["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise ProviderUnavailable(
            "LM Studio hat keine verwertbare Chat-Antwort geliefert."
        ) from exc

    if finish_reason == "length":
        raise AIResponseError(
            "LM Studio hat die JSON-Antwort wegen des Tokenlimits abgeschnitten. "
            "Erhöhe LMSTUDIO_MAX_TOKENS oder nutze ein Modell mit größerem Kontext."
        )

    if not isinstance(content, str):
        content = json.dumps(content)
    return parse_model_json_dict(content, source="LM Studio")
