import os
import pytest
from tools.markdown_converter import run

@pytest.mark.asyncio
async def test_markdown_converter_missing_inputs():
    
    results = [res async for res in run({"output_path": "out.html"})]
    assert len(results) == 1
    assert results[0]["type"] == "error"
    assert "Both input and output paths are required." in results[0]["message"]

    
    results = [res async for res in run({"input_path": "in.md"})]
    assert len(results) == 1
    assert results[0]["type"] == "error"
    assert "Both input and output paths are required." in results[0]["message"]

@pytest.mark.asyncio
async def test_markdown_converter_invalid_input():
    results = [res async for res in run({"input_path": "non_existent.md", "output_path": "out.html"})]
    assert len(results) == 1
    assert results[0]["type"] == "error"
    assert "not found" in results[0]["message"]

@pytest.mark.asyncio
async def test_markdown_converter_happy_path(tmp_path):
    input_md = tmp_path / "test.md"
    input_md.write_text("# Hello World\n\nThis is a **test**.", encoding="utf-8")

    output_html = tmp_path / "output.html"

    results = [res async for res in run({
        "input_path": str(input_md),
        "output_path": str(output_html)
    })]

    assert len(results) == 4
    assert results[0]["type"] == "log"
    assert "Compiling markdown" in results[0]["message"]

    assert results[1]["type"] == "progress"
    assert results[1]["percent"] == 100.0

    assert results[2]["type"] == "log"
    assert "Styled HTML document saved" in results[2]["message"]

    assert results[3]["type"] == "success"
    assert "Markdown converted successfully" in results[3]["message"]

    assert output_html.exists()
    content = output_html.read_text(encoding="utf-8")
    assert "<h1>Hello World</h1>" in content
    assert "<strong>test</strong>" in content
    assert "<!DOCTYPE html>" in content
