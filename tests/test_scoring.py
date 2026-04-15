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
        "kigo": {"level": "strong"},
        "kireji": {"level": "strong"},
        "nature_imagery": {"level": "strong"},
        "present_tense": {"level": "strong"},
        "juxtaposition": {"level": "strong"},
        "image_coherence": {"level": "coherent"},
        "show_not_tell": {"level": "showing"},
        "mono_no_aware": {"level": "absent"},
    }


def test_compute_score_full_marks() -> None:
    b = compute_score(_analysis(True), _full_result())
    assert b.form == 2
    assert b.quality == 12
    assert b.raw_total == 14
    assert b.normalized == 10
    assert b.pre_cap_overall == 10
    assert b.suggestions_cap_applied is False
    assert b.overall == 10


def test_compute_score_caps_overall_when_perfect_but_hints_remain() -> None:
    b = compute_score(_analysis(True), _full_result(), suggestions=["Noch etwas"])
    assert b.normalized == 10
    assert b.pre_cap_overall == 10
    assert b.suggestions_cap_applied is True
    assert b.overall == 9


def test_compute_score_zero_when_nothing_matches() -> None:
    result = {
        "kigo": {"level": "absent"},
        "kireji": {"level": "absent"},
        "nature_imagery": {"level": "absent"},
        "present_tense": {"level": "absent"},
        "juxtaposition": {"level": "absent"},
        "image_coherence": {"level": "fragmented"},
        "show_not_tell": {"level": "telling"},
        "mono_no_aware": {"level": "absent"},
    }
    b = compute_score(_analysis(False), result)
    assert b.form == 0
    assert b.quality == 0
    assert b.normalized == 0
    assert b.pre_cap_overall == 0
    assert b.suggestions_cap_applied is False
    assert b.overall == 0


def test_compute_score_partial() -> None:
    result = {
        "kigo": {"level": "strong"},
        "kireji": {"level": "weak"},
        "nature_imagery": {"level": "weak"},
        "present_tense": {"level": "absent"},
        "juxtaposition": {"level": "strong"},
        "image_coherence": {"level": "loosely_connected"},
        "show_not_tell": {"level": "mixed"},
        "mono_no_aware": {"level": "present"},
    }
    b = compute_score(_analysis(True), result)
    assert b.form == 2
    assert b.quality == 7.5
    assert b.raw_total == 9.5
    assert b.normalized == 7
    assert b.mono_no_aware_bonus == 1
    assert b.pre_cap_overall == 8
    assert b.suggestions_cap_applied is False
    assert b.overall == 8


def test_compute_score_supports_legacy_boolean_results() -> None:
    result = {
        "kigo": {"present": True},
        "kireji": {"present": False},
        "nature_imagery": True,
        "present_tense": False,
        "juxtaposition": {"present": True},
        "mono_no_aware": {"present": False},
    }
    b = compute_score(_analysis(True), result)
    assert b.form == 2
    assert b.quality == 6
    assert b.normalized == 6
    assert b.pre_cap_overall == 6
    assert b.suggestions_cap_applied is False
    assert b.overall == 6
