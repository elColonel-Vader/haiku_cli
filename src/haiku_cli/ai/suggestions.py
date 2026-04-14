from __future__ import annotations

import re

STRUCTURE_CONTRADICTION_RE = re.compile(
    r"("
    r"5\s*-\s*7\s*-\s*5"
    r"|silben?"
    r"|zeilen?\s*(?:sind|ist)\s*(?:nicht\s*)?(?:zu\s*)?(?:lang|kurz|falsch)"
    r"|nicht\s+streng"
    r"|strenge?\s+form"
    r"|metr"
    r")",
    re.IGNORECASE,
)


def sanitize_suggestions(suggestions: list[str], *, valid_structure: bool) -> list[str]:
    if not valid_structure:
        return suggestions

    return [item for item in suggestions if not STRUCTURE_CONTRADICTION_RE.search(item)]
