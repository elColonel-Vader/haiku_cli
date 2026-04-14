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


def test_compute_score_full_marks() -> None:
    result = {
        "kigo": {"present": True},
        "kireji": {"present": True},
        "nature_imagery": True,
        "present_tense": True,
        "juxtaposition": {"present": True},
    }
    assert compute_score(_analysis(True), result) == 10


def test_compute_score_zero_when_nothing_matches() -> None:
    result = {
        "kigo": {"present": False},
        "kireji": {"present": False},
        "nature_imagery": False,
        "present_tense": False,
        "juxtaposition": {"present": False},
    }
    assert compute_score(_analysis(False), result) == 0


def test_compute_score_partial() -> None:
    result = {
        "kigo": {"present": True},
        "kireji": {"present": False},
        "nature_imagery": True,
        "present_tense": False,
        "juxtaposition": {"present": True},
    }
    assert compute_score(_analysis(True), result) == 8
