from __future__ import annotations

import json

import pytest

from haiku_cli.ai import ProviderUnavailable
from haiku_cli.ai.lmstudio import run_lmstudio_check


class _FakeResponse:
    def __init__(self, payload: dict):
        self._payload = payload

    def read(self) -> bytes:
        return json.dumps(self._payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return None


def test_run_lmstudio_check_uses_first_loaded_model(monkeypatch) -> None:
    calls: list[tuple[str, str | None]] = []

    def fake_urlopen(req, timeout=0):
        calls.append((req.full_url, req.data.decode("utf-8") if req.data else None))
        if req.full_url.endswith("/models"):
            return _FakeResponse({"data": [{"id": "qwen-local"}]})
        if req.full_url.endswith("/chat/completions"):
            return _FakeResponse(
                {
                    "choices": [
                        {
                            "message": {
                                "content": '{"kigo":{"present":true},"kireji":{"present":false}}'
                            }
                        }
                    ]
                }
            )
        raise AssertionError(f"unexpected url: {req.full_url}")

    monkeypatch.setattr("haiku_cli.ai.lmstudio.request.urlopen", fake_urlopen)

    result = run_lmstudio_check("Prompt", strict=False, fix=False)

    assert result["kigo"]["present"] is True
    assert calls[0][0].endswith("/models")
    assert '"model": "qwen-local"' in calls[1][1]


def test_run_lmstudio_check_raises_when_server_unavailable(monkeypatch) -> None:
    def fake_urlopen(req, timeout=0):
        raise OSError("down")

    monkeypatch.setattr("haiku_cli.ai.lmstudio.request.urlopen", fake_urlopen)

    with pytest.raises(ProviderUnavailable):
        run_lmstudio_check("Prompt", strict=False, fix=False)
