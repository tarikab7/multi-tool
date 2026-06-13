import pytest
from tools.gdrive_link_converter import run

@pytest.mark.asyncio
async def test_run_missing_parameter():
    # Test passing an empty dict
    gen = run({})

    results = [event async for event in gen]

    assert len(results) == 1
    assert results[0] == {"type": "error", "message": "Google Drive sharing URL is required."}

@pytest.mark.asyncio
async def test_run_valid_file_d_url():
    # Test passing a valid /file/d/ URL
    params = {"share_url": "https://drive.google.com/file/d/1A2B3C/view?usp=sharing"}
    gen = run(params)

    results = [event async for event in gen]

    assert len(results) == 4
    assert results[0] == {"type": "log", "message": "Parsing Drive sharing link elements..."}
    assert results[1] == {"type": "found", "message": "File ID: 1A2B3C"}
    assert results[2] == {"type": "found", "message": "Direct Link: https://docs.google.com/uc?export=download&id=1A2B3C"}
    assert results[3] == {"type": "success", "message": "Successfully converted to direct download link."}

@pytest.mark.asyncio
async def test_run_valid_id_url():
    # Test passing a valid open?id= URL
    params = {"share_url": "https://drive.google.com/open?id=1A2B3C&authuser=0"}
    gen = run(params)

    results = [event async for event in gen]

    assert len(results) == 4
    assert results[0] == {"type": "log", "message": "Parsing Drive sharing link elements..."}
    assert results[1] == {"type": "found", "message": "File ID: 1A2B3C"}
    assert results[2] == {"type": "found", "message": "Direct Link: https://docs.google.com/uc?export=download&id=1A2B3C"}
    assert results[3] == {"type": "success", "message": "Successfully converted to direct download link."}

@pytest.mark.asyncio
async def test_run_invalid_url():
    # Test passing an invalid URL format
    params = {"share_url": "https://drive.google.com/some/other/path"}
    gen = run(params)

    results = [event async for event in gen]

    assert len(results) == 2
    assert results[0] == {"type": "log", "message": "Parsing Drive sharing link elements..."}
    assert results[1] == {"type": "error", "message": "Unable to extract file ID. Ensure link has standard Drive format."}
