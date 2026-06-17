import pytest
import json
from tools.word_counter import run as run_word_counter
from tools.json_minifier import run as run_json_minifier

@pytest.mark.asyncio
async def test_word_counter_success():
    params = {"text": "hello world\nthis is a test"}
    events = [event async for event in run_word_counter(params)]

    # Verify the structure of the events
    assert any(e.get("type") == "log" for e in events)
    assert any(e.get("type") == "found" and "Characters: 26" in e.get("message") for e in events)
    assert any(e.get("type") == "found" and "Words: 6" in e.get("message") for e in events)
    assert any(e.get("type") == "found" and "Lines: 2" in e.get("message") for e in events)
    assert any(e.get("type") == "success" for e in events)

@pytest.mark.asyncio
async def test_word_counter_empty():
    params = {"text": "   "}
    events = [event async for event in run_word_counter(params)]

    assert len(events) == 1
    assert events[0].get("type") == "error"
    assert "Input text is required" in events[0].get("message")

@pytest.mark.asyncio
async def test_json_minifier_format():
    params = {"raw_json": '{"a": 1, "b": 2}', "action": "format"}
    events = [event async for event in run_json_minifier(params)]

    assert any(e.get("type") == "log" for e in events)

    found_events = [e for e in events if e.get("type") == "found"]
    assert len(found_events) == 1
    formatted_json = found_events[0].get("message")

    # Check that it's nicely formatted (indentation)
    assert "    \"a\": 1" in formatted_json

    assert any(e.get("type") == "success" for e in events)

@pytest.mark.asyncio
async def test_json_minifier_minify():
    params = {"raw_json": '{\n    "a": 1,\n    "b": 2\n}', "action": "minify"}
    events = [event async for event in run_json_minifier(params)]

    found_events = [e for e in events if e.get("type") == "found"]
    assert len(found_events) == 1
    minified_json = found_events[0].get("message")

    assert minified_json == '{"a":1,"b":2}'

@pytest.mark.asyncio
async def test_json_minifier_invalid():
    params = {"raw_json": '{a: 1}'} # Invalid JSON
    events = [event async for event in run_json_minifier(params)]

    error_events = [e for e in events if e.get("type") == "error"]
    assert len(error_events) == 1
    assert "Invalid JSON syntax" in error_events[0].get("message")

@pytest.mark.asyncio
async def test_json_minifier_empty():
    params = {"raw_json": ''}
    events = [event async for event in run_json_minifier(params)]

    assert len(events) == 1
    assert events[0].get("type") == "error"
    assert "JSON input string is required" in events[0].get("message")
