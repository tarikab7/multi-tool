import pytest
import os
from tools.gif_tool import run

@pytest.mark.asyncio
async def test_gif_tool_missing_input():
    gen = run({})
    events = [event async for event in gen]
    dicts = [e.to_dict() if hasattr(e, 'to_dict') else e for e in events]

    assert len(dicts) == 1
    assert dicts[0]["type"] == "error"
    assert "required" in dicts[0]["message"]

@pytest.mark.asyncio
async def test_gif_tool_create_success(tmp_path, mocker):
    input_vid = tmp_path / "vid.mp4"
    input_vid.write_text("dummy")
    output_gif = tmp_path / "out.gif"

    mock_proc = mocker.MagicMock()
    mock_proc.returncode = 0
    # Simulate communicate() returning stdout, stderr
    mock_proc.communicate = mocker.AsyncMock(return_value=(b"", b""))
    mocker.patch('asyncio.create_subprocess_exec', return_value=mock_proc)

    gen = run({
        "mode": "create",
        "input_path": str(input_vid),
        "output_path": str(output_gif)
    })

    events = [event async for event in gen]
    dicts = [e.to_dict() if hasattr(e, 'to_dict') else e for e in events]

    assert dicts[0]["type"] == "log"
    assert dicts[1]["type"] == "progress"
    assert dicts[1]["percent"] == 100.0
    assert dicts[2]["type"] == "log"
    assert dicts[3]["type"] == "success"
    assert dicts[3]["message"] == "Successfully created GIF."

@pytest.mark.asyncio
async def test_gif_tool_extract_success(tmp_path, mocker):
    input_vid = tmp_path / "vid.mp4"
    input_vid.write_text("dummy")
    output_dir = tmp_path / "frames"
    output_dir.mkdir()

    mock_proc = mocker.MagicMock()
    mock_proc.returncode = 0
    # Simulate communicate() returning stdout, stderr
    mock_proc.communicate = mocker.AsyncMock(return_value=(b"", b""))
    mocker.patch('asyncio.create_subprocess_exec', return_value=mock_proc)

    gen = run({
        "mode": "extract",
        "input_path": str(input_vid),
        "output_path": str(output_dir)
    })

    events = [event async for event in gen]
    dicts = [e.to_dict() if hasattr(e, 'to_dict') else e for e in events]

    assert dicts[0]["type"] == "log"
    assert dicts[1]["type"] == "progress"
    assert dicts[1]["percent"] == 100.0
    assert dicts[2]["type"] == "log"
    assert dicts[3]["type"] == "success"
    assert dicts[3]["message"] == "Successfully extracted 0 frames."
