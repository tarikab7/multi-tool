import os
import pytest
import asyncio
from tools.secure_shredder import shred_file_sync, run

@pytest.fixture
def temp_file(tmp_path):
    file_path = tmp_path / "test_file.txt"
    file_path.write_text("dummy content")
    return str(file_path)

@pytest.fixture
def temp_dir(tmp_path):
    dir_path = tmp_path / "test_dir"
    dir_path.mkdir()
    (dir_path / "file1.txt").write_text("content1")
    (dir_path / "file2.txt").write_text("content2")
    return str(dir_path)

def test_shred_file_sync(temp_file):
    assert os.path.exists(temp_file)
    success = shred_file_sync(temp_file, passes=1)
    assert success is True
    assert not os.path.exists(temp_file)

def test_shred_file_sync_empty_file(tmp_path):
    empty_file = tmp_path / "empty.txt"
    empty_file.touch()
    assert os.path.exists(str(empty_file))
    success = shred_file_sync(str(empty_file), passes=1)
    assert success is True
    assert not os.path.exists(str(empty_file))

def test_shred_file_sync_nonexistent():
    success = shred_file_sync("nonexistent_file.txt", passes=1)
    assert success is False

@pytest.mark.asyncio
async def test_run_missing_target():
    events = [event async for event in run({})]
    assert len(events) == 1
    assert events[0]["type"] == "error"
    assert "Target path is required" in events[0]["message"]

@pytest.mark.asyncio
async def test_run_nonexistent_target():
    events = [event async for event in run({"target_path": "nonexistent_path"})]
    assert len(events) == 1
    assert events[0]["type"] == "error"
    assert "does not exist" in events[0]["message"]

@pytest.mark.asyncio
async def test_run_invalid_passes(temp_file):
    events = [event async for event in run({"target_path": temp_file, "passes": "invalid"})]
    assert len(events) == 1
    assert events[0]["type"] == "error"
    assert "Passes must be an integer" in events[0]["message"]

@pytest.mark.asyncio
async def test_run_success_single_file(temp_file):
    events = [event async for event in run({"target_path": temp_file, "passes": "1"})]

    assert any(e.get("type") == "log" and "Starting secure shredding" in e.get("message", "") for e in events)
    assert any(e.get("type") == "progress" and e.get("percent") == 100 for e in events)

    success_events = [e for e in events if e.get("type") == "success"]
    assert len(success_events) == 1
    assert "Completed. Securely shredded 1 of 1 files." in success_events[0]["message"]
    assert not os.path.exists(temp_file)

@pytest.mark.asyncio
async def test_run_success_directory(temp_dir):
    events = [event async for event in run({"target_path": temp_dir, "passes": "1"})]

    success_events = [e for e in events if e.get("type") == "success"]
    assert len(success_events) == 1
    assert "Completed. Securely shredded 2 of 2 files." in success_events[0]["message"]
    assert not os.path.exists(temp_dir)

@pytest.mark.asyncio
async def test_run_empty_directory(tmp_path):
    empty_dir = tmp_path / "empty_dir"
    empty_dir.mkdir()
    empty_dir_str = str(empty_dir)

    events = [event async for event in run({"target_path": empty_dir_str})]

    assert any(e.get("type") == "log" and "No files found to shred" in e.get("message", "") for e in events)
    success_events = [e for e in events if e.get("type") == "success"]
    assert len(success_events) == 1
    assert "Finished shredding" in success_events[0]["message"]

    assert not os.path.exists(empty_dir_str)
