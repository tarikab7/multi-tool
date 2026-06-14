import pytest
import json
from tools import word_counter, json_minifier

@pytest.mark.asyncio
async def test_word_counter_valid():
    params = {"text": "hello world. this is a test."}
    events = []
    async for event in word_counter.run(params):
        events.append(event)

    # Check that it produces the correct sequence
    assert any(e.get("type") == "log" for e in events)
    assert any("Characters: 28" in e.get("message", "") for e in events)
    assert any("Words: 6" in e.get("message", "") for e in events)
    assert events[-1].get("type") == "success"

@pytest.mark.asyncio
async def test_word_counter_empty():
    params = {"text": "   "}
    events = []
    async for event in word_counter.run(params):
        events.append(event)

    assert len(events) == 1
    assert events[0].get("type") == "error"
    assert "required" in events[0].get("message", "")

@pytest.mark.asyncio
async def test_json_minifier_format():
    params = {
        "raw_json": '{"a": 1, "b": 2}',
        "action": "format"
    }
    events = []
    async for event in json_minifier.run(params):
        events.append(event)

    assert any(e.get("type") == "log" for e in events)

    found_events = [e for e in events if e.get("type") == "found"]
    assert len(found_events) == 1

    # Check formatting
    formatted_json = found_events[0].get("message")
    assert "{\n    \"a\": 1,\n    \"b\": 2\n}" == formatted_json

    assert events[-1].get("type") == "success"

@pytest.mark.asyncio
async def test_json_minifier_minify():
    params = {
        "raw_json": '{\n  "a": 1,\n  "b": 2\n}',
        "action": "minify"
    }
    events = []
    async for event in json_minifier.run(params):
        events.append(event)

    found_events = [e for e in events if e.get("type") == "found"]
    assert len(found_events) == 1

    # Check minified output
    minified_json = found_events[0].get("message")
    assert '{"a":1,"b":2}' == minified_json

    assert events[-1].get("type") == "success"

@pytest.mark.asyncio
async def test_json_minifier_invalid():
    params = {
        "raw_json": '{a: 1}',
    }
    events = []
    async for event in json_minifier.run(params):
        events.append(event)

    assert events[-1].get("type") == "error"
    assert "Invalid JSON syntax" in events[-1].get("message", "")

@pytest.mark.asyncio
async def test_json_minifier_empty():
    params = {"raw_json": ""}
    events = []
    async for event in json_minifier.run(params):
        events.append(event)

    assert len(events) == 1
    assert events[0].get("type") == "error"
    assert "required" in events[0].get("message", "")
