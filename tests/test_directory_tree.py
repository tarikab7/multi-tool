import os
import tempfile
import asyncio
import pytest
from unittest.mock import patch

from tools.directory_tree import make_tree, run

@pytest.fixture
def temp_dir_structure():
    with tempfile.TemporaryDirectory() as temp_dir:
        
        
        
        
        
        

        a_dir = os.path.join(temp_dir, "a_dir")
        os.makedirs(a_dir)

        with open(os.path.join(a_dir, "nested_file.txt"), "w") as f:
            f.write("test")

        with open(os.path.join(temp_dir, "file1.txt"), "w") as f:
            f.write("test")

        with open(os.path.join(temp_dir, "file2.txt"), "w") as f:
            f.write("test")

        yield temp_dir

def test_make_tree_invalid_path():
    assert make_tree("/path/that/does/not/exist/12345") == []

def test_make_tree_empty_dir():
    with tempfile.TemporaryDirectory() as temp_dir:
        assert make_tree(temp_dir) == []

def test_make_tree_structure(temp_dir_structure):
    tree = make_tree(temp_dir_structure)
    
    
    
    
    
    expected = [
        "├── a_dir",
        "│   └── nested_file.txt",
        "├── file1.txt",
        "└── file2.txt"
    ]
    assert tree == expected

@pytest.mark.asyncio
async def test_run_invalid_path():
    gen = run({"dir_path": "/path/that/does/not/exist/12345"})
    result = await anext(gen)
    assert result["type"] == "error"
    assert "Valid directory path is required" in result["message"]

    with pytest.raises(StopAsyncIteration):
        await anext(gen)

@pytest.mark.asyncio
async def test_run_empty_path():
    gen = run({"dir_path": ""})
    result = await anext(gen)
    assert result["type"] == "error"

    gen = run({})
    result = await anext(gen)
    assert result["type"] == "error"

@pytest.mark.asyncio
async def test_run_valid_path(temp_dir_structure):
    gen = run({"dir_path": temp_dir_structure})
    results = [res async for res in gen]

    
    
    
    
    
    
    
    

    types = [r["type"] for r in results]
    assert types[0] == "log"
    assert "Mapping file structure" in results[0]["message"]
    assert types[-1] == "success"
    assert "Tree rendered" in results[-1]["message"]

    
    assert len(results) == 7
    messages = [r["message"] for r in results]
    assert "├── a_dir" in messages
    assert "└── file2.txt" in messages

@pytest.mark.asyncio
async def test_run_truncation():
    with tempfile.TemporaryDirectory() as temp_dir:
        
        fake_lines = [f"├── file{i}.txt" for i in range(305)]

        with patch("tools.directory_tree.make_tree", return_value=fake_lines):
            gen = run({"dir_path": temp_dir})
            results = [res async for res in gen]

            types = [r["type"] for r in results]
            messages = [r["message"] for r in results]

            assert types[-1] == "success"
            assert types[-2] == "log"
            assert "... (Truncated" in messages[-2]

            
            log_types = [t for t in types if t == "log"]
            
            assert len(log_types) == 302
