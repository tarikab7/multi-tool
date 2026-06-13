import pytest
import os
from tools.broken_symlinks import run

@pytest.mark.asyncio
async def test_broken_symlinks_empty_path():
    params = {"dir_path": ""}
    results = [res async for res in run(params)]
    assert len(results) == 1
    assert results[0]["type"] == "error"
    assert results[0]["message"] == "Valid scanning directory is required."

@pytest.mark.asyncio
async def test_broken_symlinks_missing_dir_path():
    params = {}
    results = [res async for res in run(params)]
    assert len(results) == 1
    assert results[0]["type"] == "error"
    assert results[0]["message"] == "Valid scanning directory is required."

@pytest.mark.asyncio
async def test_broken_symlinks_invalid_path():
    params = {"dir_path": "/path/that/definitely/does/not/exist/12345"}
    results = [res async for res in run(params)]
    assert len(results) == 1
    assert results[0]["type"] == "error"
    assert results[0]["message"] == "Valid scanning directory is required."

@pytest.mark.asyncio
async def test_broken_symlinks_path_is_file(tmp_path):
    file_path = tmp_path / "test_file.txt"
    file_path.write_text("hello")
    params = {"dir_path": str(file_path)}
    results = [res async for res in run(params)]
    assert len(results) == 1
    assert results[0]["type"] == "error"
    assert results[0]["message"] == "Valid scanning directory is required."
