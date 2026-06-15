import pytest
import os
import json
import shutil
import tempfile
from tools.duplicate_finder import run

@pytest.fixture
def temp_test_dir():
    temp_dir = tempfile.mkdtemp()

    # Create some files
    # Original file
    with open(os.path.join(temp_dir, "original.txt"), "w") as f:
        f.write("duplicate content")

    # Duplicates
    with open(os.path.join(temp_dir, "dup1.txt"), "w") as f:
        f.write("duplicate content")

    os.makedirs(os.path.join(temp_dir, "sub"), exist_ok=True)
    with open(os.path.join(temp_dir, "sub", "dup2.txt"), "w") as f:
        f.write("duplicate content")

    # Unique file
    with open(os.path.join(temp_dir, "unique.txt"), "w") as f:
        f.write("unique content")

    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.mark.asyncio
async def test_duplicate_finder_scan(temp_test_dir):
    params = {
        "directory": temp_test_dir,
        "action": "log",
        "min_size_kb": "0"
    }

    events = [event async for event in run(params)]

    success_events = [e for e in events if e.get("type") == "success"]
    assert len(success_events) > 0
    assert "Found 2 duplicate files" in success_events[-1]["message"]

@pytest.mark.asyncio
async def test_duplicate_finder_delete_with_backup(temp_test_dir):
    params = {
        "directory": temp_test_dir,
        "action": "delete",
        "min_size_kb": "0",
        "backup_manifest": True
    }

    events = [event async for event in run(params)]

    manifest_path = os.path.join(temp_test_dir, "duplicates_manifest.json")
    assert os.path.isfile(manifest_path), "Manifest file should be created"

    with open(manifest_path, "r") as f:
        manifest = json.load(f)

    assert len(manifest) == 1
    original = list(manifest.keys())[0]
    assert len(manifest[original]) == 2

    # Assert dup1 and dup2 are deleted
    assert not os.path.exists(os.path.join(temp_test_dir, "dup1.txt"))
    assert not os.path.exists(os.path.join(temp_test_dir, "sub", "dup2.txt"))
    # Assert original and unique are kept
    assert os.path.exists(original)
    assert os.path.exists(os.path.join(temp_test_dir, "unique.txt"))

@pytest.mark.asyncio
async def test_duplicate_finder_restore(temp_test_dir):
    # First, perform a deletion with backup
    params = {
        "directory": temp_test_dir,
        "action": "delete",
        "min_size_kb": "0",
        "backup_manifest": True
    }
    [event async for event in run(params)]

    # Assert duplicates are deleted
    assert not os.path.exists(os.path.join(temp_test_dir, "dup1.txt"))

    # Now, restore them
    params_restore = {
        "directory": temp_test_dir,
        "action": "restore",
        "min_size_kb": "0"
    }
    events = [event async for event in run(params_restore)]

    success_events = [e for e in events if e.get("type") == "success"]
    assert len(success_events) > 0
    assert "Restored 2" in success_events[-1]["message"]

    # Assert duplicates are back
    assert os.path.exists(os.path.join(temp_test_dir, "dup1.txt"))
    assert os.path.exists(os.path.join(temp_test_dir, "sub", "dup2.txt"))

    # Verify contents are correct
    with open(os.path.join(temp_test_dir, "dup1.txt"), "r") as f:
        assert f.read() == "duplicate content"
