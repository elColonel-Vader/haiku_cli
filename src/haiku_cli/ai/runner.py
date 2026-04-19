from __future__ import annotations

from typing import Any

from haiku_cli.ai import AIResponseError, ProviderUnavailable
from haiku_cli.ai.claude import run_claude_check
from haiku_cli.ai.lmstudio import run_lmstudio_check
from haiku_cli.ai.ollama import run_ollama_check
from haiku_cli.ai.prompts import build_user_prompt
from haiku_cli.models import HaikuAnalysis
from haiku_cli.scoring import ScoreBreakdown


def run_ai_check(
    lines: tuple[str, str, str],
    analysis: HaikuAnalysis,
    *,
    provider: str,
    strict: bool,
    fix: bool,
    model: str | None = None,
) -> dict[str, Any]:
    user_content = build_user_prompt(lines, analysis)
    if provider == "auto":
        try:
            return run_lmstudio_check(user_content, strict=strict, fix=fix, model=model)
        except (ProviderUnavailable, AIResponseError) as lmstudio_exc:
            try:
                return run_ollama_check(user_content, strict=strict, fix=fix, model=model)
            except (ProviderUnavailable, AIResponseError) as ollama_exc:
                raise ProviderUnavailable(
                    "Kein lokaler KI-Provider verfügbar. "
                    f"LM Studio: {lmstudio_exc} "
                    f"Ollama: {ollama_exc}"
                ) from ollama_exc
    if provider == "ollama":
        return run_ollama_check(user_content, strict=strict, fix=fix, model=model)
    if provider == "lmstudio":
        return run_lmstudio_check(user_content, strict=strict, fix=fix, model=model)
    if provider == "claude":
        return run_claude_check(user_content, strict=strict, fix=fix, model=model)
    raise ProviderUnavailable(f"Unbekannter Provider: {provider}")


def evaluate_strict_result(score_breakdown: ScoreBreakdown) -> bool:
    return score_breakdown.overall >= ScoreBreakdown.STRICT_PASS_THRESHOLD


__all__ = ["AIResponseError", "ProviderUnavailable", "evaluate_strict_result", "run_ai_check"]
