import os
import json
import shutil
import pytest
from tools.duplicate_finder import run

@pytest.fixture
def duplicate_env(tmp_path):
    # Create an environment with duplicate files
    dir_path = tmp_path / "test_dups"
    dir_path.mkdir()

    file1 = dir_path / "original.txt"
    file1.write_text("duplicate_content")

    # Ensure slightly different mtime
    import time
    time.sleep(0.01)

    file2 = dir_path / "copy.txt"
    file2.write_text("duplicate_content")

    # A unique file
    file3 = dir_path / "unique.txt"
    file3.write_text("unique_content")

    return dir_path

@pytest.mark.asyncio
async def test_duplicate_finder_manifest_and_restore(duplicate_env):
    dir_path = str(duplicate_env)

    # 1. Run the tool to delete duplicates and create a manifest
    params = {
        "directory": dir_path,
        "min_size_kb": "0",
        "action": "delete",
        "create_manifest": True
    }

    results = [res async for res in run(params)]

    # Assert successful deletion
    success_msg = next((r["message"] for r in results if r.get("type") == "success"), "")
    assert "Deleted 1 duplicate" in success_msg

    # Assert manifest was created
    manifest_path = duplicate_env / "duplicates_manifest.json"
    assert manifest_path.exists()

    with open(manifest_path, "r") as f:
        manifest = json.load(f)

    assert len(manifest) == 1
    assert "original" in manifest[0]
    assert "deleted" in manifest[0]

    original_path = manifest[0]["original"]
    deleted_path = manifest[0]["deleted"]

    # Verify original exists and deleted does not
    assert os.path.exists(original_path)
    assert not os.path.exists(deleted_path)

    # 2. Run the tool to restore from the manifest
    restore_params = {
        "directory": dir_path,
        "action": "restore"
    }

    restore_results = [res async for res in run(restore_params)]

    # Assert successful restore
    restore_success_msg = next((r["message"] for r in restore_results if r.get("type") == "success"), "")
    assert "Recovered 1 files" in restore_success_msg

    # Verify the deleted file was restored
    assert os.path.exists(deleted_path)
    with open(deleted_path, "r") as f:
        content = f.read()
    assert content == "duplicate_content"
