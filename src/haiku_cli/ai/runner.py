from __future__ import annotations

from typing import Any

from haiku_cli.ai import AIResponseError, ProviderUnavailable
from haiku_cli.ai.claude import run_claude_check
from haiku_cli.ai.ollama import run_ollama_check


def run_ai_check(
    lines: tuple[str, str, str],
    *,
    provider: str,
    strict: bool,
    fix: bool,
    model: str | None = None,
) -> dict[str, Any]:
    if provider == "ollama":
        return run_ollama_check(lines, strict=strict, fix=fix, model=model)
    if provider == "claude":
        return run_claude_check(lines, strict=strict, fix=fix, model=model)
    raise ProviderUnavailable(f"Unbekannter Provider: {provider}")


def evaluate_strict_result(result: dict[str, Any]) -> bool:
    kigo = result.get("kigo") or {}
    kireji = result.get("kireji") or {}
    juxtaposition = result.get("juxtaposition") or {}
    return all(
        (
            bool(kigo.get("present")),
            bool(kireji.get("present")),
            bool(result.get("present_tense")),
            bool(result.get("nature_imagery")),
            bool(juxtaposition.get("present")),
        )
    )


__all__ = ["AIResponseError", "ProviderUnavailable", "evaluate_strict_result", "run_ai_check"]
