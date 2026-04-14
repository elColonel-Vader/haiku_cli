from __future__ import annotations

from typing import Any

from haiku_cli.models import HaikuAnalysis


def compute_score(analysis: HaikuAnalysis, result: dict[str, Any]) -> int:
    score = 0
    kigo = result.get("kigo") or {}
    kireji = result.get("kireji") or {}
    juxtaposition = result.get("juxtaposition") or {}

    if analysis.valid_structure:
        score += 2
    if kigo.get("present"):
        score += 2
    if kireji.get("present"):
        score += 1
    if result.get("nature_imagery"):
        score += 2
    if result.get("present_tense"):
        score += 1
    if juxtaposition.get("present"):
        score += 2

    return min(score, 10)
