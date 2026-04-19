from __future__ import annotations

from haiku_cli.scoring import compute_score, derive_verdict


def _result(
    *,
    kigo: int,
    kireji: int,
    bild: int,
    gegenwart: int,
    natur: int,
    verdichtung: int,
    hard_fail: bool = False,
    hard_fail_reason: str | None = None,
) -> dict:
    return {
        "kigo": {"score": kigo},
        "kireji": {"score": kireji},
        "bild": {"score": bild},
        "gegenwart": {"score": gegenwart},
        "natur": {"score": natur},
        "verdichtung": {"score": verdichtung},
        "hard_fail": {"triggered": hard_fail, "reason": hard_fail_reason},
        "overall_score": 0.1,
        "verdict": "UNGENÜGEND",
    }


def test_compute_score_full_marks() -> None:
    b = compute_score(_result(kigo=3, kireji=3, bild=3, gegenwart=2, natur=2, verdichtung=2))
    assert b.weighted_points == 270
    assert b.raw_overall == 10.0
    assert b.overall == 10.0
    assert b.verdict == "MEISTERHAFT"


def test_compute_score_zero_when_nothing_matches() -> None:
    b = compute_score(_result(kigo=0, kireji=0, bild=0, gegenwart=0, natur=0, verdichtung=0))
    assert b.weighted_points == 0
    assert b.overall == 0.0
    assert b.verdict == "UNGENÜGEND"


def test_compute_score_partial_uses_weighted_formula() -> None:
    b = compute_score(_result(kigo=2, kireji=2, bild=2, gegenwart=2, natur=2, verdichtung=1))
    assert b.weighted_points == 190
    assert b.raw_overall == 7.0
    assert b.overall == 7.0
    assert b.verdict == "GUT"


def test_compute_score_caps_hard_fail_at_three() -> None:
    b = compute_score(
        _result(
            kigo=3,
            kireji=3,
            bild=3,
            gegenwart=2,
            natur=2,
            verdichtung=2,
            hard_fail=True,
            hard_fail_reason="Aphorismus statt Haiku",
        )
    )
    assert b.raw_overall == 10.0
    assert b.overall == 3.0
    assert b.verdict == "SCHWACH"
    assert b.hard_fail_triggered is True
    assert b.hard_fail_reason == "Aphorismus statt Haiku"


def test_compute_score_ignores_model_supplied_overall_and_verdict() -> None:
    result = _result(kigo=1, kireji=1, bild=1, gegenwart=1, natur=1, verdichtung=1)
    result["overall_score"] = 9.9
    result["verdict"] = "MEISTERHAFT"
    b = compute_score(result)
    assert b.overall == 3.7
    assert b.verdict == "SCHWACH"


def test_derive_verdict_thresholds() -> None:
    assert derive_verdict(8.0) == "MEISTERHAFT"
    assert derive_verdict(6.5) == "GUT"
    assert derive_verdict(4.5) == "ORDENTLICH"
    assert derive_verdict(2.5) == "SCHWACH"
    assert derive_verdict(2.4) == "UNGENÜGEND"
