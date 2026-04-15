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
    assert "Behaupte nicht, die Form sei kein 5-7-5" in prompt
    assert "poetische Inversion" in prompt
    assert "strong | weak | absent" in prompt
    assert '"image_coherence"' in prompt
    assert '"show_not_tell"' in prompt
