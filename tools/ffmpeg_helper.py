import asyncio
import subprocess
import re

async def run_ffmpeg_with_progress(cmd: list):
    """
    Executes an FFmpeg command asynchronously, reads its stderr in real-time,
    and yields progress events.

    Finally yields a dict containing the result:
    {"type": "_result", "returncode": returncode, "stderr": stderr_output}
    """
    duration_seconds = None
    duration_re = re.compile(r"Duration:\s*(\d{2}):(\d{2}):(\d{2})(?:\.(\d+))?")
    time_re = re.compile(r"time=\s*(\d{2}):(\d{2}):(\d{2})(?:\.(\d+))?")

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    stderr_lines = []

    try:
        while True:
            try:
                line = await proc.stderr.readuntil(b'\r')
            except asyncio.exceptions.IncompleteReadError as e:
                line = e.partial
            except asyncio.exceptions.LimitOverrunError:
                # If we hit a LimitOverrunError, read a chunk to clear the buffer
                line = await proc.stderr.read(1024)

            if not line:
                break

            line_str = line.decode('utf-8', errors='replace').strip()
            # We still want to append to stderr_lines to return full stderr,
            # but ffmpeg produces A LOT of \r lines, we only keep the last few
            # or we can keep everything and join by \n.
            stderr_lines.append(line_str)

            # Extract duration if not yet known
            if duration_seconds is None:
                duration_match = duration_re.search(line_str)
                if duration_match:
                    h, m, s = duration_match.group(1), duration_match.group(2), duration_match.group(3)
                    ms = duration_match.group(4) or "0"
                    duration_seconds = int(h) * 3600 + int(m) * 60 + int(s) + float(f"0.{ms}")

            # Extract elapsed time and compute progress
            if duration_seconds and duration_seconds > 0:
                time_match = time_re.search(line_str)
                if time_match:
                    h, m, s = time_match.group(1), time_match.group(2), time_match.group(3)
                    ms = time_match.group(4) or "0"
                    elapsed = int(h) * 3600 + int(m) * 60 + int(s) + float(f"0.{ms}")

                    percent = min(100.0, (elapsed / duration_seconds) * 100)
                    yield {"type": "progress", "progress": percent}

        await proc.wait()
    except asyncio.CancelledError:
        try:
            proc.kill()
        except ProcessLookupError:
            pass
        await proc.wait()
        raise

    yield {"type": "_result", "returncode": proc.returncode, "stderr": "".join(stderr_lines)}
