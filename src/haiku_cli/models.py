from __future__ import annotations

from dataclasses import dataclass, field

EXPECTED_SYLLABLES = (5, 7, 5)


@dataclass(frozen=True)
class WordAnalysis:
    original: str
    normalized: str
    syllables: int
    display: str
    method: str
    parts: tuple[str, ...] = ()


@dataclass(frozen=True)
class LineAnalysis:
    text: str
    words: tuple[WordAnalysis, ...]
    total: int
    expected: int
    valid: bool


@dataclass(frozen=True)
class HaikuAnalysis:
    lines: tuple[LineAnalysis, ...]
    valid_structure: bool


@dataclass
class RunResult:
    analysis: HaikuAnalysis
    ai_result: dict | None = None
    warnings: list[str] = field(default_factory=list)
