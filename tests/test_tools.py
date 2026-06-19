import pytest
from tools import word_counter, json_minifier

@pytest.mark.asyncio
async def test_word_counter_success():
    params = {"text": "Hello world\nThis is a test."}
    results = [res async for res in word_counter.run(params)]

    assert any(r.get("type") == "log" and "Tokenizing text inputs..." in r.get("message", "") for r in results)
    assert any(r.get("type") == "found" and "Characters: 27" in r.get("message", "") for r in results)
    assert any(r.get("type") == "found" and "Words: 6" in r.get("message", "") for r in results)
    assert any(r.get("type") == "found" and "Lines: 2" in r.get("message", "") for r in results)
    assert any(r.get("type") == "success" and "Counting finished" in r.get("message", "") for r in results)

@pytest.mark.asyncio
async def test_word_counter_empty():
    params = {"text": "   "}
    results = [res async for res in word_counter.run(params)]

    assert len(results) == 1
    assert results[0].get("type") == "error"
    assert "Input text is required" in results[0].get("message", "")

@pytest.mark.asyncio
async def test_json_minifier_format():
    params = {
        "raw_json": '{"a": 1, "b": 2}',
        "action": "format"
    }
    results = [res async for res in json_minifier.run(params)]

    assert any(r.get("type") == "log" and "format" in r.get("message", "") for r in results)

    found_event = next((r for r in results if r.get("type") == "found"), None)
    assert found_event is not None
    assert '{\n    "a": 1,\n    "b": 2\n}' in found_event.get("message", "")

    assert any(r.get("type") == "success" for r in results)

@pytest.mark.asyncio
async def test_json_minifier_minify():
    params = {
        "raw_json": '{\n    "a": 1,\n    "b": 2\n}',
        "action": "minify"
    }
    results = [res async for res in json_minifier.run(params)]

    assert any(r.get("type") == "log" and "minify" in r.get("message", "") for r in results)

    found_event = next((r for r in results if r.get("type") == "found"), None)
    assert found_event is not None
    assert '{"a":1,"b":2}' in found_event.get("message", "")

    assert any(r.get("type") == "success" for r in results)

@pytest.mark.asyncio
async def test_json_minifier_empty():
    params = {"raw_json": ""}
    results = [res async for res in json_minifier.run(params)]

    assert len(results) == 1
    assert results[0].get("type") == "error"
    assert "JSON input string is required" in results[0].get("message", "")

@pytest.mark.asyncio
async def test_json_minifier_invalid():
    params = {
        "raw_json": '{"a": 1, "b":}',
        "action": "format"
    }
    results = [res async for res in json_minifier.run(params)]

    assert any(r.get("type") == "error" and "Invalid JSON syntax" in r.get("message", "") for r in results)
