import pytest
import os
import json
import shutil
from tools.duplicate_finder import run

@pytest.mark.asyncio
async def test_duplicate_finder_delete_and_restore(tmp_path):
    # Setup test environment
    test_dir = tmp_path / "test_dir"
    test_dir.mkdir()

    file1 = test_dir / "file1.txt"
    file1.write_text("Hello duplicate")

    file2 = test_dir / "file2.txt"
    file2.write_text("Hello duplicate")

    file3 = test_dir / "file3.txt"
    file3.write_text("Unique content")

    file4_dir = test_dir / "subdir"
    file4_dir.mkdir()
    file4 = file4_dir / "file4.txt"
    file4.write_text("Hello duplicate")

    # Set modification times to ensure file1 is kept (oldest)
    os.utime(file1, (1000, 1000))
    os.utime(file2, (2000, 2000))
    os.utime(file4, (3000, 3000))

    # Test duplicate deletion with manifest creation
    params_delete = {
        "directory": str(test_dir),
        "min_size_kb": "0",
        "action": "delete",
        "create_manifest": True
    }

    gen_delete = run(params_delete)
    delete_output = []
    async for item in gen_delete:
        delete_output.append(item)

    # Assertions for deletion
    assert os.path.exists(file1)
    assert not os.path.exists(file2)
    assert os.path.exists(file3)
    assert not os.path.exists(file4)

    manifest_path = test_dir / "duplicates_manifest.json"
    assert manifest_path.exists()

    with open(manifest_path, 'r') as f:
        manifest = json.load(f)

    assert len(manifest) == 1
    assert manifest[0]["original"] == str(file1)
    assert str(file2) in manifest[0]["redundant"]
    assert str(file4) in manifest[0]["redundant"]

    # Test restoring from manifest
    params_restore = {
        "directory": str(test_dir),
        "action": "restore"
    }

    gen_restore = run(params_restore)
    restore_output = []
    async for item in gen_restore:
        restore_output.append(item)

    # Assertions for restore
    assert os.path.exists(file1)
    assert os.path.exists(file2)
    assert os.path.exists(file3)
    assert os.path.exists(file4)

    assert file1.read_text() == "Hello duplicate"
    assert file2.read_text() == "Hello duplicate"
    assert file4.read_text() == "Hello duplicate"

@pytest.mark.asyncio
async def test_duplicate_finder_parallel_hashing(tmp_path):
    # Test that parallel hashing works properly without creating errors
    test_dir = tmp_path / "test_parallel"
    test_dir.mkdir()

    # Create 60 small duplicate files (more than batch_size=50)
    for i in range(60):
        file = test_dir / f"file_{i}.txt"
        file.write_text("Hello parallel world")

    params_scan = {
        "directory": str(test_dir),
        "min_size_kb": "0",
        "action": "log"
    }

    gen_scan = run(params_scan)
    scan_output = []
    async for item in gen_scan:
        scan_output.append(item)

    success_msg = next(item["message"] for item in reversed(scan_output) if item["type"] == "success")
    assert "Found 59 duplicate files" in success_msg
