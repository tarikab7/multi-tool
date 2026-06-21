import os
import json
import pytest
import shutil
from tools.duplicate_finder import run

@pytest.fixture
def test_dir(tmp_path):
    # Create test environment with duplicate files
    dir_path = tmp_path / "test_duplicates"
    dir_path.mkdir()

    # original file
    file1 = dir_path / "original.txt"
    file1.write_text("This is some identical content for duplicate testing.")

    # first duplicate
    file2 = dir_path / "copy1.txt"
    file2.write_text("This is some identical content for duplicate testing.")

    # second duplicate
    file3 = dir_path / "copy2.txt"
    file3.write_text("This is some identical content for duplicate testing.")

    # unique file
    file4 = dir_path / "unique.txt"
    file4.write_text("This is completely unique content.")

    # change modification times to guarantee order: original is oldest
    # file1 is original
    os.utime(file1, (1000000000, 1000000000))
    # file2 is newer
    os.utime(file2, (1000000010, 1000000010))
    # file3 is newest
    os.utime(file3, (1000000020, 1000000020))

    return str(dir_path)

@pytest.mark.asyncio
async def test_duplicate_finder_log(test_dir):
    params = {"directory": test_dir, "action": "log"}
    results = [res async for res in run(params)]

    # Verify no files were deleted
    files = os.listdir(test_dir)
    assert len(files) == 4

    # Verify we logged duplicate findings
    success_res = next((r for r in results if r.get("type") == "success"), None)
    assert success_res is not None
    assert "Found 2 duplicate files" in success_res["message"]

@pytest.mark.asyncio
async def test_duplicate_finder_delete_backup_and_restore(test_dir):
    # 1. Action: delete_backup
    params = {"directory": test_dir, "action": "delete_backup"}
    results = [res async for res in run(params)]

    # Verify duplicates were deleted
    files = os.listdir(test_dir)
    # 2 files remaining (original.txt, unique.txt) + 1 manifest (duplicates_manifest.json)
    assert len(files) == 3
    assert "original.txt" in files
    assert "unique.txt" in files
    assert "duplicates_manifest.json" in files
    assert "copy1.txt" not in files
    assert "copy2.txt" not in files

    # Verify manifest contents
    manifest_path = os.path.join(test_dir, "duplicates_manifest.json")
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    assert len(manifest) == 2
    deleted_paths = [item["deleted"] for item in manifest]
    assert any("copy1.txt" in p for p in deleted_paths)
    assert any("copy2.txt" in p for p in deleted_paths)

    # 2. Action: restore
    params_restore = {"directory": test_dir, "action": "restore"}
    restore_results = [res async for res in run(params_restore)]

    # Verify files were restored
    restored_files = os.listdir(test_dir)
    # Should now have the original 4 files + the manifest
    assert len(restored_files) == 5
    assert "copy1.txt" in restored_files
    assert "copy2.txt" in restored_files

    success_res = next((r for r in restore_results if r.get("type") == "success"), None)
    assert success_res is not None
    assert "Restored 2 files" in success_res["message"]
