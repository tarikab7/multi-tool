import pytest
import os
from tools.folder_analyzer import get_folder_size_sync, run, format_size

def test_get_folder_size_sync(tmp_path):
    test_dir = tmp_path / "test_dir"
    test_dir.mkdir()
    file1 = test_dir / "file1.txt"
    file1.write_text("a" * 10) # 10 bytes

    sub_dir = test_dir / "sub_dir"
    sub_dir.mkdir()
    file2 = sub_dir / "file2.txt"
    file2.write_text("b" * 20) # 20 bytes

    size = get_folder_size_sync(str(test_dir))
    assert size == 30

def test_format_size():
    assert format_size(500) == "500 Bytes"
    assert format_size(1024) == "1.00 KB"
    assert format_size(1024 * 1024) == "1.00 MB"
    assert format_size(1024 * 1024 * 1024) == "1.00 GB"

@pytest.mark.asyncio
async def test_run(tmp_path):
    test_dir = tmp_path / "test_dir"
    test_dir.mkdir()
    file1 = test_dir / "file1.txt"
    file1.write_text("a" * 10)

    gen = run({"directory": str(test_dir)})
    results = [event async for event in gen]

    assert any(event.get("type") == "success" for event in results)
