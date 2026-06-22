import pytest
import os
import json
import shutil
from tools.duplicate_finder import run

@pytest.mark.asyncio
async def test_duplicate_finder_parallel_hash_and_manifest(tmp_path):
    # Create 3 identical files
    file1 = tmp_path / "file1.txt"
    file2 = tmp_path / "file2.txt"
    file3 = tmp_path / "sub" / "file3.txt"

    file3.parent.mkdir()

    content = b"identical content 12345"
    file1.write_bytes(content)

    # Sleep briefly to ensure file modification times differ if filesystem lacks high precision
    import time
    time.sleep(0.01)
    file2.write_bytes(content)
    time.sleep(0.01)
    file3.write_bytes(content)

    assert file1.exists()
    assert file2.exists()
    assert file3.exists()

    params = {
        "directory": str(tmp_path),
        "min_size_kb": "0",
        "action": "delete_backup"
    }

    results = [res async for res in run(params)]

    success_msg = next((r for r in results if r.get("type") == "success"), None)
    assert success_msg is not None
    assert "Deleted 2 duplicate files" in success_msg["message"]

    # file1 should be kept (it's the oldest), file2 and file3 deleted
    assert file1.exists()
    assert not file2.exists()
    assert not file3.exists()

    # Verify manifest creation
    manifest_path = tmp_path / "duplicates_manifest.json"
    assert manifest_path.exists()

    with open(manifest_path, "r") as f:
        manifest = json.load(f)

    assert str(file1) in manifest
    deleted_files = manifest[str(file1)]
    assert len(deleted_files) == 2
    assert str(file2) in deleted_files
    assert str(file3) in deleted_files


@pytest.mark.asyncio
async def test_duplicate_finder_restore_from_manifest(tmp_path):
    file1 = tmp_path / "file1.txt"
    file2 = tmp_path / "file2.txt"
    file3 = tmp_path / "sub" / "file3.txt"

    content = b"identical content 12345"
    file1.write_bytes(content)

    # We only create file1. file2 and file3 are assumed deleted.

    manifest_path = tmp_path / "duplicates_manifest.json"
    manifest_data = {
        str(file1): [str(file2), str(file3)]
    }

    with open(manifest_path, "w") as f:
        json.dump(manifest_data, f)

    assert not file2.exists()
    assert not file3.exists()

    params = {
        "directory": str(tmp_path),
        "action": "restore"
    }

    results = [res async for res in run(params)]

    success_msg = next((r for r in results if r.get("type") == "success"), None)
    assert success_msg is not None
    assert "Restored 2 files" in success_msg["message"]

    # Verify files are restored
    assert file1.exists()
    assert file2.exists()
    assert file3.exists()
    assert file2.read_bytes() == content
    assert file3.read_bytes() == content
