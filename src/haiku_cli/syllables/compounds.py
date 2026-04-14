from __future__ import annotations

from functools import lru_cache

KNOWN_COMPOUNDS: dict[str, tuple[str, ...]] = {
    "donaudampfschiff": ("donau", "dampf", "schiff"),
    "herbstwind": ("herbst", "wind"),
    "kirschblüte": ("kirsch", "blüte"),
    "mondschein": ("mond", "schein"),
    "seifenblase": ("seifen", "blase"),
}

try:
    from compound_split import char_split
except ImportError:  # pragma: no cover - optional dependency
    char_split = None


@lru_cache(maxsize=512)
def split_compound(word: str) -> tuple[str, ...] | None:
    normalized = word.casefold()
    if normalized in KNOWN_COMPOUNDS:
        return KNOWN_COMPOUNDS[normalized]

    if char_split is None or len(normalized) < 8:
        return None

    try:  # pragma: no cover - depends on optional third-party package
        candidates = char_split.split_compound(normalized)
    except Exception:
        return None

    if not candidates:
        return None

    best = candidates[0]
    if not isinstance(best, (list, tuple)) or len(best) < 3:
        return None

    parts = tuple(str(part) for part in best[1:] if str(part))
    if len(parts) <= 1 or "".join(parts).casefold() != normalized:
        return None
    return parts
