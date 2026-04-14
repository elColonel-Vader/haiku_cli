from __future__ import annotations

import re
import unicodedata
from functools import lru_cache

import pyphen

from haiku_cli.models import WordAnalysis

from .compounds import split_compound

TOKEN_RE = re.compile(r"[A-Za-zÄÖÜäöüß]+(?:[·-][A-Za-zÄÖÜäöüß]+)*")
MARKER_RE = re.compile(r"[·-]")
VOWELS = set("aeiouyäöü")
DIPHTHONGS = {"aa", "au", "äu", "ee", "ei", "eu", "ie", "oo"}
KNOWN_COUNTS: dict[str, int] = {
    "donaudampfschiff": 5,
    "frühling": 2,
    "herbstwind": 2,
    "kirschblüte": 3,
    "meditation": 5,
    "mondschein": 2,
    "reh": 1,
    "seifenblase": 4,
    "stille": 2,
    "station": 3,
    "vögel": 2,
}
HYPHENATOR = pyphen.Pyphen(lang="de_DE")


def _to_nfc(text: str) -> str:
    return unicodedata.normalize("NFC", text)


def tokenize(line: str) -> list[str]:
    normalized = _to_nfc(line)
    return [match.group(0) for match in TOKEN_RE.finditer(normalized)]


def _normalize(word: str) -> str:
    return _to_nfc(word).casefold()


def _manual_breakdown(word: str) -> WordAnalysis | None:
    normalized_word = _to_nfc(word)
    if not MARKER_RE.search(normalized_word):
        return None

    parts = tuple(part for part in MARKER_RE.split(normalized_word) if part)
    if len(parts) <= 1:
        return None

    return WordAnalysis(
        original=normalized_word,
        normalized=_normalize(normalized_word),
        syllables=len(parts),
        display="-".join(parts),
        method="manual",
        parts=parts,
    )


@lru_cache(maxsize=1024)
def _hyphenate(word: str) -> str:
    return HYPHENATOR.inserted(_to_nfc(word), hyphen="-")


def _count_pyphen(word: str) -> tuple[int, str]:
    inserted = _hyphenate(word)
    count = len([part for part in inserted.split("-") if part])
    return count, inserted


def _count_heuristic(word: str) -> int:
    lowered = _normalize(word)
    count = 0
    index = 0
    while index < len(lowered):
        char = lowered[index]
        if char not in VOWELS:
            index += 1
            continue

        count += 1
        if lowered[index : index + 2] in DIPHTHONGS:
            index += 2
            continue

        index += 1
        while index < len(lowered) and lowered[index] in VOWELS:
            if lowered[index - 1 : index + 1] not in DIPHTHONGS:
                count += 1
            index += 1

    if lowered.endswith("tion"):
        count += 1

    return max(count, 1)


def analyze_word(word: str, *, allow_compounds: bool = True) -> WordAnalysis:
    word = _to_nfc(word)
    manual = _manual_breakdown(word)
    if manual is not None:
        return manual

    normalized = _normalize(word)
    if normalized in KNOWN_COUNTS:
        count, display = _count_pyphen(word)
        return WordAnalysis(
            original=word,
            normalized=normalized,
            syllables=KNOWN_COUNTS[normalized],
            display=display,
            method="known",
        )

    if allow_compounds:
        parts = split_compound(word)
        if parts and len(parts) > 1:
            analyses = tuple(analyze_word(part, allow_compounds=False) for part in parts)
            total = sum(part.syllables for part in analyses)
            if total > 0:
                return WordAnalysis(
                    original=word,
                    normalized=normalized,
                    syllables=total,
                    display="|".join(parts),
                    method="compound",
                    parts=parts,
                )

    pyphen_count, display = _count_pyphen(word)
    heuristic_count = _count_heuristic(word)
    syllables = max(pyphen_count, heuristic_count)
    if normalized.endswith("tion"):
        syllables = max(syllables, heuristic_count)

    method = "pyphen" if pyphen_count > 0 else "heuristic"
    return WordAnalysis(
        original=word,
        normalized=normalized,
        syllables=syllables,
        display=display or word,
        method=method,
    )


def analyze_line(line: str) -> tuple[WordAnalysis, ...]:
    words = [analyze_word(word) for word in tokenize(line)]
    return tuple(words)
