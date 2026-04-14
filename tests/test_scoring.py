from __future__ import annotations

from haiku_cli.models import HaikuAnalysis, LineAnalysis
from haiku_cli.scoring import compute_score


def _analysis(valid_structure: bool) -> HaikuAnalysis:
    return HaikuAnalysis(
        lines=(
            LineAnalysis(text="a", words=(), total=5, expected=5, valid=True),
            LineAnalysis(text="b", words=(), total=7, expected=7, valid=True),
            LineAnalysis(text="c", words=(), total=5, expected=5, valid=True),
        ),
        valid_structure=valid_structure,
    )


def _full_result() -> dict:
    return {
        "kigo": {"present": True},
        "kireji": {"present": True},
        "nature_imagery": True,
        "present_tense": True,
        "juxtaposition": {"present": True},
    }


def test_compute_score_full_marks() -> None:
    b = compute_score(_analysis(True), _full_result())
    assert b.form == 2
    assert b.quality == 8
    assert b.raw_total == 10
    assert b.overall == 10


def test_compute_score_caps_overall_when_perfect_but_hints_remain() -> None:
    b = compute_score(_analysis(True), _full_result(), suggestions=["Noch etwas"])
    assert b.raw_total == 10
    assert b.overall == 9


def test_compute_score_zero_when_nothing_matches() -> None:
    result = {
        "kigo": {"present": False},
        "kireji": {"present": False},
        "nature_imagery": False,
        "present_tense": False,
        "juxtaposition": {"present": False},
    }
    b = compute_score(_analysis(False), result)
    assert b.form == 0
    assert b.quality == 0
    assert b.overall == 0


def test_compute_score_partial() -> None:
    result = {
        "kigo": {"present": True},
        "kireji": {"present": False},
        "nature_imagery": True,
        "present_tense": False,
        "juxtaposition": {"present": True},
    }
    b = compute_score(_analysis(True), result)
    assert b.form == 2
    assert b.quality == 6
    assert b.raw_total == 8
    assert b.overall == 8
