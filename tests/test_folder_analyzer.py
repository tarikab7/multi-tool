import os
import tempfile
import pytest
from tools.folder_analyzer import get_folder_size_sync

def test_get_folder_size_sync():
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create some files
        file1_path = os.path.join(temp_dir, "file1.txt")
        with open(file1_path, "wb") as f:
            f.write(b"A" * 1024)  # 1 KB

        # Create a subfolder
        subfolder_path = os.path.join(temp_dir, "subfolder")
        os.makedirs(subfolder_path)

        file2_path = os.path.join(subfolder_path, "file2.txt")
        with open(file2_path, "wb") as f:
            f.write(b"B" * 2048)  # 2 KB

        assert get_folder_size_sync(temp_dir) == 3072

def test_get_folder_size_sync_empty_folder():
    with tempfile.TemporaryDirectory() as temp_dir:
        assert get_folder_size_sync(temp_dir) == 0

def test_get_folder_size_sync_with_symlink():
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a file
        file1_path = os.path.join(temp_dir, "file1.txt")
        with open(file1_path, "wb") as f:
            f.write(b"A" * 1024)  # 1 KB

        # Create a symlink to file1
        symlink_path = os.path.join(temp_dir, "symlink.txt")
        try:
            os.symlink(file1_path, symlink_path)
        except OSError:
            # If creating symlink fails, skip the rest of the test
            pytest.skip("Could not create symlink")

        # The size should only be 1024, symlink size is ignored
        assert get_folder_size_sync(temp_dir) == 1024

def test_get_folder_size_sync_nonexistent():
    # os.walk on nonexistent directory yields nothing, returns 0
    assert get_folder_size_sync("/path/to/some/nonexistent/directory/123456789") == 0
