from __future__ import annotations

import pytest

from haiku_cli.parser import ParseError, parse_haiku


def test_parse_haiku_normalizes_whitespace() -> None:
    lines = parse_haiku("  Kirschblüten   fallen \n\n der Wind trägt sie \n Frühling wird still ")
    assert lines == (
        "Kirschblüten fallen",
        "der Wind trägt sie",
        "Frühling wird still",
    )


def test_parse_haiku_requires_exactly_three_lines() -> None:
    with pytest.raises(ParseError):
        parse_haiku("eine\nzwei")


def test_parse_haiku_normalizes_decomposed_umlauts() -> None:
    lines = parse_haiku("Ku\u0308hle Luft\nVo\u0308gel ziehen\nFru\u0308hling naht")
    assert lines == ("Kühle Luft", "Vögel ziehen", "Frühling naht")
