import pytest
import asyncio
import json
from tools import word_counter, json_minifier, uuid_generator

@pytest.mark.asyncio
async def test_word_counter_success():
    params = {"text": "Hello world\nThis is a test."}
    events = []
    async for event in word_counter.run(params):
        events.append(event)

    assert len(events) > 0
    assert any(e["type"] == "log" for e in events)
    assert any(e["type"] == "found" and "Characters: 27" in e["message"] for e in events)
    assert any(e["type"] == "found" and "Words: 6" in e["message"] for e in events)
    assert any(e["type"] == "found" and "Lines: 2" in e["message"] for e in events)
    assert events[-1]["type"] == "success"

@pytest.mark.asyncio
async def test_word_counter_empty():
    params = {"text": "   "}
    events = []
    async for event in word_counter.run(params):
        events.append(event)

    assert len(events) == 1
    assert events[0]["type"] == "error"

@pytest.mark.asyncio
async def test_json_minifier_minify():
    raw_json = '{\n    "key": "value",\n    "num": 123\n}'
    params = {"raw_json": raw_json, "action": "minify"}
    events = []
    async for event in json_minifier.run(params):
        events.append(event)

    assert any(e["type"] == "log" for e in events)
    found_events = [e for e in events if e["type"] == "found"]
    assert len(found_events) == 1

    # Check if JSON is correctly minified (no spaces after colons/commas, depending on json.dumps settings)
    assert '{"key":"value","num":123}' == found_events[0]["message"]
    assert events[-1]["type"] == "success"

@pytest.mark.asyncio
async def test_json_minifier_format():
    raw_json = '{"key":"value","num":123}'
    params = {"raw_json": raw_json, "action": "format"}
    events = []
    async for event in json_minifier.run(params):
        events.append(event)

    found_events = [e for e in events if e["type"] == "found"]
    assert len(found_events) == 1
    formatted = json.loads(found_events[0]["message"])
    assert formatted["key"] == "value"
    assert events[-1]["type"] == "success"

@pytest.mark.asyncio
async def test_json_minifier_invalid():
    params = {"raw_json": '{"key": "value"'}
    events = []
    async for event in json_minifier.run(params):
        events.append(event)

    assert events[-1]["type"] == "error"

@pytest.mark.asyncio
async def test_uuid_generator():
    params = {"version": "v4", "count": "3"}
    events = []
    async for event in uuid_generator.run(params):
        events.append(event)

    assert any(e["type"] == "log" for e in events)
    found_events = [e for e in events if e["type"] == "found"]
    assert len(found_events) == 3

    for e in found_events:
        # Check if it looks like a UUID
        uid = e["message"]
        assert len(uid) == 36
        assert uid.count('-') == 4

    assert events[-1]["type"] == "success"
