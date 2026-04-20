from __future__ import annotations

from types import SimpleNamespace

import pytest

import haiku_cli.syllables.compounds as compounds_module
from haiku_cli.syllables.german import analyze_line, analyze_word


@pytest.mark.parametrize(
    ("word", "expected"),
    [
        ("Kirschblüte", 3),
        ("Apfelblüte", 4),
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


def test_apfelbluete_weiss_is_five_syllables() -> None:
    line = analyze_line("Apfelblüte, weiß -")
    assert sum(w.syllables for w in line) == 5


def test_split_compound_prefers_known_compounds() -> None:
    assert compounds_module.split_compound("Apfelblüte") == ("apfel", "blüte")


def test_split_compound_uses_charsplit_fst_when_available(monkeypatch) -> None:
    class FakeSplitter:
        def split_compound(self, word: str):
            assert word == "wolkenschicht"
            return [(0.9, "wolken", "schicht")]

    compounds_module._charsplit_fst_splitter.cache_clear()
    compounds_module.split_compound.cache_clear()
    monkeypatch.setattr(compounds_module, "CharSplitFstSplitter", FakeSplitter)
    monkeypatch.setattr(compounds_module, "legacy_char_split", None)

    assert compounds_module.split_compound("Wolkenschicht") == ("wolken", "schicht")

    compounds_module._charsplit_fst_splitter.cache_clear()
    compounds_module.split_compound.cache_clear()


def test_split_compound_falls_back_to_legacy_splitter(monkeypatch) -> None:
    compounds_module._charsplit_fst_splitter.cache_clear()
    compounds_module.split_compound.cache_clear()
    monkeypatch.setattr(compounds_module, "CharSplitFstSplitter", None)
    monkeypatch.setattr(
        compounds_module,
        "legacy_char_split",
        SimpleNamespace(split_compound=lambda word: [(0.7, "löwen", "zahn")]),
    )

    assert compounds_module.split_compound("Löwenzahn") == ("löwen", "zahn")

    compounds_module._charsplit_fst_splitter.cache_clear()
    compounds_module.split_compound.cache_clear()


def test_split_compound_rejects_invalid_reconstruction(monkeypatch) -> None:
    class FakeSplitter:
        def split_compound(self, word: str):
            return [(0.9, "wolke", "nschicht")]

    compounds_module._charsplit_fst_splitter.cache_clear()
    compounds_module.split_compound.cache_clear()
    monkeypatch.setattr(compounds_module, "CharSplitFstSplitter", FakeSplitter)
    monkeypatch.setattr(compounds_module, "legacy_char_split", None)

    assert compounds_module.split_compound("Wolkenschicht") is None

    compounds_module._charsplit_fst_splitter.cache_clear()
    compounds_module.split_compound.cache_clear()
