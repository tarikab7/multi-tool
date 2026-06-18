import asyncio
import subprocess
import re

async def get_media_duration(filepath: str) -> float:
    """Gets the duration of a media file in seconds using ffprobe."""
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        filepath
    ]
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode == 0:
            return float(stdout.decode().strip())
    except Exception:
        pass
    return 0.0

async def run_ffmpeg_with_progress(cmd: list, duration: float, success_message: str):
    """
    Executes an FFmpeg command and yields progress updates by parsing stderr.
    """
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE
        )
    except Exception as e:
        yield {"type": "error", "message": f"Failed to start FFmpeg: {str(e)}"}
        return

    time_pattern = re.compile(r"time=(\d+):(\d+):(\d+\.\d+)")
    last_error_line = ""

    try:
        while True:
            try:
                line = await proc.stderr.readuntil(b'\r')
            except asyncio.exceptions.IncompleteReadError as e:
                line = e.partial
            except asyncio.exceptions.LimitOverrunError:
                line = await proc.stderr.read(4096)
                continue

            if not line:
                break

            try:
                decoded_line = line.decode('utf-8', errors='ignore')
                last_error_line = decoded_line.strip()
            except Exception:
                continue

            match = time_pattern.search(decoded_line)
            if match and duration > 0:
                hours = float(match.group(1))
                minutes = float(match.group(2))
                seconds = float(match.group(3))

                elapsed = (hours * 3600) + (minutes * 60) + seconds
                progress = min(100.0, (elapsed / duration) * 100)
                yield {"type": "progress", "progress": progress}

        await proc.wait()

        if proc.returncode == 0:
            yield {"type": "success", "message": success_message}
        else:
            yield {"type": "error", "message": f"FFmpeg failed: {last_error_line}"}

    except asyncio.CancelledError:
        try:
            proc.kill()
        except OSError:
            pass
        await proc.wait()
        raise
