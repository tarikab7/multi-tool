import pytest
import asyncio
from tools.word_counter import run as run_word_counter
from tools.json_minifier import run as run_json_minifier

@pytest.mark.asyncio
async def test_word_counter():
    results = [res async for res in run_word_counter({"text": "hello world. this is a test."})]

    # Expect 1 log, 4 found (Chars, Words, Lines, Est Time), 1 success
    assert len(results) == 6
    assert results[0]["type"] == "log"
    assert results[1]["message"] == "Characters: 28"
    assert results[2]["message"] == "Words: 6"
    assert results[3]["message"] == "Lines: 1"
    assert "Est. Reading Time" in results[4]["message"]
    assert results[-1]["type"] == "success"

@pytest.mark.asyncio
async def test_word_counter_empty():
    results = [res async for res in run_word_counter({"text": "  "})]
    assert len(results) == 1
    assert results[0]["type"] == "error"

@pytest.mark.asyncio
async def test_json_minifier_minify():
    raw_json = '{\n    "key": "value",\n    "array": [\n        1,\n        2\n    ]\n}'
    results = [res async for res in run_json_minifier({"raw_json": raw_json, "action": "minify"})]

    assert len(results) == 3
    assert results[0]["type"] == "log"
    assert results[1]["type"] == "found"
    assert results[1]["message"] == '{"key":"value","array":[1,2]}'
    assert results[2]["type"] == "success"

@pytest.mark.asyncio
async def test_json_minifier_format():
    raw_json = '{"key":"value","array":[1,2]}'
    results = [res async for res in run_json_minifier({"raw_json": raw_json, "action": "format"})]

    assert len(results) == 3
    assert results[0]["type"] == "log"
    assert results[1]["type"] == "found"
    # The formatted json will have indents, let's just make sure it's valid json and not minified
    import json
    assert json.loads(results[1]["message"]) == {"key": "value", "array": [1, 2]}
    assert "    " in results[1]["message"] # check indentation
    assert results[2]["type"] == "success"

@pytest.mark.asyncio
async def test_json_minifier_invalid_json():
    raw_json = '{"key": "value",}' # Invalid json (trailing comma)
    results = [res async for res in run_json_minifier({"raw_json": raw_json})]

    assert len(results) == 2
    assert results[0]["type"] == "log"
    assert results[1]["type"] == "error"
    assert "Invalid JSON syntax" in results[1]["message"]

@pytest.mark.asyncio
async def test_json_minifier_empty():
    results = [res async for res in run_json_minifier({})]
    assert len(results) == 1
    assert results[0]["type"] == "error"
