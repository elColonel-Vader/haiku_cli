from __future__ import annotations

import json
import os
from typing import Any
from urllib import request

from haiku_cli.ai import ProviderUnavailable
from haiku_cli.ai.json_response import parse_model_json_dict
from haiku_cli.ai.prompts import build_system_prompt

DEFAULT_LMSTUDIO_BASE_URL = "http://localhost:1234/v1"
DEFAULT_LMSTUDIO_API_KEY = "lm-studio"


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
) -> dict[str, Any]:
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {DEFAULT_LMSTUDIO_API_KEY}",
    }
    data = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(payload).encode("utf-8")

    req = request.Request(url, data=data, headers=headers, method=method)
    try:
        with request.urlopen(req, timeout=5) as response:
            raw = response.read().decode("utf-8")
    except OSError as exc:
        raise ProviderUnavailable(
            "LM Studio ist nicht erreichbar. Prüfe, ob der Local Server läuft "
            f"({url})."
        ) from exc

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ProviderUnavailable("LM Studio hat keine gültige JSON-Antwort geliefert.") from exc

    if not isinstance(parsed, dict):
        raise ProviderUnavailable("LM Studio hat eine unerwartete API-Antwort geliefert.")
    return parsed


def _list_models() -> list[dict[str, Any]]:
    response = _request_json(f"{_base_url()}/models")
    models = response.get("data")
    if not isinstance(models, list):
        raise ProviderUnavailable("LM Studio liefert keine Modellliste am /models-Endpoint.")
    return [model for model in models if isinstance(model, dict)]


def _select_model(model: str | None) -> str:
    if model:
        return model

    models = _list_models()
    for entry in models:
        model_id = entry.get("id")
        if isinstance(model_id, str) and model_id.strip():
            return model_id

    raise ProviderUnavailable(
        "LM Studio ist erreichbar, aber es ist kein geladenes Modell verfügbar. "
        "Starte den Local Server mit einem Modell oder nutze --model."
    )


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
    response = _request_json(f"{_base_url()}/chat/completions", method="POST", payload=payload)
    try:
        content = response["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise ProviderUnavailable(
            "LM Studio hat keine verwertbare Chat-Antwort geliefert."
        ) from exc

    if not isinstance(content, str):
        content = json.dumps(content)
    return parse_model_json_dict(content, source="LM Studio")
