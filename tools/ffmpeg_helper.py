import asyncio
import re

async def run_ffmpeg_with_progress(cmd: list, success_message: str):
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    duration = None
    duration_re = re.compile(r"Duration:\s*(\d{2}):(\d{2}):(\d{2}\.\d+)")
    time_re = re.compile(r"time=\s*(\d{2}):(\d{2}):(\d{2}\.\d+)")

    stderr_output = []
    try:
        while True:
            line = await proc.stderr.readline()
            if not line:
                break
            line_str = line.decode('utf-8', errors='replace')
            stderr_output.append(line_str)

            if duration is None:
                match = duration_re.search(line_str)
                if match:
                    h, m, s = match.groups()
                    duration = int(h) * 3600 + int(m) * 60 + float(s)

            if duration:
                match = time_re.search(line_str)
                if match:
                    h, m, s = match.groups()
                    elapsed = int(h) * 3600 + int(m) * 60 + float(s)
                    percent = min(100.0, (elapsed / duration) * 100)
                    yield {"type": "progress", "percent": percent, "message": f"Processing... {percent:.1f}%"}

        await proc.wait()
        if proc.returncode == 0:
            yield {"type": "success", "message": success_message}
        else:
            yield {"type": "error", "message": f"FFmpeg failed: {''.join(stderr_output[-5:])}"}
    except asyncio.CancelledError:
        try:
            proc.kill()
        except OSError:
            pass
        yield {"type": "error", "message": "Task cancelled"}
        raise
