from __future__ import annotations

import pytest

import haiku_cli.ai.runner as runner_module
from haiku_cli.ai import AIResponseError, ProviderUnavailable
from haiku_cli.models import HaikuAnalysis, LineAnalysis


def _analysis() -> HaikuAnalysis:
    return HaikuAnalysis(
        lines=(
            LineAnalysis(text="a", words=(), total=5, expected=5, valid=True),
            LineAnalysis(text="b", words=(), total=7, expected=7, valid=True),
            LineAnalysis(text="c", words=(), total=5, expected=5, valid=True),
        ),
        valid_structure=True,
    )


def test_run_ai_check_auto_falls_back_to_lmstudio(monkeypatch) -> None:
    calls: list[str] = []

    def fake_ollama(user_content, *, strict, fix, model):
        calls.append("ollama")
        raise ProviderUnavailable("Ollama down")

    def fake_lmstudio(user_content, *, strict, fix, model):
        calls.append("lmstudio")
        return {"kigo": {"present": True}}

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

    assert result["kigo"]["present"] is True
    assert calls == ["ollama", "lmstudio"]


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


def test_run_ai_check_auto_falls_back_on_ollama_json_error(monkeypatch) -> None:
    calls: list[str] = []

    def fake_ollama(user_content, *, strict, fix, model):
        calls.append("ollama")
        raise AIResponseError("Ollama hat kein gültiges JSON geliefert.")

    def fake_lmstudio(user_content, *, strict, fix, model):
        calls.append("lmstudio")
        return {"kigo": {"present": True}}

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

    assert result["kigo"]["present"] is True
    assert calls == ["ollama", "lmstudio"]
