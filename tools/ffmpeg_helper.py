import asyncio
import re
import subprocess
from typing import AsyncGenerator

async def get_media_duration(filepath: str) -> float:
    cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", filepath
    ]
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, _ = await proc.communicate()
    try:
        return float(stdout.decode().strip())
    except ValueError:
        return 0.0

def parse_time_to_seconds(time_str: str) -> float:
    time_str = time_str.strip()
    if not time_str:
        return 0.0
    if ':' in time_str:
        parts = time_str.split(':')
        if len(parts) == 3:
            h, m, s = parts
            return float(h) * 3600 + float(m) * 60 + float(s)
        elif len(parts) == 2:
            m, s = parts
            return float(m) * 60 + float(s)
    try:
        return float(time_str)
    except ValueError:
        return 0.0

async def run_ffmpeg_with_progress(cmd: list, duration: float) -> AsyncGenerator[dict, None]:
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE
    )

    time_regex = re.compile(r"time=\s*([0-9:.]+)")
    last_error_line = ""

    try:
        while True:
            try:
                line_bytes = await proc.stderr.readuntil(b'\r')
            except asyncio.exceptions.IncompleteReadError as e:
                line_bytes = e.partial
            except asyncio.exceptions.LimitOverrunError:
                line_bytes = await proc.stderr.read(4096)

            if not line_bytes:
                break

            line = line_bytes.decode('utf-8', errors='replace').strip()
            if line:
                last_error_line = line
                match = time_regex.search(line)
                if match:
                    time_str = match.group(1)
                    elapsed = parse_time_to_seconds(time_str)
                    if duration > 0:
                        percent = min(100.0, (elapsed / duration) * 100)
                        yield {"type": "progress", "progress": percent}

        await proc.wait()
        if proc.returncode != 0:
            yield {"type": "error", "message": f"FFmpeg failed: {last_error_line}"}
    finally:
        if proc.returncode is None:
            try:
                proc.kill()
            except OSError:
                pass
            await proc.wait()
