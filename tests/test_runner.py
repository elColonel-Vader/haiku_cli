from __future__ import annotations

import pytest

import haiku_cli.ai.runner as runner_module
from haiku_cli.ai import AIResponseError, ProviderUnavailable
from haiku_cli.models import HaikuAnalysis, LineAnalysis
from haiku_cli.scoring import compute_score


def _analysis() -> HaikuAnalysis:
    return HaikuAnalysis(
        lines=(
            LineAnalysis(text="a", words=(), total=5, expected=5, valid=True),
            LineAnalysis(text="b", words=(), total=7, expected=7, valid=True),
            LineAnalysis(text="c", words=(), total=5, expected=5, valid=True),
        ),
        valid_structure=True,
    )


def _result(score: int = 1) -> dict:
    return {
        "kigo": {"score": score},
        "kireji": {"score": score},
        "bild": {"score": score},
        "gegenwart": {"score": min(score, 2)},
        "natur": {"score": min(score, 2)},
        "verdichtung": {"score": min(score, 2)},
        "hard_fail": {"triggered": False, "reason": None},
    }


def test_run_ai_check_auto_uses_lmstudio_when_available(monkeypatch) -> None:
    calls: list[str] = []

    def fake_ollama(user_content, *, strict, fix, model):
        calls.append("ollama")
        return _result(0)

    def fake_lmstudio(user_content, *, strict, fix, model):
        calls.append("lmstudio")
        return _result(2)

    monkeypatch.setattr(runner_module, "run_ollama_check", fake_ollama)
    monkeypatch.setattr(runner_module, "run_lmstudio_check", fake_lmstudio)

    result = runner_module.run_ai_check(
        ("eins", "zwei", "drei"),
        _analysis(),
        provider="auto",
        strict=False,
        fix=False,
        model=None,
    )

    assert result["kigo"]["score"] == 2
    assert calls == ["lmstudio"]


def test_run_ai_check_auto_falls_back_to_ollama(monkeypatch) -> None:
    calls: list[str] = []

    def fake_ollama(user_content, *, strict, fix, model):
        calls.append("ollama")
        return _result(1)

    def fake_lmstudio(user_content, *, strict, fix, model):
        calls.append("lmstudio")
        raise ProviderUnavailable("LM Studio down")

    monkeypatch.setattr(runner_module, "run_ollama_check", fake_ollama)
    monkeypatch.setattr(runner_module, "run_lmstudio_check", fake_lmstudio)

    result = runner_module.run_ai_check(
        ("eins", "zwei", "drei"),
        _analysis(),
        provider="auto",
        strict=False,
        fix=False,
        model=None,
    )

    assert result["kigo"]["score"] == 1
    assert calls == ["lmstudio", "ollama"]


def test_evaluate_strict_result_accepts_scores_from_threshold() -> None:
    score_breakdown = compute_score(_result(2))
    assert runner_module.evaluate_strict_result(score_breakdown) is True


def test_evaluate_strict_result_rejects_scores_below_threshold() -> None:
    score_breakdown = compute_score(_result(1))
    assert runner_module.evaluate_strict_result(score_breakdown) is False


def test_run_ai_check_auto_reports_both_local_failures(monkeypatch) -> None:
    def fake_ollama(user_content, *, strict, fix, model):
        raise ProviderUnavailable("Ollama down")

    def fake_lmstudio(user_content, *, strict, fix, model):
        raise ProviderUnavailable("LM Studio down")

    monkeypatch.setattr(runner_module, "run_ollama_check", fake_ollama)
    monkeypatch.setattr(runner_module, "run_lmstudio_check", fake_lmstudio)

    with pytest.raises(ProviderUnavailable) as exc:
        runner_module.run_ai_check(
            ("eins", "zwei", "drei"),
            _analysis(),
            provider="auto",
            strict=False,
            fix=False,
            model=None,
        )

    assert "Ollama" in str(exc.value)
    assert "LM Studio" in str(exc.value)


def test_run_ai_check_auto_falls_back_on_lmstudio_json_error(monkeypatch) -> None:
    calls: list[str] = []

    def fake_ollama(user_content, *, strict, fix, model):
        calls.append("ollama")
        return _result(1)

    def fake_lmstudio(user_content, *, strict, fix, model):
        calls.append("lmstudio")
        raise AIResponseError("LM Studio hat kein gültiges JSON geliefert.")

    monkeypatch.setattr(runner_module, "run_ollama_check", fake_ollama)
    monkeypatch.setattr(runner_module, "run_lmstudio_check", fake_lmstudio)

    result = runner_module.run_ai_check(
        ("eins", "zwei", "drei"),
        _analysis(),
        provider="auto",
        strict=True,
        fix=False,
        model=None,
    )

    assert result["kigo"]["score"] == 1
    assert calls == ["lmstudio", "ollama"]
