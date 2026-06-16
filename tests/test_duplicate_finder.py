import os
import json
import pytest
import shutil
import asyncio
from tools.duplicate_finder import run

@pytest.fixture
def test_directory(tmp_path):
    d = tmp_path / "dup_test"
    d.mkdir()

    # Create some files
    # file1.txt and file2.txt are identical
    f1 = d / "file1.txt"
    f1.write_text("Hello World")

    f2 = d / "file2.txt"
    f2.write_text("Hello World")

    # file3.txt is different
    f3 = d / "file3.txt"
    f3.write_text("Hello Universe")

    # Wait to ensure timestamp difference for keeping oldest
    import time
    time.sleep(0.01)
    os.utime(f1, (time.time() - 10, time.time() - 10)) # make f1 older so it's kept

    return d

@pytest.mark.asyncio
async def test_duplicate_finder_log(test_directory):
    params = {
        "directory": str(test_directory),
        "min_size_kb": "0",
        "action": "log"
    }
    gen = run(params)
    results = [res async for res in gen]

    # Verify we found the duplicate
    logs = [r for r in results if r["type"] == "log"]
    success = [r for r in results if r["type"] == "success"]

    assert any("Found 1 duplicate content group" in l["message"] for l in logs)
    assert any("[KEEP]" in l["message"] and "file1.txt" in l["message"] for l in logs)
    assert any("[DUPLICATE]" in l["message"] and "file2.txt" in l["message"] for l in logs)
    assert len(success) == 1

@pytest.mark.asyncio
async def test_duplicate_finder_delete_backup(test_directory):
    params = {
        "directory": str(test_directory),
        "min_size_kb": "0",
        "action": "delete_backup"
    }
    gen = run(params)
    results = [res async for res in gen]

    # Verify file2.txt was deleted
    assert os.path.exists(test_directory / "file1.txt")
    assert not os.path.exists(test_directory / "file2.txt")

    # Verify manifest was created
    manifest_path = test_directory / "duplicates_manifest.json"
    assert os.path.exists(manifest_path)

    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)

    assert str(test_directory / "file2.txt") in manifest
    assert manifest[str(test_directory / "file2.txt")] == str(test_directory / "file1.txt")

@pytest.mark.asyncio
async def test_duplicate_finder_restore(test_directory):
    # First, run delete_backup
    params_delete = {
        "directory": str(test_directory),
        "min_size_kb": "0",
        "action": "delete_backup"
    }
    gen_delete = run(params_delete)
    [res async for res in gen_delete]

    assert not os.path.exists(test_directory / "file2.txt")

    # Now, run restore
    params_restore = {
        "directory": str(test_directory),
        "action": "restore"
    }
    gen_restore = run(params_restore)
    results = [res async for res in gen_restore]

    # Verify file2.txt was restored
    assert os.path.exists(test_directory / "file2.txt")
    assert (test_directory / "file2.txt").read_text() == "Hello World"

    success = [r for r in results if r["type"] == "success"]
    assert any("Restored: 1" in s["message"] for s in success)
