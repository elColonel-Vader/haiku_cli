from __future__ import annotations

from click.testing import CliRunner

import haiku_cli.cli as cli_module
from haiku_cli.ai import ProviderUnavailable
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


def test_cli_strict_graceful_fallback_without_ai(monkeypatch) -> None:
    def fake_run_ai_check(*args, **kwargs):
        raise ProviderUnavailable("Kein KI-Backend (Teststub).")

    monkeypatch.setattr(cli_module, "run_ai_check", fake_run_ai_check)

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
    assert "[default:" in result.output and "auto]" in result.output
    assert "lmstudio" in result.output


def test_cli_uses_computed_score_and_filters_structure_contradictions(monkeypatch) -> None:
    runner = CliRunner()

    def fake_run_ai_check(lines, analysis, *, provider, strict, fix, model):
        assert analysis.valid_structure is True
        return {
            "kigo": {"level": "strong", "explanation": "April verankert die Szene klar im Frühling."},
            "kireji": {"level": "strong", "explanation": "Der Gedankenstrich setzt einen deutlichen Schnitt."},
            "present_tense": {"level": "strong", "explanation": "Das Gedicht bleibt im erlebten Jetzt."},
            "nature_imagery": {"level": "strong", "explanation": "Blüte und Stille sind konkrete Naturbilder."},
            "juxtaposition": {
                "level": "strong",
                "explanation": "Blüte und Stille stehen in produktiver Spannung.",
            },
            "image_coherence": {
                "level": "coherent",
                "explanation": "Alle Bilder gehören zu einem ruhigen Frühlingsfeld.",
            },
            "show_not_tell": {
                "level": "showing",
                "explanation": "Die Stimmung entsteht aus den Bildern statt aus benannten Gefühlen.",
            },
            "mono_no_aware": {"level": "absent", "explanation": ""},
            "overall_score": 3,
            "suggestions": [
                "Nicht streng 5-7-5, bitte Silben prüfen.",
                "Die Gegenüberstellung könnte noch knapper formuliert werden.",
            ],
        }

    monkeypatch.setattr(cli_module, "run_ai_check", fake_run_ai_check)

    result = runner.invoke(main, ["--check"], input=VALID_HAIKU)
    assert result.exit_code == 0
    assert "Form: 2/2" in result.output
    assert "Haiku-Qualität: 12/12" in result.output
    assert "Gesamtwertung: 9/10" in result.output
    assert "Hinweis-Deckel: 10/10 wurde wegen offener Hinweise auf 9/10 reduziert." in result.output
    assert "Nicht streng 5-7-5" not in result.output
    assert "Die Gegenüberstellung könnte noch knapper formuliert werden." in result.output


def test_cli_renders_failed_criteria_with_cross(monkeypatch) -> None:
    runner = CliRunner()

    def fake_run_ai_check(lines, analysis, *, provider, strict, fix, model):
        return {
            "kigo": {"level": "absent", "explanation": "Kein Saisonbezug."},
            "kireji": {"level": "weak", "explanation": "Eine Pause ist da, aber ohne starken Schnitt."},
            "present_tense": {"level": "absent", "explanation": "Der Zeitbezug bleibt unklar."},
            "nature_imagery": {"level": "strong", "explanation": "Das Naturbild ist konkret."},
            "juxtaposition": {"level": "absent", "explanation": "Kein Kontrast."},
            "image_coherence": {"level": "fragmented", "explanation": "Die Bilder springen stark."},
            "show_not_tell": {"level": "mixed", "explanation": "Ein Teil bleibt erklärend."},
            "mono_no_aware": {"level": "absent", "explanation": ""},
            "suggestions": [],
        }

    monkeypatch.setattr(cli_module, "run_ai_check", fake_run_ai_check)

    result = runner.invoke(main, ["--check"], input=VALID_HAIKU)
    assert result.exit_code == 0
    assert "Kigo: absent" in result.output
    assert "Kireji: weak" in result.output
    assert "Naturbild: strong" in result.output


def test_cli_uses_auto_provider_by_default(monkeypatch) -> None:
    runner = CliRunner()

    def fake_run_ai_check(lines, analysis, *, provider, strict, fix, model):
        assert provider == "auto"
        return {
            "kigo": {"level": "absent", "explanation": ""},
            "kireji": {"level": "absent", "explanation": ""},
            "present_tense": {"level": "absent", "explanation": ""},
            "nature_imagery": {"level": "absent", "explanation": ""},
            "juxtaposition": {"level": "absent", "explanation": ""},
            "image_coherence": {"level": "fragmented", "explanation": ""},
            "show_not_tell": {"level": "telling", "explanation": ""},
            "mono_no_aware": {"level": "absent", "explanation": ""},
            "suggestions": [],
        }

    monkeypatch.setattr(cli_module, "run_ai_check", fake_run_ai_check)

    result = runner.invoke(main, ["--check"], input=VALID_HAIKU)
    assert result.exit_code == 0


def test_cli_accepts_explicit_lmstudio_provider(monkeypatch) -> None:
    runner = CliRunner()

    def fake_run_ai_check(lines, analysis, *, provider, strict, fix, model):
        assert provider == "lmstudio"
        return {
            "kigo": {"level": "absent", "explanation": ""},
            "kireji": {"level": "absent", "explanation": ""},
            "present_tense": {"level": "absent", "explanation": ""},
            "nature_imagery": {"level": "absent", "explanation": ""},
            "juxtaposition": {"level": "absent", "explanation": ""},
            "image_coherence": {"level": "fragmented", "explanation": ""},
            "show_not_tell": {"level": "telling", "explanation": ""},
            "mono_no_aware": {"level": "absent", "explanation": ""},
            "suggestions": [],
        }

    monkeypatch.setattr(cli_module, "run_ai_check", fake_run_ai_check)

    result = runner.invoke(main, ["--check", "--provider", "lmstudio"], input=VALID_HAIKU)
    assert result.exit_code == 0
