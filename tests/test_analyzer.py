import json

from viral_ops.analyzer import _parse_json, _friendly_error


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


# ------------------------------------------------------------------
# _friendly_error
# ------------------------------------------------------------------

def test_friendly_error_429():
    exc = Exception("429 RESOURCE_EXHAUSTED quota exceeded")
    msg = _friendly_error(exc, "Gemini")
    assert "limit" in msg.lower()
    assert "wait" in msg.lower()
    assert len(msg) < 300  # no JSON blobs

def test_friendly_error_resource_exhausted():
    exc = Exception("RESOURCE_EXHAUSTED free tier")
    msg = _friendly_error(exc, "Gemini")
    assert "limit" in msg.lower()

def test_friendly_error_503():
    exc = Exception("503 UNAVAILABLE high demand")
    msg = _friendly_error(exc, "Gemini")
    assert "demand" in msg.lower() or "wait" in msg.lower()

def test_friendly_error_401():
    exc = Exception("401 invalid API key")
    msg = _friendly_error(exc, "Claude")
    assert "key" in msg.lower() or "rejected" in msg.lower()

def test_friendly_error_generic_is_short():
    exc = Exception("Some unexpected error " + "x" * 500)
    msg = _friendly_error(exc, "OpenAI")
    assert len(msg) < 300  # always truncated, never a wall of text
