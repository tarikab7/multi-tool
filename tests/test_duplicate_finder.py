import os
import json
import pytest
import pytest_asyncio
import asyncio
from tools.duplicate_finder import run

@pytest.fixture
def test_directory(tmp_path):
    dir_path = tmp_path / "dup_test"
    dir_path.mkdir()

    # Create original files
    file1 = dir_path / "original.txt"
    file1.write_text("hello duplicate world!")

    file2 = dir_path / "duplicate1.txt"
    file2.write_text("hello duplicate world!")

    file3 = dir_path / "duplicate2.txt"
    file3.write_text("hello duplicate world!")

    file4 = dir_path / "unique.txt"
    file4.write_text("something else completely")

    return dir_path

@pytest.mark.asyncio
async def test_log_action(test_directory):
    params = {"directory": str(test_directory), "min_size_kb": "0", "action": "log"}
    results = [res async for res in run(params)]

    # Check if duplicate is found
    success_msg = next((r["message"] for r in results if r["type"] == "success"), "")
    assert "Found 2 duplicate files" in success_msg

    # Ensure no files were deleted
    files = list(test_directory.iterdir())
    assert len(files) == 4

@pytest.mark.asyncio
async def test_backup_delete_and_restore(test_directory):
    # 1. Run backup_delete
    params = {"directory": str(test_directory), "min_size_kb": "0", "action": "backup_delete"}
    results = [res async for res in run(params)]

    # Check deletion success
    success_msg = next((r["message"] for r in results if r["type"] == "success"), "")
    assert "Deleted 2 duplicate files" in success_msg

    # Verify files are gone
    files = list(test_directory.iterdir())
    # original.txt + unique.txt + duplicates_manifest.json = 3 files
    assert len(files) == 3

    # Check manifest
    manifest_path = test_directory / "duplicates_manifest.json"
    assert manifest_path.exists()

    with open(manifest_path, 'r') as f:
        manifest = json.load(f)

    assert len(manifest) == 2

    # We can't guarantee which two files are deleted because they have identical mtime due to fast test execution.
    # But we know 2 files out of the 3 identical ones were deleted.
    deleted_paths = list(manifest.keys())

    # 2. Run restore
    restore_params = {"directory": str(test_directory), "action": "restore"}
    restore_results = [res async for res in run(restore_params)]

    restore_success = next((r["message"] for r in restore_results if r["type"] == "success"), "")
    assert "Restored 2 files from manifest" in restore_success

    # Verify files are back
    # original.txt + unique.txt + duplicate1.txt + duplicate2.txt + duplicates_manifest.json = 5 files
    restored_files = list(test_directory.iterdir())
    assert len(restored_files) == 5

    # Verify contents are correct
    assert (test_directory / "duplicate1.txt").read_text() == "hello duplicate world!"
    assert (test_directory / "duplicate2.txt").read_text() == "hello duplicate world!"
    assert (test_directory / "original.txt").read_text() == "hello duplicate world!"
