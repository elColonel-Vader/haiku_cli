from __future__ import annotations

import sys
from types import SimpleNamespace

from haiku_cli.ai.ollama import DEFAULT_OLLAMA_MODEL, run_ollama_check


def test_run_ollama_check_uses_gemma_default(monkeypatch) -> None:
    calls: list[dict] = []

    class FakeClient:
        def chat(self, **kwargs):
            calls.append(kwargs)
            assert kwargs["messages"]
            assert kwargs["options"] == {"temperature": 0.1}
            assert kwargs["format"] == "json"
            return {"message": {"content": "{}"}}

    monkeypatch.setitem(sys.modules, "ollama", SimpleNamespace(Client=FakeClient))

    result = run_ollama_check(
        "Promptinhalt",
        strict=False,
        fix=False,
    )

    assert result == {}
    assert calls[0]["model"] == DEFAULT_OLLAMA_MODEL
    assert calls[0]["messages"][1]["content"] == "Promptinhalt"
