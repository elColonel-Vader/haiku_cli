from __future__ import annotations

from haiku_cli.ai.prompts import build_user_prompt
from haiku_cli.validate import validate_haiku


def test_build_user_prompt_includes_program_syllable_context() -> None:
    lines = (
        "Kirschblüten fallen",
        "leiser Regen über Moos",
        "Frühling atmet still",
    )
    analysis = validate_haiku(lines)
    prompt = build_user_prompt(lines, analysis)

    assert "Verbindliche Silbenanalyse des Programms" in prompt
    assert "Struktur insgesamt: gültig" in prompt
    assert "Haiku CLI v2 Strict" in prompt
    assert "Hard-Fail-Bedingungen" in prompt
    assert '"hard_fail"' in prompt
    assert '"verdict"' in prompt
    assert "Schritt für Schritt" not in prompt
    assert "knappe Gesamtbegründung" in prompt
    assert "strong | weak | absent" not in prompt
    assert '"image_coherence"' not in prompt
