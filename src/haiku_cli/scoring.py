from __future__ import annotations

from dataclasses import dataclass
from typing import Any, ClassVar

CATEGORY_MAX_SCORES: dict[str, int] = {
    "kigo": 3,
    "kireji": 3,
    "bild": 3,
    "gegenwart": 2,
    "natur": 2,
    "verdichtung": 2,
}

CATEGORY_WEIGHTS: dict[str, int] = {
    "kigo": 25,
    "kireji": 20,
    "bild": 25,
    "gegenwart": 10,
    "natur": 10,
    "verdichtung": 10,
}


def _coerce_score(value: Any, *, maximum: int) -> int:
    if not isinstance(value, dict):
        return 0

    score = value.get("score")
    if not isinstance(score, (int, float)):
        return 0

    return max(0, min(int(score), maximum))


def get_category_score(result: dict[str, Any], key: str) -> int:
    return _coerce_score(result.get(key), maximum=CATEGORY_MAX_SCORES[key])


def get_hard_fail(result: dict[str, Any]) -> tuple[bool, str | None]:
    value = result.get("hard_fail")
    if not isinstance(value, dict):
        return False, None

    triggered = bool(value.get("triggered"))
    reason = value.get("reason")
    if reason is None:
        return triggered, None

    normalized = str(reason).strip()
    if not normalized or normalized.casefold() == "null":
        return triggered, None
    return triggered, normalized


def derive_verdict(score: float) -> str:
    if score >= 8.0:
        return "MEISTERHAFT"
    if score >= 6.5:
        return "GUT"
    if score >= 4.5:
        return "ORDENTLICH"
    if score >= 2.5:
        return "SCHWACH"
    return "UNGENÜGEND"


@dataclass(frozen=True)
class ScoreBreakdown:
    kigo: int
    kireji: int
    bild: int
    gegenwart: int
    natur: int
    verdichtung: int
    weighted_points: int
    raw_overall: float
    overall: float
    verdict: str
    hard_fail_triggered: bool
    hard_fail_reason: str | None

    OVERALL_MAX: ClassVar[float] = 10.0
    HARD_FAIL_CAP: ClassVar[float] = 3.0
    STRICT_PASS_THRESHOLD: ClassVar[float] = 6.5
    STRICT_WARN_THRESHOLD: ClassVar[float] = 4.5
    MAX_POSSIBLE: ClassVar[int] = 270


def compute_score(result: dict[str, Any]) -> ScoreBreakdown:
    kigo = get_category_score(result, "kigo")
    kireji = get_category_score(result, "kireji")
    bild = get_category_score(result, "bild")
    gegenwart = get_category_score(result, "gegenwart")
    natur = get_category_score(result, "natur")
    verdichtung = get_category_score(result, "verdichtung")

    weighted_points = (
        kigo * CATEGORY_WEIGHTS["kigo"]
        + kireji * CATEGORY_WEIGHTS["kireji"]
        + bild * CATEGORY_WEIGHTS["bild"]
        + gegenwart * CATEGORY_WEIGHTS["gegenwart"]
        + natur * CATEGORY_WEIGHTS["natur"]
        + verdichtung * CATEGORY_WEIGHTS["verdichtung"]
    )
    raw_overall = round((weighted_points / ScoreBreakdown.MAX_POSSIBLE) * 10, 1)

    hard_fail_triggered, hard_fail_reason = get_hard_fail(result)
    overall = min(raw_overall, ScoreBreakdown.HARD_FAIL_CAP) if hard_fail_triggered else raw_overall
    verdict = derive_verdict(overall)

    return ScoreBreakdown(
        kigo=kigo,
        kireji=kireji,
        bild=bild,
        gegenwart=gegenwart,
        natur=natur,
        verdichtung=verdichtung,
        weighted_points=weighted_points,
        raw_overall=raw_overall,
        overall=overall,
        verdict=verdict,
        hard_fail_triggered=hard_fail_triggered,
        hard_fail_reason=hard_fail_reason,
    )


def evaluate_strict_result(score_breakdown: ScoreBreakdown) -> bool:
    return score_breakdown.overall >= ScoreBreakdown.STRICT_PASS_THRESHOLD
