import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from tools.ffmpeg_helper import run_ffmpeg_with_progress
from tools import audio_trimmer, video_to_audio, video_stabilizer
import os

@pytest.mark.asyncio
async def test_ffmpeg_helper_success():
    cmd = ["ffmpeg", "-i", "in.mp4", "out.mp4"]

    mock_proc = AsyncMock()
    mock_proc.returncode = 0

    # Simulate a stream of chars
    # We'll simulate: Duration: 00:00:10.00 \r time=00:00:05.00 \r
    stream_chars = [
        *list(b"Duration: 00:00:10.00\r"),
        *list(b"time=00:00:05.00\r")
    ]

    async def mock_read(n):
        if stream_chars:
            return bytes([stream_chars.pop(0)])
        return b""

    mock_proc.stderr.read.side_effect = mock_read
    mock_proc.wait = AsyncMock()

    with patch("asyncio.create_subprocess_exec", return_value=mock_proc) as mock_exec:
        results = [res async for res in run_ffmpeg_with_progress(cmd)]

        mock_exec.assert_called_once_with(*cmd, stdout=-1, stderr=-1) # subprocess.PIPE is -1

        progress_res = [r for r in results if r["type"] == "progress"]
        assert len(progress_res) == 1
        assert progress_res[0]["message"] == "50.00%"

        success_res = [r for r in results if r["type"] == "success"]
        assert len(success_res) == 1
        assert success_res[0]["message"] == "FFmpeg completed successfully."

@pytest.mark.asyncio
async def test_ffmpeg_helper_cancellation():
    cmd = ["ffmpeg", "-i", "in.mp4", "out.mp4"]

    mock_proc = AsyncMock()
    mock_proc.returncode = 0
    mock_proc.terminate = MagicMock()

    async def mock_read(n):
        await asyncio.sleep(1) # Block to simulate running
        return b""

    mock_proc.stderr.read.side_effect = mock_read

    async def mock_wait():
        return
    mock_proc.wait = AsyncMock(side_effect=mock_wait)

    with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
        task = asyncio.create_task(anext(run_ffmpeg_with_progress(cmd)))
        await asyncio.sleep(0.01)
        task.cancel()

        with pytest.raises(asyncio.CancelledError):
            await task

        mock_proc.terminate.assert_called_once()

@pytest.mark.asyncio
async def test_audio_trimmer():
    params = {
        "audio_path": "dummy.mp3",
        "start_time": "00:00:01",
        "end_time": "00:00:11"
    }

    # Mock os.path.exists to True
    with patch("os.path.exists", return_value=True), \
         patch("tools.audio_trimmer.run_ffmpeg_with_progress") as mock_helper:

        async def mock_helper_gen(*args, **kwargs):
            yield {"type": "progress", "message": "50.00%"}
            yield {"type": "success", "message": "Done"}

        mock_helper.side_effect = mock_helper_gen

        results = [res async for res in audio_trimmer.run(params)]

        # Verify call args
        mock_helper.assert_called_once()
        args, kwargs = mock_helper.call_args
        assert kwargs["duration"] == 10.0

        progress = [r for r in results if r["type"] == "progress"]
        assert len(progress) == 1

@pytest.mark.asyncio
async def test_video_to_audio():
    params = {
        "video_path": "dummy.mp4",
        "format_type": "mp3"
    }

    with patch("os.path.exists", return_value=True), \
         patch("tools.video_to_audio.run_ffmpeg_with_progress") as mock_helper:

        async def mock_helper_gen(*args, **kwargs):
            yield {"type": "progress", "message": "50.00%"}
            yield {"type": "success", "message": "Done"}

        mock_helper.side_effect = mock_helper_gen

        results = [res async for res in video_to_audio.run(params)]

        mock_helper.assert_called_once()
        args, kwargs = mock_helper.call_args
        assert kwargs["duration"] is None

        progress = [r for r in results if r["type"] == "progress"]
        assert len(progress) == 1

@pytest.mark.asyncio
async def test_video_stabilizer():
    params = {
        "video_path": "dummy.mp4"
    }

    with patch("os.path.exists", return_value=True), \
         patch("tools.video_stabilizer.run_ffmpeg_with_progress") as mock_helper, \
         patch("os.remove"):

        async def mock_helper_gen(*args, **kwargs):
            yield {"type": "progress", "message": "50.00%"}
            yield {"type": "success", "message": "Done"}

        mock_helper.side_effect = mock_helper_gen

        results = [res async for res in video_stabilizer.run(params)]

        assert mock_helper.call_count == 2

        progress = [r for r in results if r["type"] == "progress"]
        assert len(progress) == 2
        assert progress[0]["message"] == "[Pass 1] 50.00%"
        assert progress[1]["message"] == "[Pass 2] 50.00%"
