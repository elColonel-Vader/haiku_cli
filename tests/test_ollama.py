from __future__ import annotations

import sys
from types import SimpleNamespace

from haiku_cli.ai.ollama import DEFAULT_OLLAMA_MODEL, run_ollama_check


def test_run_ollama_check_uses_default_model(monkeypatch) -> None:
    calls: list[dict] = []

    class FakeClient:
        def chat(self, **kwargs):
            calls.append(kwargs)
            assert kwargs["messages"]
            assert kwargs["options"] == {"temperature": 0.1}
            assert kwargs["format"] == "json"
            return {"message": {"content": '{"kigo":{"score":2}}'}}

    monkeypatch.setitem(sys.modules, "ollama", SimpleNamespace(Client=FakeClient))

    result = run_ollama_check(
        "Promptinhalt",
        strict=False,
        fix=False,
    )

    assert result == {"kigo": {"score": 2}}
    assert calls[0]["model"] == DEFAULT_OLLAMA_MODEL
    assert calls[0]["messages"][1]["content"] == "Promptinhalt"


def test_run_ollama_check_falls_back_to_http_when_package_missing(monkeypatch) -> None:
    monkeypatch.delitem(sys.modules, "ollama", raising=False)

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return b'{"message": {"content": "{\\"kigo\\": {\\"score\\": 1}}"}}'

    captured: dict = {}

    def fake_urlopen(req, timeout):
        captured["url"] = req.full_url
        captured["method"] = req.get_method()
        captured["timeout"] = timeout
        captured["payload"] = req.data.decode("utf-8")
        return FakeResponse()

    monkeypatch.setattr("haiku_cli.ai.ollama.request.urlopen", fake_urlopen)

    result = run_ollama_check(
        "Promptinhalt",
        strict=True,
        fix=False,
    )

    assert result == {"kigo": {"score": 1}}
    assert captured["url"].endswith("/api/chat")
    assert captured["method"] == "POST"
    assert captured["timeout"] == 120
    assert f'"model": "{DEFAULT_OLLAMA_MODEL}"' in captured["payload"]
    assert '"format": "json"' in captured["payload"]
    assert '"stream": false' in captured["payload"]
