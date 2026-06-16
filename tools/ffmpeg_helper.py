import asyncio
import subprocess
import re

async def run_ffmpeg_with_progress(*cmd, expected_duration=None, start_offset=0.0):
    """
    Runs an FFmpeg command and yields progress updates by parsing stderr.

    Yields:
        {"type": "progress", "progress": float}  # 0.0 to 100.0
        {"type": "success", "message": str}
        {"type": "error", "message": str}
    """
    duration_re = re.compile(r"Duration:\s+(\d+):(\d{2}):(\d+\.\d+)")
    time_re = re.compile(r"time=\s*(\d+):(\d{2}):(\d+\.\d+)")

    total_seconds = expected_duration
    last_error_chunk = ""

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        while True:
            try:
                # FFmpeg outputs progress with carriage returns instead of newlines
                line = await proc.stderr.readuntil(b'\r')
            except asyncio.exceptions.IncompleteReadError as e:
                line = e.partial
            except asyncio.exceptions.LimitOverrunError:
                # If a line is too long, just read what we can and continue
                line = await proc.stderr.read(4096)

            if not line:
                break

            line_str = line.decode('utf-8', errors='replace')
            # Keep a buffer of the last bit of stderr for error reporting
            last_error_chunk = (last_error_chunk + line_str)[-1000:]

            # Extract duration if we don't have it yet
            if total_seconds is None:
                duration_match = duration_re.search(line_str)
                if duration_match:
                    h, m, s = duration_match.groups()
                    total_seconds = float(h) * 3600 + float(m) * 60 + float(s)
                    if start_offset > 0 and total_seconds > start_offset:
                        total_seconds -= start_offset

            # Extract current time to calculate progress
            time_match = time_re.search(line_str)
            if time_match and total_seconds and total_seconds > 0:
                h, m, s = time_match.groups()
                elapsed_seconds = float(h) * 3600 + float(m) * 60 + float(s)

                percent = min(100.0, (elapsed_seconds / total_seconds) * 100)
                yield {"type": "progress", "progress": round(percent, 2)}

        await proc.wait()

        if proc.returncode == 0:
            yield {"type": "success", "message": "FFmpeg process completed successfully."}
        else:
            yield {"type": "error", "message": f"FFmpeg failed (code {proc.returncode}): {last_error_chunk.strip()}"}

    except asyncio.CancelledError:
        # Clean up dangling FFmpeg instance on cancellation
        if 'proc' in locals() and proc.returncode is None:
            try:
                proc.terminate()
                await asyncio.wait_for(proc.wait(), timeout=5.0)
            except asyncio.TimeoutError:
                proc.kill()
        raise
    except Exception as e:
        yield {"type": "error", "message": f"Error running FFmpeg: {str(e)}"}
