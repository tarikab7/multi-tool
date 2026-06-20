import pytest
import os
import json
import shutil
from tools.duplicate_finder import run

@pytest.fixture
def temp_workspace(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    # Create duplicate files
    file1 = workspace / "file1.txt"
    file1.write_text("Hello duplicate world!")

    file2 = workspace / "file2.txt"
    file2.write_text("Hello duplicate world!")

    # Create a unique file to make sure it's not deleted
    file3 = workspace / "file3.txt"
    file3.write_text("I am unique.")

    return workspace

@pytest.mark.asyncio
async def test_duplicate_finder_delete_and_restore(temp_workspace):
    dir_str = str(temp_workspace)

    # Check initial state
    assert len(os.listdir(dir_str)) == 3

    # Run delete action
    results_delete = [res async for res in run({"directory": dir_str, "action": "delete"})]

    # Check successful deletion
    success_msg = next((r["message"] for r in results_delete if r.get("type") == "success"), "")
    assert "Deleted 1 duplicate files" in success_msg

    # Should have 2 files + 1 manifest left
    files_after_delete = os.listdir(dir_str)
    assert "file3.txt" in files_after_delete
    assert "duplicates_manifest.json" in files_after_delete
    assert len(files_after_delete) == 3

    manifest_path = os.path.join(dir_str, "duplicates_manifest.json")
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)

    assert len(manifest) == 1

    # Run restore action
    results_restore = [res async for res in run({"directory": dir_str, "action": "restore"})]

    success_restore_msg = next((r["message"] for r in results_restore if r.get("type") == "success"), "")
    assert "Restored 1 files" in success_restore_msg

    # Files should be back to 3 original files, and manifest deleted
    files_after_restore = os.listdir(dir_str)
    assert len(files_after_restore) == 3
    assert "file1.txt" in files_after_restore
    assert "file2.txt" in files_after_restore
    assert "file3.txt" in files_after_restore
    assert "duplicates_manifest.json" not in files_after_restore
