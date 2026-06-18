import os
import json
import pytest
import pytest_asyncio
import asyncio
from tools.duplicate_finder import run

@pytest_asyncio.fixture
async def temp_dir(tmp_path):
    # Create test directory
    test_dir = tmp_path / "dup_test"
    test_dir.mkdir()

    # Create unique file
    unique_file = test_dir / "unique.txt"
    unique_file.write_text("This is a unique file.")

    # Create duplicates
    original = test_dir / "original.txt"
    original.write_text("This is duplicate content.")

    # Wait to ensure original is older
    await asyncio.sleep(0.1)

    dup1 = test_dir / "duplicate1.txt"
    dup1.write_text("This is duplicate content.")

    dup2 = test_dir / "duplicate2.txt"
    dup2.write_text("This is duplicate content.")

    return str(test_dir), {
        "unique": str(unique_file),
        "original": str(original),
        "dup1": str(dup1),
        "dup2": str(dup2)
    }

@pytest.mark.asyncio
async def test_duplicate_finder_parallel_hash(temp_dir):
    d_path, files = temp_dir
    params = {"directory": d_path, "min_size_kb": "0", "action": "log"}

    results = [res async for res in run(params)]

    # Verify success log
    success_logs = [r for r in results if r.get("type") == "success"]
    assert len(success_logs) == 1

    # Should find 1 group with 3 identical files
    assert "Found 2 duplicate files" in success_logs[0]["message"]

    # Verify unique file is not marked as duplicate
    assert not any(files["unique"] in r.get("message", "") for r in results if r.get("type") == "log" and "[KEEP]" in r.get("message", ""))

@pytest.mark.asyncio
async def test_duplicate_finder_backup_and_restore(temp_dir):
    d_path, files = temp_dir

    # Test backup and delete
    params = {"directory": d_path, "min_size_kb": "0", "action": "delete", "create_backup": True}
    results = [res async for res in run(params)]

    # Check deleted
    assert not os.path.exists(files["dup1"])
    assert not os.path.exists(files["dup2"])
    assert os.path.exists(files["original"])

    # Check manifest
    manifest_path = os.path.join(d_path, "duplicates_manifest.json")
    assert os.path.exists(manifest_path)

    with open(manifest_path, 'r') as f:
        manifest = json.load(f)

    assert len(manifest) == 2
    assert manifest[files["dup1"]] == files["original"]
    assert manifest[files["dup2"]] == files["original"]

    # Test restore
    params = {"directory": d_path, "action": "restore"}
    results = [res async for res in run(params)]

    # Check restored
    assert os.path.exists(files["dup1"])
    assert os.path.exists(files["dup2"])

    with open(files["dup1"], 'r') as f:
        assert f.read() == "This is duplicate content."

@pytest.mark.asyncio
async def test_restore_missing_manifest(temp_dir):
    d_path, _ = temp_dir
    params = {"directory": d_path, "action": "restore"}

    results = [res async for res in run(params)]

    error_logs = [r for r in results if r.get("type") == "error"]
    assert len(error_logs) == 1
    assert "No manifest found" in error_logs[0]["message"]
