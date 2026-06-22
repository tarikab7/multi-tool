import os
import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from tools.thumbnail_sheet import get_video_duration, extract_frame_sync, create_sheet_sync, run

@pytest.mark.asyncio
async def test_get_video_duration_success():
    with patch("asyncio.create_subprocess_exec") as mock_exec:
        mock_proc = AsyncMock()
        mock_proc.communicate.return_value = (b"12.34\n", b"")
        mock_exec.return_value = mock_proc

        duration = await get_video_duration("dummy.mp4")
        assert duration == 12.34
        mock_exec.assert_called_once()

@pytest.mark.asyncio
async def test_get_video_duration_failure():
    with patch("asyncio.create_subprocess_exec", side_effect=Exception("Failed")):
        duration = await get_video_duration("dummy.mp4")
        assert duration == 0.0

def test_extract_frame_sync_success():
    with patch("subprocess.run") as mock_run:
        with patch("os.path.exists", return_value=True):
            res = extract_frame_sync("dummy.mp4", 5.0, "out.jpg")
            assert res is True
            mock_run.assert_called_once()
            args = mock_run.call_args[0][0]
            assert "ffmpeg" in args
            assert "5.0" in args

def test_create_sheet_sync_empty_frames():
    assert create_sheet_sync([], 2, 2, "out.jpg", "vid.mp4") is False

def test_create_sheet_sync_success():
    mock_image = MagicMock()
    mock_image.size = (1920, 1080)
    mock_image.resize.return_value = mock_image

    mock_image_class = MagicMock()
    mock_image_class.open.return_value.__enter__.return_value = mock_image
    mock_image_class.open.return_value = mock_image
    mock_image_class.new.return_value = mock_image

    with patch("tools.thumbnail_sheet.Image", mock_image_class):
        with patch("tools.thumbnail_sheet.ImageDraw"):
            res = create_sheet_sync(["frame1.jpg", "frame2.jpg"], 2, 1, "out.jpg", "vid.mp4")
            assert res is True
            mock_image.save.assert_called_once()

@pytest.mark.asyncio
async def test_run_missing_params():
    params = {}
    gen = run(params)
    res = await anext(gen)
    assert res["type"] == "error"
    assert "required" in res["message"]

@pytest.mark.asyncio
async def test_run_video_not_found():
    params = {"video_path": "missing.mp4", "output_path": "out.jpg"}
    with patch("os.path.isfile", return_value=False):
        gen = run(params)
        res = await anext(gen)
        assert res["type"] == "error"
        assert "not found" in res["message"]

@pytest.mark.asyncio
async def test_run_invalid_dimensions():
    params = {"video_path": "vid.mp4", "output_path": "out.jpg", "cols": "a", "rows": "2"}
    with patch("os.path.isfile", return_value=True):
        gen = run(params)
        res = await anext(gen)
        assert res["type"] == "error"
        assert "integers" in res["message"]

@pytest.mark.asyncio
async def test_run_invalid_duration():
    params = {"video_path": "vid.mp4", "output_path": "out.jpg", "cols": "2", "rows": "2"}
    with patch("os.path.isfile", return_value=True):
        with patch("tools.thumbnail_sheet.get_video_duration", return_value=0.0):
            gen = run(params)
            res1 = await anext(gen)
            assert res1["type"] == "log"
            res2 = await anext(gen)
            assert res2["type"] == "error"
            assert "duration" in res2["message"]

@pytest.mark.asyncio
async def test_run_success():
    params = {"video_path": "vid.mp4", "output_path": "out.jpg", "cols": "2", "rows": "2"}
    with patch("os.path.isfile", return_value=True):
        with patch("tools.thumbnail_sheet.get_video_duration", return_value=10.0):
            with patch("tools.thumbnail_sheet.extract_frame_sync", return_value=True):
                with patch("tools.thumbnail_sheet.create_sheet_sync", return_value=True):
                    gen = run(params)
                    events = [e async for e in gen]

                    types = [e["type"] for e in events]
                    assert "success" in types
                    assert events[-1]["type"] == "success"
