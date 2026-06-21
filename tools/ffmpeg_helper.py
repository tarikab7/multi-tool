import os
import subprocess
import asyncio
import re

async def get_media_duration(file_path: str) -> float:
    """
    Asynchronously get media duration in seconds using ffprobe.
    """
    cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", file_path
    ]
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode == 0:
            return float(stdout.decode().strip())
    except Exception:
        pass
    return 0.0

def parse_time_to_seconds(time_str: str) -> float:
    """
    Parse a time string (HH:MM:SS or HH:MM:SS.ms) into seconds.
    If it's already a raw float/int string, parse it directly.
    """
    time_str = time_str.strip()
    if not time_str:
        return 0.0
    if ':' in time_str:
        parts = time_str.split(':')
        seconds = 0.0
        multiplier = 1
        for part in reversed(parts):
            seconds += float(part) * multiplier
            multiplier *= 60
        return seconds
    try:
        return float(time_str)
    except ValueError:
        return 0.0

async def run_ffmpeg_with_progress(cmd: list, duration: float, success_message: str):
    """
    Run an FFmpeg command and yield progress updates.
    """
    proc = None
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        time_pattern = re.compile(r"time=\s*(\d+:\d+:\d+\.?\d*)")

        # Continuously buffer the latest decoded line
        last_line = ""

        while True:
            try:
                # readuntil(b'\r') might read multiple lines if stderr uses \n, but ffmpeg usually uses \r
                # Just to be safe we'll use read(1024) and split if it hangs
                # But readuntil(b'\r') is what was required by memory
                line_bytes = await proc.stderr.readuntil(b'\r')
                line = line_bytes.decode(errors='replace').strip()
                if line:
                    last_line = line
            except asyncio.exceptions.IncompleteReadError as e:
                # e.partial contains the unread bytes
                if e.partial:
                    line = e.partial.decode(errors='replace').strip()
                    if line:
                        last_line = line
                        match = time_pattern.search(line)
                        if match and duration > 0:
                            current_time_str = match.group(1)
                            current_time = parse_time_to_seconds(current_time_str)
                            percentage = min(100.0, (current_time / duration) * 100)
                            yield {"type": "progress", "percentage": percentage}
                break
            except asyncio.exceptions.LimitOverrunError:
                # Skip overlong lines if any
                line_bytes = await proc.stderr.read(4096)
                continue

            match = time_pattern.search(line)
            if match and duration > 0:
                current_time_str = match.group(1)
                current_time = parse_time_to_seconds(current_time_str)
                percentage = min(100.0, (current_time / duration) * 100)
                yield {"type": "progress", "percentage": percentage}

        await proc.wait()

        if proc.returncode == 0:
            if success_message is not None:
                yield {"type": "success", "message": success_message}
        else:
            yield {"type": "error", "message": f"FFmpeg failed: {last_line}"}

    except Exception as e:
        yield {"type": "error", "message": f"Error running FFmpeg: {str(e)}"}
    finally:
        if proc is not None and proc.returncode is None:
            try:
                proc.kill()
            except ProcessLookupError:
                pass
            await proc.wait()
