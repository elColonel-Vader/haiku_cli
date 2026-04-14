from __future__ import annotations

import os
from typing import Any

from haiku_cli.ai import ProviderUnavailable
from haiku_cli.ai.json_response import parse_model_json_dict
from haiku_cli.ai.prompts import build_system_prompt


def run_claude_check(
    user_content: str,
    *,
    strict: bool,
    fix: bool,
    model: str | None = None,
) -> dict[str, Any]:
    try:
        from anthropic import Anthropic
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise ProviderUnavailable(
            "Das Paket 'anthropic' ist nicht installiert. Installiere die AI-Extras."
        ) from exc

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ProviderUnavailable("ANTHROPIC_API_KEY ist nicht gesetzt.")

    client = Anthropic(api_key=api_key)
    selected_model = model or "claude-3-5-sonnet-latest"

    try:  # pragma: no cover - depends on external service
        response = client.messages.create(
            model=selected_model,
            max_tokens=1200,
            system=build_system_prompt(strict=strict, fix=fix),
            messages=[
                {
                    "role": "user",
                    "content": user_content,
                }
            ],
        )
    except Exception as exc:
        raise ProviderUnavailable("Claude ist nicht erreichbar.") from exc

    content = "".join(block.text for block in response.content if getattr(block, "text", None))
    return parse_model_json_dict(content, source="Claude")
