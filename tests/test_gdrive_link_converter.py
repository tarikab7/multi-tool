import pytest
import asyncio
from tools.gdrive_link_converter import run

@pytest.mark.asyncio
async def test_run_missing_parameter():
    generator = run({})
    items = [item async for item in generator]

    assert len(items) == 1
    assert items[0]["type"] == "error"
    assert "Google Drive sharing URL is required" in items[0]["message"]

@pytest.mark.asyncio
async def test_run_empty_url():
    generator = run({"share_url": "   "})
    items = [item async for item in generator]

    assert len(items) == 1
    assert items[0]["type"] == "error"
    assert "Google Drive sharing URL is required" in items[0]["message"]

@pytest.mark.asyncio
async def test_run_file_d_format():
    generator = run({"share_url": "https://drive.google.com/file/d/1A2B3C/view?usp=sharing"})
    items = [item async for item in generator]

    assert len(items) == 4
    assert items[0]["type"] == "log"
    assert items[1]["type"] == "found"
    assert items[1]["message"] == "File ID: 1A2B3C"
    assert items[2]["type"] == "found"
    assert items[2]["message"] == "Direct Link: https://docs.google.com/uc?export=download&id=1A2B3C"
    assert items[3]["type"] == "success"

@pytest.mark.asyncio
async def test_run_open_id_format():
    generator = run({"share_url": "https://drive.google.com/open?id=1A2B3C"})
    items = [item async for item in generator]

    assert len(items) == 4
    assert items[0]["type"] == "log"
    assert items[1]["type"] == "found"
    assert items[1]["message"] == "File ID: 1A2B3C"
    assert items[2]["type"] == "found"
    assert items[2]["message"] == "Direct Link: https://docs.google.com/uc?export=download&id=1A2B3C"
    assert items[3]["type"] == "success"

@pytest.mark.asyncio
async def test_run_invalid_url():
    generator = run({"share_url": "https://drive.google.com/invalid"})
    items = [item async for item in generator]

    assert len(items) == 2
    assert items[0]["type"] == "log"
    assert items[1]["type"] == "error"
    assert "Unable to extract file ID" in items[1]["message"]
