from __future__ import annotations

from haiku_cli.models import EXPECTED_SYLLABLES, HaikuAnalysis, LineAnalysis
from haiku_cli.syllables.german import analyze_line


def validate_haiku(lines: tuple[str, str, str]) -> HaikuAnalysis:
    analyses: list[LineAnalysis] = []
    for expected, line in zip(EXPECTED_SYLLABLES, lines, strict=True):
        words = analyze_line(line)
        total = sum(word.syllables for word in words)
        analyses.append(
            LineAnalysis(
                text=line,
                words=words,
                total=total,
                expected=expected,
                valid=total == expected,
            )
        )

    return HaikuAnalysis(
        lines=tuple(analyses),
        valid_structure=all(line.valid for line in analyses),
    )
