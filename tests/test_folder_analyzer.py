import pytest
import os
from tools.folder_analyzer import run

@pytest.mark.asyncio
async def test_folder_analyzer_missing_dir():
    gen = run({})
    events = [event async for event in gen]
    dicts = [e.to_dict() if hasattr(e, 'to_dict') else e for e in events]

    assert len(dicts) == 1
    assert dicts[0]["type"] == "error"
    assert "required" in dicts[0]["message"]

@pytest.mark.asyncio
async def test_folder_analyzer_success(tmp_path):
    # Setup dummy tree
    sub1 = tmp_path / "sub1"
    sub1.mkdir()
    (sub1 / "file1.txt").write_text("a" * 1024) # 1 KB

    sub2 = tmp_path / "sub2"
    sub2.mkdir()
    (sub2 / "file2.txt").write_text("b" * 2048) # 2 KB

    gen = run({"directory": str(tmp_path)})
    events = [event async for event in gen]
    dicts = [e.to_dict() if hasattr(e, 'to_dict') else e for e in events]

    # It should have 2 subfolders so we should hit progress
    progress_events = [d for d in dicts if d["type"] == "progress"]
    assert len(progress_events) == 2

    success_event = dicts[-1]
    assert success_event["type"] == "success"
    assert success_event["message"] == "Folder size analysis completed."

@pytest.mark.asyncio
async def test_folder_analyzer_empty_dir(tmp_path):
    gen = run({"directory": str(tmp_path)})
    events = [event async for event in gen]
    dicts = [e.to_dict() if hasattr(e, 'to_dict') else e for e in events]

    assert len(dicts) == 4
    assert dicts[1]["type"] == "log"
    assert "No subdirectories" in dicts[1]["message"]
    assert dicts[-1]["type"] == "success"
