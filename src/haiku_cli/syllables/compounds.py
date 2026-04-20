from __future__ import annotations

import re
from functools import lru_cache

VALID_PART_RE = re.compile(r"^[a-zäöüß]+$")
IMPLAUSIBLE_PART_PREFIXES = ("ns", "ts")

KNOWN_COMPOUNDS: dict[str, tuple[str, ...]] = {
    "apfelblüte": ("apfel", "blüte"),
    "donaudampfschiff": ("donau", "dampf", "schiff"),
    "herbstwind": ("herbst", "wind"),
    "kirschblüte": ("kirsch", "blüte"),
    "mondschein": ("mond", "schein"),
    "seifenblase": ("seifen", "blase"),
}

try:
    from charsplit_fst import Splitter as CharSplitFstSplitter
except ImportError:  # pragma: no cover - optional dependency
    CharSplitFstSplitter = None

try:
    from compound_split import char_split as legacy_char_split
except ImportError:  # pragma: no cover - optional dependency
    legacy_char_split = None


@lru_cache(maxsize=1)
def _charsplit_fst_splitter() -> object | None:
    if CharSplitFstSplitter is None:
        return None

    try:  # pragma: no cover - depends on optional third-party package
        return CharSplitFstSplitter()
    except Exception:
        return None


def _normalize_parts(parts: tuple[str, ...], *, normalized: str) -> tuple[str, ...] | None:
    cleaned = tuple(str(part).casefold() for part in parts if str(part).strip())
    if len(cleaned) <= 1:
        return None
    if "".join(cleaned) != normalized:
        return None
    if any(not VALID_PART_RE.fullmatch(part) for part in cleaned):
        return None
    if any(len(part) < 2 for part in cleaned):
        return None
    if any(not re.search(r"[aeiouyäöü]", part) for part in cleaned):
        return None
    if any(part.startswith(IMPLAUSIBLE_PART_PREFIXES) for part in cleaned[1:]):
        return None
    return cleaned


def _split_with_charsplit_fst(normalized: str) -> tuple[str, ...] | None:
    splitter = _charsplit_fst_splitter()
    if splitter is None or len(normalized) < 8:
        return None

    try:  # pragma: no cover - depends on optional third-party package
        candidates = splitter.split_compound(normalized)
    except Exception:
        return None

    if not candidates:
        return None

    best = candidates[0]
    if not isinstance(best, (list, tuple)) or len(best) < 3:
        return None

    return _normalize_parts(tuple(best[1:]), normalized=normalized)


def _split_with_legacy_compound_split(normalized: str) -> tuple[str, ...] | None:
    if legacy_char_split is None or len(normalized) < 8:
        return None

    try:  # pragma: no cover - depends on optional third-party package
        candidates = legacy_char_split.split_compound(normalized)
    except Exception:
        return None

    if not candidates:
        return None

    best = candidates[0]
    if not isinstance(best, (list, tuple)) or len(best) < 3:
        return None

    return _normalize_parts(tuple(best[1:]), normalized=normalized)


@lru_cache(maxsize=512)
def split_compound(word: str) -> tuple[str, ...] | None:
    normalized = word.casefold()
    if normalized in KNOWN_COMPOUNDS:
        return KNOWN_COMPOUNDS[normalized]

    fst_parts = _split_with_charsplit_fst(normalized)
    if fst_parts is not None:
        return fst_parts

    return _split_with_legacy_compound_split(normalized)
