from __future__ import annotations

from dataclasses import dataclass
from typing import Any, ClassVar, Mapping, Sequence

from haiku_cli.models import HaikuAnalysis

THREE_LEVEL_SCORES: dict[str, float] = {"absent": 0.0, "weak": 1.0, "strong": 2.0}
HALF_STEP_LEVEL_SCORES: dict[str, float] = {"absent": 0.0, "weak": 0.5, "strong": 1.0}
IMAGE_COHERENCE_SCORES: dict[str, float] = {
    "fragmented": 0.0,
    "loosely_connected": 1.0,
    "coherent": 2.0,
}
SHOW_NOT_TELL_SCORES: dict[str, float] = {"telling": 0.0, "mixed": 1.0, "showing": 2.0}
MONO_NO_AWARE_SCORES: dict[str, float] = {"absent": 0.0, "present": 1.0}


def _extract_level(
    value: Any,
    *,
    level_scores: Mapping[str, float],
    legacy_true: str,
    legacy_false: str,
) -> str:
    if isinstance(value, dict):
        level = value.get("level")
        if isinstance(level, str) and level in level_scores:
            return level
        if "present" in value:
            return legacy_true if bool(value.get("present")) else legacy_false
    elif isinstance(value, bool):
        return legacy_true if value else legacy_false

    return legacy_false


def get_kigo_level(result: dict[str, Any]) -> str:
    return _extract_level(
        result.get("kigo"),
        level_scores=THREE_LEVEL_SCORES,
        legacy_true="strong",
        legacy_false="absent",
    )


def get_kireji_level(result: dict[str, Any]) -> str:
    return _extract_level(
        result.get("kireji"),
        level_scores=HALF_STEP_LEVEL_SCORES,
        legacy_true="strong",
        legacy_false="absent",
    )


def get_nature_imagery_level(result: dict[str, Any]) -> str:
    return _extract_level(
        result.get("nature_imagery"),
        level_scores=THREE_LEVEL_SCORES,
        legacy_true="strong",
        legacy_false="absent",
    )


def get_present_tense_level(result: dict[str, Any]) -> str:
    return _extract_level(
        result.get("present_tense"),
        level_scores=HALF_STEP_LEVEL_SCORES,
        legacy_true="strong",
        legacy_false="absent",
    )


def get_juxtaposition_level(result: dict[str, Any]) -> str:
    return _extract_level(
        result.get("juxtaposition"),
        level_scores=THREE_LEVEL_SCORES,
        legacy_true="strong",
        legacy_false="absent",
    )


def get_image_coherence_level(result: dict[str, Any]) -> str:
    return _extract_level(
        result.get("image_coherence"),
        level_scores=IMAGE_COHERENCE_SCORES,
        legacy_true="coherent",
        legacy_false="fragmented",
    )


def get_show_not_tell_level(result: dict[str, Any]) -> str:
    return _extract_level(
        result.get("show_not_tell"),
        level_scores=SHOW_NOT_TELL_SCORES,
        legacy_true="showing",
        legacy_false="telling",
    )


def get_mono_no_aware_level(result: dict[str, Any]) -> str:
    return _extract_level(
        result.get("mono_no_aware"),
        level_scores=MONO_NO_AWARE_SCORES,
        legacy_true="present",
        legacy_false="absent",
    )


@dataclass(frozen=True)
class ScoreBreakdown:
    """Form (0–2), Haiku-Qualität (0–12) und normalisierte Gesamtwertung (0–10)."""

    form: int
    quality: float
    raw_total: float
    normalized: int
    mono_no_aware_bonus: int
    pre_cap_overall: int
    suggestions_cap_applied: bool
    overall: int

    FORM_MAX: ClassVar[int] = 2
    QUALITY_MAX: ClassVar[int] = 12
    RAW_MAX: ClassVar[int] = 14
    OVERALL_MAX: ClassVar[int] = 10


def compute_score(
    analysis: HaikuAnalysis,
    result: dict[str, Any],
    suggestions: Sequence[str] | None = None,
) -> ScoreBreakdown:
    form = 2 if analysis.valid_structure else 0

    quality = (
        THREE_LEVEL_SCORES[get_kigo_level(result)]
        + HALF_STEP_LEVEL_SCORES[get_kireji_level(result)]
        + THREE_LEVEL_SCORES[get_nature_imagery_level(result)]
        + HALF_STEP_LEVEL_SCORES[get_present_tense_level(result)]
        + THREE_LEVEL_SCORES[get_juxtaposition_level(result)]
        + IMAGE_COHERENCE_SCORES[get_image_coherence_level(result)]
        + SHOW_NOT_TELL_SCORES[get_show_not_tell_level(result)]
    )

    raw_total = form + quality
    normalized = round((raw_total / ScoreBreakdown.RAW_MAX) * ScoreBreakdown.OVERALL_MAX)
    mono_no_aware_bonus = (
        1
        if get_mono_no_aware_level(result) == "present"
        and normalized < ScoreBreakdown.OVERALL_MAX
        else 0
    )

    has_hints = bool(suggestions)
    pre_cap_overall = normalized + mono_no_aware_bonus
    overall = pre_cap_overall
    suggestions_cap_applied = False
    if overall == ScoreBreakdown.OVERALL_MAX and has_hints:
        overall = ScoreBreakdown.OVERALL_MAX - 1
        suggestions_cap_applied = True

    return ScoreBreakdown(
        form=form,
        quality=quality,
        raw_total=raw_total,
        normalized=normalized,
        mono_no_aware_bonus=mono_no_aware_bonus,
        pre_cap_overall=pre_cap_overall,
        suggestions_cap_applied=suggestions_cap_applied,
        overall=overall,
    )
