import pytest
from unittest.mock import patch, MagicMock
from tools.gif_tool import run

@pytest.fixture
def mock_subprocess():
    with patch("asyncio.create_subprocess_exec") as mock_exec:
        # Create a mock process
        process_mock = MagicMock()
        process_mock.returncode = 0

        # Async mock for communicate
        async def mock_communicate():
            return b"stdout", b"stderr"

        process_mock.communicate = mock_communicate

        # Async mock for create_subprocess_exec
        async def async_mock_exec(*args, **kwargs):
            return process_mock

        mock_exec.side_effect = async_mock_exec
        yield mock_exec

@pytest.mark.asyncio
async def test_gif_tool_missing_input_path():
    params = {}
    results = [res async for res in run(params)]

    assert len(results) == 1
    assert results[0] == {"type": "error", "message": "Input file path is required."}

@pytest.mark.asyncio
@patch("os.path.isfile")
async def test_gif_tool_input_file_not_found(mock_isfile):
    mock_isfile.return_value = False

    params = {"input_path": "/fake/path/vid.mp4"}
    results = [res async for res in run(params)]

    assert len(results) == 1
    assert results[0] == {"type": "error", "message": "Input file '/fake/path/vid.mp4' not found."}

@pytest.mark.asyncio
@patch("os.path.isfile")
async def test_gif_tool_create_missing_gif_extension(mock_isfile):
    mock_isfile.return_value = True

    params = {
        "input_path": "/fake/path/vid.mp4",
        "output_path": "/fake/path/output.mp4" # Wrong extension
    }
    results = [res async for res in run(params)]

    assert len(results) == 1
    assert results[0] == {"type": "error", "message": "Output path must end with '.gif'."}

@pytest.mark.asyncio
@patch("os.path.isfile")
@patch("os.makedirs")
async def test_gif_tool_create_success(mock_makedirs, mock_isfile, mock_subprocess):
    mock_isfile.return_value = True

    params = {
        "input_path": "/fake/path/vid.mp4",
        "output_path": "/fake/path/output.gif",
        "fps": "15",
        "width": "640"
    }

    results = [res async for res in run(params)]

    # Check outputs
    assert len(results) == 4
    assert results[0] == {"type": "log", "message": "Generating high-quality GIF with custom color palette..."}
    assert results[1] == {"type": "progress", "percent": 100.0}
    assert results[2] == {"type": "log", "message": "Saved GIF to: /fake/path/output.gif"}
    assert results[3] == {"type": "success", "message": "Successfully created GIF."}

    # Check if subprocess was called with correct command
    # filter_str = f"[0:v]fps={fps},scale={width}:-1:flags=lanczos,split[a][b];[a]palettegen[p];[b][p]paletteuse"
    expected_filter = "[0:v]fps=15,scale=640:-1:flags=lanczos,split[a][b];[a]palettegen[p];[b][p]paletteuse"
    mock_subprocess.assert_called_once_with(
        'ffmpeg', '-y', '-i', '/fake/path/vid.mp4', '-filter_complex', expected_filter, '/fake/path/output.gif',
        stdout=-1, # subprocess.PIPE
        stderr=-1
    )

@pytest.mark.asyncio
@patch("os.path.isfile")
@patch("os.makedirs")
@patch("os.listdir")
async def test_gif_tool_extract_success(mock_listdir, mock_makedirs, mock_isfile, mock_subprocess):
    mock_isfile.return_value = True
    mock_listdir.return_value = ["frame_0001.png", "frame_0002.png", "other.txt"]

    params = {
        "mode": "extract",
        "input_path": "/fake/path/vid.mp4",
        "output_path": "/fake/path/frames_dir"
    }

    results = [res async for res in run(params)]

    assert len(results) == 4
    assert results[0] == {"type": "log", "message": "Extracting frames into: /fake/path/frames_dir"}
    assert results[1] == {"type": "progress", "percent": 100.0}
    assert results[2] == {"type": "log", "message": "Extracted 2 frame(s) as PNG."}
    assert results[3] == {"type": "success", "message": "Successfully extracted 2 frames."}

    # Check if subprocess was called with correct command
    mock_subprocess.assert_called_once_with(
        'ffmpeg', '-y', '-i', '/fake/path/vid.mp4', '-vsync', '0', '/fake/path/frames_dir/frame_%04d.png',
        stdout=-1, # subprocess.PIPE
        stderr=-1
    )
