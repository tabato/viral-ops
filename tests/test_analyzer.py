import json

from viral_ops.analyzer import _parse_json


def test_parse_plain_json():
    raw = json.dumps({
        "hook_analysis": "Strong curiosity gap.",
        "viral_reasons": "Timing and emotion.",
        "copy_angles": ["Angle 1", "Angle 2", "Angle 3"],
    })
    result = _parse_json(raw)
    assert result is not None
    assert result["hook_analysis"] == "Strong curiosity gap."
    assert len(result["copy_angles"]) == 3


def test_parse_json_with_backtick_fence():
    raw = '```json\n{"hook_analysis": "test", "viral_reasons": "x", "copy_angles": []}\n```'
    result = _parse_json(raw)
    assert result is not None
    assert result["hook_analysis"] == "test"


def test_parse_json_with_plain_fence():
    raw = '```\n{"hook_analysis": "test"}\n```'
    result = _parse_json(raw)
    assert result is not None


def test_parse_invalid_json_returns_none():
    assert _parse_json("this is not json at all") is None


def test_parse_empty_string_returns_none():
    assert _parse_json("") is None


def test_parse_extracts_embedded_json():
    raw = 'Sure! Here is the analysis:\n{"hook_analysis": "works", "viral_reasons": "y", "copy_angles": []}\nDone.'
    result = _parse_json(raw)
    assert result is not None
    assert result["hook_analysis"] == "works"
