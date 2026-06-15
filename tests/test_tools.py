import pytest
from tools.word_counter import run as run_word_counter
from tools.json_minifier import run as run_json_minifier

@pytest.mark.asyncio
async def test_word_counter_empty():
    results = [res async for res in run_word_counter({"text": ""})]
    assert len(results) == 1
    assert results[0]["type"] == "error"
    assert "required" in results[0]["message"]

@pytest.mark.asyncio
async def test_word_counter_success():
    text = "Hello world.\nThis is a test."
    results = [res async for res in run_word_counter({"text": text})]

    assert any(r["type"] == "log" for r in results)

    found_events = [r for r in results if r["type"] == "found"]
    assert any("Characters: 28" in r["message"] for r in found_events)
    assert any("Words: 6" in r["message"] for r in found_events)
    assert any("Lines: 2" in r["message"] for r in found_events)
    assert any("Est. Reading Time:" in r["message"] for r in found_events)

    assert results[-1]["type"] == "success"
    assert "finished" in results[-1]["message"]

@pytest.mark.asyncio
async def test_json_minifier_empty():
    results = [res async for res in run_json_minifier({"raw_json": ""})]
    assert len(results) == 1
    assert results[0]["type"] == "error"
    assert "required" in results[0]["message"]

@pytest.mark.asyncio
async def test_json_minifier_format():
    raw_json = '{"a":1,"b":  2}'
    results = [res async for res in run_json_minifier({"raw_json": raw_json, "action": "format"})]

    assert any(r["type"] == "log" for r in results)

    found_events = [r for r in results if r["type"] == "found"]
    assert len(found_events) == 1
    formatted = found_events[0]["message"]
    assert "{\n    \"a\": 1,\n    \"b\": 2\n}" in formatted

    assert results[-1]["type"] == "success"

@pytest.mark.asyncio
async def test_json_minifier_minify():
    raw_json = '{\n  "a": 1,\n  "b": 2\n}'
    results = [res async for res in run_json_minifier({"raw_json": raw_json, "action": "minify"})]

    found_events = [r for r in results if r["type"] == "found"]
    assert len(found_events) == 1
    minified = found_events[0]["message"]
    assert minified == '{"a":1,"b":2}'

    assert results[-1]["type"] == "success"

@pytest.mark.asyncio
async def test_json_minifier_invalid():
    raw_json = '{"a": 1'
    results = [res async for res in run_json_minifier({"raw_json": raw_json})]

    assert any(r["type"] == "log" for r in results)
    assert results[-1]["type"] == "error"
    assert "Invalid JSON" in results[-1]["message"]
