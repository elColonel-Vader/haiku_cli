from __future__ import annotations

import json

import pytest

from haiku_cli.ai import AIResponseError, ProviderUnavailable
from haiku_cli.ai.lmstudio import DEFAULT_LMSTUDIO_MAX_TOKENS, run_lmstudio_check


class _FakeResponse:
    def __init__(self, payload: dict):
        self._payload = payload

    def read(self) -> bytes:
        return json.dumps(self._payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return None


def test_run_lmstudio_check_uses_default_model(monkeypatch) -> None:
    calls: list[tuple[str, str | None]] = []

    def fake_urlopen(req, timeout=0):
        calls.append((req.full_url, req.data.decode("utf-8") if req.data else None))
        if req.full_url.endswith("/chat/completions"):
            return _FakeResponse(
                {
                    "choices": [
                        {
                            "message": {
                                "content": '{"kigo":{"score":2},"kireji":{"score":1}}'
                            }
                        }
                    ]
                }
            )
        raise AssertionError(f"unexpected url: {req.full_url}")

    monkeypatch.setattr("haiku_cli.ai.lmstudio.request.urlopen", fake_urlopen)

    result = run_lmstudio_check("Prompt", strict=False, fix=False)

    assert result["kigo"]["score"] == 2
    assert calls[0][0].endswith("/chat/completions")
    payload = json.loads(calls[0][1])
    assert payload["model"] == "google/gemma-4-e4b"
    assert payload["max_tokens"] == DEFAULT_LMSTUDIO_MAX_TOKENS
    assert payload["stream"] is False
    assert payload["response_format"]["type"] == "json_schema"
    assert payload["response_format"]["json_schema"]["strict"] is True
    assert payload["response_format"]["json_schema"]["schema"]["additionalProperties"] is False


def test_run_lmstudio_check_raises_when_server_unavailable(monkeypatch) -> None:
    def fake_urlopen(req, timeout=0):
        raise OSError("down")

    monkeypatch.setattr("haiku_cli.ai.lmstudio.request.urlopen", fake_urlopen)

    with pytest.raises(ProviderUnavailable):
        run_lmstudio_check("Prompt", strict=False, fix=False)


def test_run_lmstudio_check_uses_max_tokens_env(monkeypatch) -> None:
    captured: dict = {}

    def fake_urlopen(req, timeout=0):
        captured["payload"] = json.loads(req.data.decode("utf-8"))
        return _FakeResponse(
            {
                "choices": [
                    {
                        "message": {
                            "content": '{"kigo":{"score":2},"kireji":{"score":1}}'
                        }
                    }
                ]
            }
        )

    monkeypatch.setenv("LMSTUDIO_MAX_TOKENS", "2400")
    monkeypatch.setattr("haiku_cli.ai.lmstudio.request.urlopen", fake_urlopen)

    run_lmstudio_check("Prompt", strict=False, fix=False)

    assert captured["payload"]["max_tokens"] == 2400


def test_run_lmstudio_check_reports_length_cutoff(monkeypatch) -> None:
    def fake_urlopen(req, timeout=0):
        return _FakeResponse(
            {
                "choices": [
                    {
                        "finish_reason": "length",
                        "message": {"content": '```json\n{"reasoning": "abgeschnitten"'},
                    }
                ]
            }
        )

    monkeypatch.setattr("haiku_cli.ai.lmstudio.request.urlopen", fake_urlopen)

    with pytest.raises(AIResponseError, match="Tokenlimits abgeschnitten"):
        run_lmstudio_check("Prompt", strict=True, fix=False)
