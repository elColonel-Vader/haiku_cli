from __future__ import annotations

import json
from urllib import request
from typing import Any

from haiku_cli.ai import ProviderUnavailable
from haiku_cli.ai.json_response import parse_model_json_dict
from haiku_cli.ai.prompts import build_system_prompt

DEFAULT_OLLAMA_MODEL = "deepseek-r1:14b"
DEFAULT_OLLAMA_BASE_URL = "http://localhost:11434"


def _run_ollama_http_check(
    user_content: str,
    *,
    strict: bool,
    fix: bool,
    model: str,
) -> dict[str, Any]:
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": build_system_prompt(strict=strict, fix=fix)},
            {"role": "user", "content": user_content},
        ],
        "format": "json",
        "stream": False,
        "options": {"temperature": 0.1},
    }
    req = request.Request(
        f"{DEFAULT_OLLAMA_BASE_URL}/api/chat",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=120) as response:
            raw = response.read().decode("utf-8")
    except OSError as exc:
        raise ProviderUnavailable(
            "Ollama ist nicht erreichbar. "
            "Prüfe, ob der Dienst läuft und das Modell vorhanden ist."
        ) from exc

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ProviderUnavailable("Ollama hat keine gültige API-Antwort geliefert.") from exc

    if not isinstance(parsed, dict):
        raise ProviderUnavailable("Ollama hat eine unerwartete API-Antwort geliefert.")

    try:
        content = parsed["message"]["content"]
    except (KeyError, TypeError) as exc:
        raise ProviderUnavailable("Ollama hat keine verwertbare Chat-Antwort geliefert.") from exc

    if not isinstance(content, str):
        content = json.dumps(content, ensure_ascii=False)
    return parse_model_json_dict(content, source="Ollama")


def run_ollama_check(
    user_content: str,
    *,
    strict: bool,
    fix: bool,
    model: str | None = None,
) -> dict[str, Any]:
    selected_model = model or DEFAULT_OLLAMA_MODEL
    try:
        from ollama import Client
    except ImportError:
        return _run_ollama_http_check(
            user_content,
            strict=strict,
            fix=fix,
            model=selected_model,
        )

    client = Client()

    try:  # pragma: no cover - depends on local service
        response = client.chat(
            model=selected_model,
            messages=[
                {"role": "system", "content": build_system_prompt(strict=strict, fix=fix)},
                {"role": "user", "content": user_content},
            ],
            format="json",
            options={"temperature": 0.1},
        )
    except Exception as exc:
        raise ProviderUnavailable(
            "Ollama ist nicht erreichbar. "
            "Prüfe, ob der Dienst läuft und das Modell vorhanden ist."
        ) from exc

    if isinstance(response, dict):
        content = response["message"]["content"]
    else:
        content = response.message.content
    if not isinstance(content, str):
        content = json.dumps(content, ensure_ascii=False)
    return parse_model_json_dict(content, source="Ollama")
