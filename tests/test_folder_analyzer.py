import pytest
import os
import asyncio
from tools.folder_analyzer import run, format_size, get_folder_size_sync

@pytest.mark.asyncio
async def test_folder_analyzer(tmp_path):
    # Setup test directory structure
    d1 = tmp_path / "dir1"
    d1.mkdir()
    (d1 / "file1.txt").write_text("Hello" * 100) # 500 bytes

    d2 = tmp_path / "dir2"
    d2.mkdir()
    (d2 / "file2.txt").write_text("World" * 200) # 1000 bytes

    (tmp_path / "file3.txt").write_text("Test" * 50) # 200 bytes

    params = {"directory": str(tmp_path)}

    events = []
    async for event in run(params):
        events.append(event)

    assert any(e.get("type") == "success" for e in events)
    assert any("Total size of all subfolders: 1.46 KB" in str(e.get("message")) for e in events)

    # Test individual functions to ensure accuracy
    size1 = get_folder_size_sync(str(d1))
    assert size1 == 500

    size2 = get_folder_size_sync(str(d2))
    assert size2 == 1000

    assert format_size(1500) == "1.46 KB"

@pytest.mark.asyncio
async def test_folder_analyzer_empty(tmp_path):
    # Empty directory test
    params = {"directory": str(tmp_path)}
    events = []
    async for event in run(params):
        events.append(event)

    assert any(e.get("type") == "success" for e in events)
    assert any("No subdirectories found" in str(e.get("message")) for e in events)
