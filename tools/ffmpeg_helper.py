import asyncio
import re
import os

async def get_media_duration(filepath: str) -> float:
    """
    Returns the duration of the media file in seconds using ffprobe.
    Returns 0.0 if unable to probe.
    """
    if not os.path.exists(filepath):
        return 0.0

    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        filepath
    ]
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode == 0 and stdout:
            return float(stdout.decode().strip())
    except Exception:
        pass
    return 0.0

async def run_ffmpeg_with_progress(*args, duration_seconds: float = None):
    """
    Executes an FFmpeg command using asyncio.create_subprocess_exec.
    Yields log and progress events by parsing the stderr stream.
    If duration_seconds is provided, it yields percentage progress.
    Finally yields a success or error event.
    """
    try:
        proc = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
    except Exception as e:
        yield {"type": "error", "message": f"Failed to start FFmpeg: {e}"}
        return

    time_regex = re.compile(r"time=(\d+):(\d+):(\d+\.\d+)")
    stderr_output = []

    try:
        while True:
            try:
                line = await proc.stderr.readuntil(b'\r')
                if not line:
                    break
            except asyncio.exceptions.IncompleteReadError as e:
                line = e.partial
                if not line:
                    break
            except asyncio.exceptions.LimitOverrunError:
                line = await proc.stderr.read(4096)
                if not line:
                    break

            text = line.decode('utf-8', errors='replace')
            stderr_output.append(text)

            match = time_regex.search(text)
            if match and duration_seconds and duration_seconds > 0:
                hours, minutes, seconds = map(float, match.groups())
                elapsed_seconds = hours * 3600 + minutes * 60 + seconds
                percent = min(100.0, (elapsed_seconds / duration_seconds) * 100)
                yield {"type": "progress", "progress": percent}

        await proc.wait()

        if proc.returncode == 0:
            yield {"type": "success", "message": "FFmpeg completed successfully."}
        else:
            error_msg = "".join(stderr_output)
            yield {"type": "error", "message": f"FFmpeg failed: {error_msg}"}

    except asyncio.CancelledError:
        try:
            proc.terminate()
            await asyncio.wait_for(proc.wait(), timeout=5.0)
        except (ProcessLookupError, asyncio.TimeoutError):
            try:
                proc.kill()
            except ProcessLookupError:
                pass
        raise
