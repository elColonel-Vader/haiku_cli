from __future__ import annotations

import pytest

from haiku_cli.syllables.german import analyze_line, analyze_word


@pytest.mark.parametrize(
    ("word", "expected"),
    [
        ("Kirschblüte", 3),
        ("Mondschein", 2),
        ("Seifenblase", 4),
        ("Meditation", 5),
        ("Station", 3),
        ("Frühling", 2),
        ("Vögel", 2),
        ("Herbstwind", 2),
        ("Donaudampfschiff", 5),
        ("Stille", 2),
        ("Reh", 1),
    ],
)
def test_german_word_counts(word: str, expected: int) -> None:
    assert analyze_word(word).syllables == expected


def test_manual_syllable_markers_win() -> None:
    analysis = analyze_word("Was·ser")
    assert analysis.syllables == 2
    assert analysis.method == "manual"


def test_decomposed_umlauts_are_recognized() -> None:
    assert analyze_word("u\u0308ber").syllables == 2
    assert analyze_word("Vo\u0308gel").syllables == 2


def test_maskiert_spoken_syllables_not_hyphenation_i_ert() -> None:
    assert analyze_word("maskiert").syllables == 2


def test_april_maskiert_sich_five_syllables() -> None:
    line = analyze_line("April maskiert sich")
    assert sum(w.syllables for w in line) == 5
