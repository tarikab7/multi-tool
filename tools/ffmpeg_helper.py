import asyncio
import subprocess
import re
from typing import AsyncGenerator, Dict, Any

async def get_media_duration(filepath: str) -> float:
    """Asynchronously retrieve the duration of a media file in seconds using ffprobe."""
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

async def run_ffmpeg_with_progress(
    cmd: list[str],
    duration: float = 0.0,
    success_message: str = "FFmpeg process completed successfully."
) -> AsyncGenerator[Dict[str, Any], None]:
    """Run FFmpeg command, parse stderr for progress, and yield progress events."""

    # FFmpeg time=HH:MM:SS.ms pattern or time=HH:MM:SS.ms pattern with spaces, also time= can be decimal seconds
    time_pattern = re.compile(r"time=\s*(\d{2}):(\d{2}):(\d{2}\.\d+)")

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=subprocess.DEVNULL, # Set to devnull to prevent pipe deadlocks
        stderr=subprocess.PIPE
    )

    last_error_line = ""

    try:
        if proc.stderr:
            while True:
                try:
                    # ffmpeg uses carriage returns (\r) to update progress on the same line
                    line_bytes = await proc.stderr.readuntil(b'\r')
                    line = line_bytes.decode('utf-8', errors='replace').strip()
                    # print("DEBUG:", line) # For local debugging if needed

                    if line:
                        last_error_line = line

                        if duration > 0.0:
                            match = time_pattern.search(line)
                            if match:
                                hours = float(match.group(1))
                                minutes = float(match.group(2))
                                seconds = float(match.group(3))
                                elapsed_seconds = hours * 3600 + minutes * 60 + seconds

                                percent = min(100.0, (elapsed_seconds / duration) * 100)
                                yield {"type": "progress", "progress": round(percent, 2)}

                except asyncio.exceptions.IncompleteReadError as e:
                    # End of stream
                    if e.partial:
                        last_error_line = e.partial.decode('utf-8', errors='replace').strip()
                        if duration > 0.0:
                            match = time_pattern.search(last_error_line)
                            if match:
                                hours = float(match.group(1))
                                minutes = float(match.group(2))
                                seconds = float(match.group(3))
                                elapsed_seconds = hours * 3600 + minutes * 60 + seconds

                                percent = min(100.0, (elapsed_seconds / duration) * 100)
                                yield {"type": "progress", "progress": round(percent, 2)}
                    break
                except asyncio.exceptions.LimitOverrunError:
                    # Line too long, just read and discard some to recover
                    await proc.stderr.read(1024)

        await proc.wait()

        if proc.returncode == 0:
            if success_message is not None:
                yield {"type": "success", "message": success_message}
        else:
            yield {"type": "error", "message": f"FFmpeg failed: {last_error_line}"}

    except Exception as e:
        yield {"type": "error", "message": f"Error running FFmpeg: {str(e)}"}
    finally:
        if proc.returncode is None:
            proc.kill()
            await proc.wait()
