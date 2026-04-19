from __future__ import annotations

import json

import pytest

from haiku_cli.ai import AIResponseError
from haiku_cli.ai.json_response import parse_model_json_dict


def test_parse_plain_json() -> None:
    assert parse_model_json_dict('{"a": 1}', source="Test") == {"a": 1}


def test_parse_json_in_markdown_fence() -> None:
    raw = """Hier ist das Ergebnis:
```json
{"kigo": {"score": 2, "word": "Kirschblüte", "season": "Frühling"}}
```
"""
    out = parse_model_json_dict(raw, source="Test")
    assert out["kigo"]["score"] == 2


def test_parse_json_after_prose() -> None:
    raw = 'Antwort: {"ok": true, "n": 2}'
    assert parse_model_json_dict(raw, source="Test") == {"ok": True, "n": 2}


def test_parse_nested_braces_in_string() -> None:
    raw = r'{"hint": "use {\"a\":1}", "ok": true}'
    out = parse_model_json_dict(raw, source="Test")
    assert out["ok"] is True


def test_parse_rejects_non_object() -> None:
    with pytest.raises(AIResponseError):
        parse_model_json_dict("[1,2,3]", source="Test")


def test_parse_python_bool_literals() -> None:
    raw = '{"ok": True, "no": False, "x": None}'
    out = parse_model_json_dict(raw, source="Test")
    assert out == {"ok": True, "no": False, "x": None}


def test_parse_trailing_commas() -> None:
    raw = '{"a": 1, "b": 2,}'
    assert parse_model_json_dict(raw, source="Test") == {"a": 1, "b": 2}


def test_parse_single_element_array_wrapper() -> None:
    raw = '[{"kigo": {"score": 1, "word": null, "season": null}}]'
    out = parse_model_json_dict(raw, source="Test")
    assert out["kigo"]["score"] == 1


def test_parse_double_encoded_json_string() -> None:
    inner = '{"hard_fail": {"triggered": false, "reason": null}}'
    raw = json.dumps(inner)
    out = parse_model_json_dict(raw, source="Test")
    assert out["hard_fail"]["triggered"] is False
