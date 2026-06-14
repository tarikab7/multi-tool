import asyncio
import re
import subprocess

async def run_ffmpeg_with_progress(cmd: list, duration: float = None, success_msg: str = "FFmpeg completed successfully."):
    """
    Runs an FFmpeg command as an async subprocess, parsing its stderr for progress updates.
    Yields progress dicts (type='progress') and handles cleanup on cancellation.
    Returns success or error dicts at the end.
    """
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
    except Exception as e:
        yield {"type": "error", "message": f"Failed to start FFmpeg: {str(e)}"}
        return

    time_regex = re.compile(r"time=(\d+):(\d+):(\d+\.\d+)")
    duration_regex = re.compile(r"Duration:\s+(\d+):(\d+):(\d+\.\d+)")

    stderr_output = bytearray()
    line_buf = ""

    try:
        while True:
            # Read byte by byte to handle \r without blocking
            char = await proc.stderr.read(1)
            if not char:
                break

            stderr_output.extend(char)
            char_str = char.decode(errors='replace')

            if char_str in ('\r', '\n'):
                if line_buf:
                    if not duration:
                        match = duration_regex.search(line_buf)
                        if match:
                            h, m, s = match.groups()
                            duration = float(h) * 3600 + float(m) * 60 + float(s)

                    match = time_regex.search(line_buf)
                    if match:
                        h, m, s = match.groups()
                        elapsed = float(h) * 3600 + float(m) * 60 + float(s)
                        if duration and duration > 0:
                            progress = min(100.0, (elapsed / duration) * 100)
                            yield {"type": "progress", "message": f"{progress:.2f}%"}
                    line_buf = ""
            else:
                line_buf += char_str

        await proc.wait()

        if proc.returncode == 0:
            yield {"type": "success", "message": success_msg}
        else:
            stderr_str = stderr_output.decode(errors='replace')
            yield {"type": "error", "message": f"FFmpeg failed: {stderr_str}"}

    except asyncio.CancelledError:
        proc.terminate()
        try:
            await asyncio.wait_for(proc.wait(), timeout=5.0)
        except asyncio.TimeoutError:
            proc.kill()
        raise
    except Exception as e:
        yield {"type": "error", "message": f"Error running FFmpeg: {str(e)}"}
