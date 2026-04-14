from __future__ import annotations

from click.testing import CliRunner

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
