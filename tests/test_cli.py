from __future__ import annotations

from click.testing import CliRunner

import haiku_cli.cli as cli_module
from haiku_cli.cli import main

VALID_HAIKU = "\n".join(
    (
        "Kirschblüten fallen",
        "leiser Regen über Moos",
        "Frühling atmet still",
    )
)

INVALID_HAIKU = "\n".join(
    (
        "Kirschblüten fallen",
        "Wind über Gras",
        "Frühling atmet still",
    )
)


def test_cli_pipe_mode_valid() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["--quiet"], input=VALID_HAIKU)
    assert result.exit_code == 0


def test_cli_pipe_mode_invalid() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["--quiet"], input=INVALID_HAIKU)
    assert result.exit_code == 1


def test_cli_interactive_mode() -> None:
    runner = CliRunner()
    result = runner.invoke(
        main,
        input="Kirschblüten fallen\nleiser Regen über Moos\nFrühling atmet still\n",
    )
    assert result.exit_code == 0
    assert "Struktur: gültiges 5-7-5" in result.output


def test_cli_strict_graceful_fallback_without_ai() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["--strict"], input=VALID_HAIKU)
    assert result.exit_code == 0
    assert "Warnung" in result.output


def test_cli_help_uses_real_umlauts() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "Führt zusätzlich eine KI-Haikuprüfung aus." in result.output
    assert "Silbenaufschlüsselung" in result.output


def test_cli_uses_computed_score_and_filters_structure_contradictions(monkeypatch) -> None:
    runner = CliRunner()

    def fake_run_ai_check(lines, analysis, *, provider, strict, fix, model):
        assert analysis.valid_structure is True
        return {
            "kigo": {"present": True, "word": "Frühling", "season": "Frühling"},
            "kireji": {"present": True, "description": "Klarer Schnitt"},
            "present_tense": True,
            "nature_imagery": True,
            "juxtaposition": {"present": True, "description": "Blüte gegen Stille"},
            "mono_no_aware": {"present": False, "description": ""},
            "overall_score": 3,
            "suggestions": [
                "Nicht streng 5-7-5, bitte Silben prüfen.",
                "Die Gegenüberstellung könnte noch knapper formuliert werden.",
            ],
        }

    monkeypatch.setattr(cli_module, "run_ai_check", fake_run_ai_check)

    result = runner.invoke(main, ["--check"], input=VALID_HAIKU)
    assert result.exit_code == 0
    assert "Gesamtwertung: 10/10" in result.output
    assert "Nicht streng 5-7-5" not in result.output
    assert "Die Gegenüberstellung könnte noch knapper formuliert werden." in result.output


def test_cli_renders_failed_criteria_with_cross(monkeypatch) -> None:
    runner = CliRunner()

    def fake_run_ai_check(lines, analysis, *, provider, strict, fix, model):
        return {
            "kigo": {"present": False, "word": "", "season": ""},
            "kireji": {"present": False, "description": ""},
            "present_tense": False,
            "nature_imagery": True,
            "juxtaposition": {"present": False, "description": ""},
            "mono_no_aware": {"present": False, "description": ""},
            "suggestions": [],
        }

    monkeypatch.setattr(cli_module, "run_ai_check", fake_run_ai_check)

    result = runner.invoke(main, ["--check"], input=VALID_HAIKU)
    assert result.exit_code == 0
    assert "✗ Kigo: nicht erkannt" in result.output
    assert "✗ Kireji: nicht erkannt" in result.output
    assert "✓ Naturbild: ja" in result.output
