from __future__ import annotations

from haiku_cli.ai.suggestions import sanitize_suggestions


def test_sanitize_suggestions_filters_structure_contradictions() -> None:
    suggestions = [
        "Nicht streng 5-7-5, bitte Silben prüfen.",
        "Die Naturbilder könnten konkreter werden.",
        "Eine stärkere Gegenüberstellung würde helfen.",
    ]

    assert sanitize_suggestions(suggestions, valid_structure=True) == [
        "Die Naturbilder könnten konkreter werden.",
        "Eine stärkere Gegenüberstellung würde helfen.",
    ]


def test_sanitize_suggestions_keeps_structure_feedback_when_invalid() -> None:
    suggestions = ["Nicht streng 5-7-5, bitte Silben prüfen."]
    assert sanitize_suggestions(suggestions, valid_structure=False) == suggestions
