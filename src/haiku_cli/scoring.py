from __future__ import annotations

from dataclasses import dataclass
from typing import Any, ClassVar, Sequence

from haiku_cli.models import HaikuAnalysis


@dataclass(frozen=True)
class ScoreBreakdown:
    """Form (0–2) plus Haiku-Qualität (0–8); overall 0–10, capped if hints remain."""

    form: int
    quality: int
    raw_total: int
    overall: int

    FORM_MAX: ClassVar[int] = 2
    QUALITY_MAX: ClassVar[int] = 8


def compute_score(
    analysis: HaikuAnalysis,
    result: dict[str, Any],
    suggestions: Sequence[str] | None = None,
) -> ScoreBreakdown:
    kigo = result.get("kigo") or {}
    kireji = result.get("kireji") or {}
    juxtaposition = result.get("juxtaposition") or {}

    form = 2 if analysis.valid_structure else 0

    quality = 0
    if kigo.get("present"):
        quality += 2
    if kireji.get("present"):
        quality += 1
    if result.get("nature_imagery"):
        quality += 2
    if result.get("present_tense"):
        quality += 1
    if juxtaposition.get("present"):
        quality += 2

    raw_total = min(form + quality, 10)

    has_hints = bool(suggestions)
    overall = 9 if raw_total == 10 and has_hints else raw_total

    return ScoreBreakdown(form=form, quality=quality, raw_total=raw_total, overall=overall)
