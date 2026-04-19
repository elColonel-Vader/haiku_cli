from __future__ import annotations

import json
import os
from typing import Any
from urllib import request

from haiku_cli.ai import ProviderUnavailable
from haiku_cli.ai.json_response import parse_model_json_dict
from haiku_cli.ai.prompts import build_system_prompt

# 127.0.0.1 avoids macOS resolving "localhost" to ::1 while the server listens on IPv4 only.
# Override with LMSTUDIO_BASE_URL, e.g. http://192.168.x.x:1234/v1
# when the CLI runs on another host.
DEFAULT_LMSTUDIO_BASE_URL = "http://127.0.0.1:1234/v1"
DEFAULT_LMSTUDIO_API_KEY = "lm-studio"
# Identifier as shown under LM Studio "Loaded Models" (OpenAI-compatible /v1/chat/completions).
DEFAULT_LMSTUDIO_MODEL = "google/gemma-4-e4b"


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
    }
    response = _request_json(
        f"{_base_url()}/chat/completions",
        method="POST",
        payload=payload,
        timeout=120,
    )
    try:
        content = response["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise ProviderUnavailable(
            "LM Studio hat keine verwertbare Chat-Antwort geliefert."
        ) from exc

    if not isinstance(content, str):
        content = json.dumps(content)
    return parse_model_json_dict(content, source="LM Studio")
