import pytest
import asyncio
import base64
import json
from tools import word_counter, json_minifier, lorem_ipsum, jwt_decoder, uuid_generator

@pytest.mark.asyncio
async def test_word_counter_empty():
    results = [res async for res in word_counter.run({})]
    assert len(results) == 1
    assert results[0]["type"] == "error"

@pytest.mark.asyncio
async def test_word_counter_valid():
    results = [res async for res in word_counter.run({"text": "Hello world!"})]
    types = [r["type"] for r in results]
    assert "log" in types
    assert "found" in types
    assert "success" in types

@pytest.mark.asyncio
async def test_json_minifier_empty():
    results = [res async for res in json_minifier.run({})]
    assert len(results) == 1
    assert results[0]["type"] == "error"

@pytest.mark.asyncio
async def test_json_minifier_valid():
    results = [res async for res in json_minifier.run({"raw_json": '{"a": 1}', "action": "minify"})]
    types = [r["type"] for r in results]
    assert "log" in types
    assert "found" in types
    assert "success" in types

@pytest.mark.asyncio
async def test_lorem_ipsum_valid():
    results = [res async for res in lorem_ipsum.run({"paragraphs": "2"})]
    types = [r["type"] for r in results]
    assert "log" in types
    assert "found" in types
    assert "success" in types
    # Expecting: 1 log, 2 found, 1 success
    assert types.count("found") == 2

@pytest.mark.asyncio
async def test_jwt_decoder_empty():
    results = [res async for res in jwt_decoder.run({})]
    assert len(results) == 1
    assert results[0]["type"] == "error"

@pytest.mark.asyncio
async def test_jwt_decoder_invalid():
    results = [res async for res in jwt_decoder.run({"jwt": "invalid"})]
    types = [r["type"] for r in results]
    assert "error" in types

@pytest.mark.asyncio
async def test_jwt_decoder_valid():
    # Construct a valid JWT structure
    header = base64.urlsafe_b64encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode()).decode().rstrip('=')
    payload = base64.urlsafe_b64encode(json.dumps({"sub": "1234567890", "name": "John Doe", "iat": 1516239022}).encode()).decode().rstrip('=')
    jwt_str = f"{header}.{payload}.signature"

    results = [res async for res in jwt_decoder.run({"jwt": jwt_str})]
    types = [r["type"] for r in results]
    assert "log" in types
    assert "found" in types
    assert "success" in types

@pytest.mark.asyncio
async def test_uuid_generator_v4():
    results = [res async for res in uuid_generator.run({"version": "v4", "count": "3"})]
    types = [r["type"] for r in results]
    assert "log" in types
    assert "found" in types
    assert "success" in types
    assert types.count("found") == 3

@pytest.mark.asyncio
async def test_uuid_generator_v1():
    results = [res async for res in uuid_generator.run({"version": "v1", "count": "2"})]
    types = [r["type"] for r in results]
    assert types.count("found") == 2
