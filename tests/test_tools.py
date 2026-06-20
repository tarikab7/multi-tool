import pytest
import asyncio
from tools import word_counter, json_minifier

@pytest.mark.asyncio
async def test_word_counter_success():
    params = {"text": "hello world test"}
    events = []
    async for event in word_counter.run(params):
        events.append(event)

    # Verify events
    types = [e["type"] for e in events]
    assert "log" in types
    assert "found" in types
    assert "success" in types

    found_events = [e for e in events if e["type"] == "found"]
    messages = [e["message"] for e in found_events]

    assert any("Characters: 16" in m for m in messages)
    assert any("Words: 3" in m for m in messages)
    assert any("Lines: 1" in m for m in messages)

@pytest.mark.asyncio
async def test_word_counter_empty():
    params = {"text": "   "}
    events = []
    async for event in word_counter.run(params):
        events.append(event)

    assert len(events) == 1
    assert events[0]["type"] == "error"
    assert "required" in events[0]["message"]

@pytest.mark.asyncio
async def test_json_minifier_format():
    params = {"raw_json": "{\"a\": 1, \"b\": 2}", "action": "format"}
    events = []
    async for event in json_minifier.run(params):
        events.append(event)

    assert events[-1]["type"] == "success"
    found_events = [e for e in events if e["type"] == "found"]
    assert len(found_events) == 1

    out = found_events[0]["message"]
    assert "{\n" in out
    assert '"a": 1' in out

@pytest.mark.asyncio
async def test_json_minifier_minify():
    params = {"raw_json": "{\n  \"a\": 1,\n  \"b\": 2\n}", "action": "minify"}
    events = []
    async for event in json_minifier.run(params):
        events.append(event)

    assert events[-1]["type"] == "success"
    found_events = [e for e in events if e["type"] == "found"]
    assert len(found_events) == 1

    out = found_events[0]["message"]
    assert out == '{"a":1,"b":2}'

@pytest.mark.asyncio
async def test_json_minifier_invalid():
    params = {"raw_json": "{\"a\": 1, }", "action": "format"}
    events = []
    async for event in json_minifier.run(params):
        events.append(event)

    assert events[-1]["type"] == "error"
    assert "Invalid JSON syntax" in events[-1]["message"]

@pytest.mark.asyncio
async def test_json_minifier_empty():
    params = {"raw_json": "", "action": "format"}
    events = []
    async for event in json_minifier.run(params):
        events.append(event)

    assert len(events) == 1
    assert events[0]["type"] == "error"
    assert "required" in events[0]["message"]
