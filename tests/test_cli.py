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


def _result(
    *,
    kigo: int,
    kireji: int,
    bild: int,
    gegenwart: int,
    natur: int,
    verdichtung: int,
    suggestions: list[str] | None = None,
    hard_fail: bool = False,
    hard_fail_reason: str | None = None,
    overall_score: float = 0.0,
    verdict: str = "UNGENÜGEND",
) -> dict:
    return {
        "reasoning": "Kategorie für Kategorie geprüft.",
        "kigo": {
            "score": kigo,
            "word": "Kirschblüten",
            "season": "Frühling",
            "note": "Klares Kigo.",
        },
        "kireji": {"score": kireji, "cut_point": "nach Zeile 1", "note": "Saubere Zäsur."},
        "bild": {
            "score": bild,
            "concrete_images": ["Kirschblüten", "Regen", "Moos"],
            "abstract_words": [],
            "note": "Konkrete Bilder tragen das Haiku.",
        },
        "gegenwart": {"score": gegenwart, "tense_issues": [], "note": "Im Augenblick gehalten."},
        "natur": {
            "score": natur,
            "elements": ["Kirschblüten", "Regen", "Moos"],
            "note": "Starker Naturbezug.",
        },
        "verdichtung": {"score": verdichtung, "filler_words": [], "note": "Knapper Ausdruck."},
        "hard_fail": {"triggered": hard_fail, "reason": hard_fail_reason},
        "overall_score": overall_score,
        "verdict": verdict,
        "suggestions": suggestions or [],
    }


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


def test_cli_strict_fails_without_ai(monkeypatch) -> None:
    def fake_run_ai_check(*args, **kwargs):
        raise ProviderUnavailable("Kein KI-Backend (Teststub).")

    monkeypatch.setattr(cli_module, "run_ai_check", fake_run_ai_check)

    runner = CliRunner()
    result = runner.invoke(main, ["--strict"], input=VALID_HAIKU)
    assert result.exit_code == 1
    assert "Warnung" in result.output


def test_cli_help_mentions_quiet_summary_mode() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "Führt zusätzlich eine KI-Haikuprüfung aus." in result.output
    assert "Verdict + Score." in result.output
    assert "[default: lmstudio]" in result.output
    assert "lmstudio" in result.output


def test_cli_uses_computed_score_and_filters_structure_contradictions(monkeypatch) -> None:
    runner = CliRunner()

    def fake_run_ai_check(lines, analysis, *, provider, strict, fix, model):
        assert analysis.valid_structure is True
        return _result(
            kigo=3,
            kireji=3,
            bild=3,
            gegenwart=2,
            natur=2,
            verdichtung=2,
            overall_score=3.0,
            verdict="SCHWACH",
            suggestions=[
                "Nicht streng 5-7-5, bitte Silben prüfen.",
                "Die Naturbilder könnten noch überraschender werden.",
            ],
        )

    monkeypatch.setattr(cli_module, "run_ai_check", fake_run_ai_check)

    result = runner.invoke(main, ["--check"], input=VALID_HAIKU)
    assert result.exit_code == 0
    assert "Verdict:" in result.output
    assert "MEISTERHAFT" in result.output
    assert "10.0/10" in result.output
    assert "Nicht streng 5-7-5" not in result.output
    assert "Die Naturbilder könnten noch überraschender werden." in result.output


def test_cli_renders_numeric_category_scores_and_hard_fail(monkeypatch) -> None:
    runner = CliRunner()

    def fake_run_ai_check(lines, analysis, *, provider, strict, fix, model):
        return _result(
            kigo=0,
            kireji=1,
            bild=0,
            gegenwart=0,
            natur=1,
            verdichtung=0,
            hard_fail=True,
            hard_fail_reason="Aphorismus statt Haiku",
        )

    monkeypatch.setattr(cli_module, "run_ai_check", fake_run_ai_check)

    result = runner.invoke(main, ["--check"], input=VALID_HAIKU)
    assert result.exit_code == 0
    assert "Kigo: 0/3" in result.output
    assert "Kireji: 1/3" in result.output
    assert "Naturbezug: 1/2" in result.output
    assert "Hard Fail:" in result.output
    assert "Aphorismus statt Haiku" in result.output


def test_cli_uses_lmstudio_provider_by_default(monkeypatch) -> None:
    runner = CliRunner()

    def fake_run_ai_check(lines, analysis, *, provider, strict, fix, model):
        assert provider == "lmstudio"
        return _result(kigo=0, kireji=0, bild=0, gegenwart=0, natur=0, verdichtung=0)

    monkeypatch.setattr(cli_module, "run_ai_check", fake_run_ai_check)

    result = runner.invoke(main, ["--check"], input=VALID_HAIKU)
    assert result.exit_code == 0


def test_cli_accepts_explicit_auto_provider(monkeypatch) -> None:
    runner = CliRunner()

    def fake_run_ai_check(lines, analysis, *, provider, strict, fix, model):
        assert provider == "auto"
        return _result(kigo=0, kireji=0, bild=0, gegenwart=0, natur=0, verdichtung=0)

    monkeypatch.setattr(cli_module, "run_ai_check", fake_run_ai_check)

    result = runner.invoke(main, ["--check", "--provider", "auto"], input=VALID_HAIKU)
    assert result.exit_code == 0


def test_cli_accepts_explicit_lmstudio_provider(monkeypatch) -> None:
    runner = CliRunner()

    def fake_run_ai_check(lines, analysis, *, provider, strict, fix, model):
        assert provider == "lmstudio"
        return _result(kigo=0, kireji=0, bild=0, gegenwart=0, natur=0, verdichtung=0)

    monkeypatch.setattr(cli_module, "run_ai_check", fake_run_ai_check)

    result = runner.invoke(main, ["--check", "--provider", "lmstudio"], input=VALID_HAIKU)
    assert result.exit_code == 0


def test_cli_check_quiet_outputs_only_verdict_and_score(monkeypatch) -> None:
    runner = CliRunner()

    def fake_run_ai_check(lines, analysis, *, provider, strict, fix, model):
        return _result(kigo=2, kireji=2, bild=2, gegenwart=2, natur=2, verdichtung=1)

    monkeypatch.setattr(cli_module, "run_ai_check", fake_run_ai_check)

    result = runner.invoke(main, ["--check", "--quiet"], input=VALID_HAIKU)
    assert result.exit_code == 0
    assert "GUT 7.0/10" in result.output
    assert "Struktur:" not in result.output
    assert "Reasoning:" not in result.output


def test_cli_strict_rejects_scores_below_threshold(monkeypatch) -> None:
    runner = CliRunner()

    def fake_run_ai_check(lines, analysis, *, provider, strict, fix, model):
        return _result(kigo=1, kireji=1, bild=1, gegenwart=1, natur=1, verdichtung=1)

    monkeypatch.setattr(cli_module, "run_ai_check", fake_run_ai_check)

    result = runner.invoke(main, ["--strict", "--quiet"], input=VALID_HAIKU)
    assert result.exit_code == 1
    assert "SCHWACH 3.7/10" in result.output


def test_cli_strict_accepts_scores_at_threshold(monkeypatch) -> None:
    runner = CliRunner()

    def fake_run_ai_check(lines, analysis, *, provider, strict, fix, model):
        return _result(kigo=2, kireji=2, bild=2, gegenwart=2, natur=2, verdichtung=1)

    monkeypatch.setattr(cli_module, "run_ai_check", fake_run_ai_check)

    result = runner.invoke(main, ["--strict", "--quiet"], input=VALID_HAIKU)
    assert result.exit_code == 0
    assert "GUT 7.0/10" in result.output
