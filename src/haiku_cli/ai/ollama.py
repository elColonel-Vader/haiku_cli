from __future__ import annotations

from typing import Any

from haiku_cli.ai import ProviderUnavailable
from haiku_cli.ai.json_response import parse_model_json_dict
from haiku_cli.ai.prompts import build_system_prompt

DEFAULT_OLLAMA_MODEL = "gemma4:e4b"


def run_ollama_check(
    user_content: str,
    *,
    strict: bool,
    fix: bool,
    model: str | None = None,
) -> dict[str, Any]:
    try:
        from ollama import Client
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise ProviderUnavailable(
            "Das Paket 'ollama' ist nicht installiert. Installiere die AI-Extras."
        ) from exc

    client = Client()
    selected_model = model or DEFAULT_OLLAMA_MODEL

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
    return parse_model_json_dict(content, source="Ollama")
