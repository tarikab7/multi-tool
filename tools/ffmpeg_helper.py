import asyncio
import subprocess
import re

async def get_media_duration(file_path: str) -> float | None:
    """
    Asynchronously retrieve media duration using ffprobe.
    """
    cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", file_path
    ]
    try:
        proc = await asyncio.create_subprocess_exec(*cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = await proc.communicate()
        if proc.returncode == 0:
            return float(stdout.decode().strip())
    except Exception:
        pass
    return None

def parse_time_to_seconds(time_str: str) -> float:
    """
    Parse HH:MM:SS.ms string to float seconds.
    """
    parts = time_str.split(":")
    if len(parts) == 3:
        h, m, s = parts
        return float(h) * 3600 + float(m) * 60 + float(s)
    elif len(parts) == 2:
        m, s = parts
        return float(m) * 60 + float(s)
    elif len(parts) == 1:
        return float(parts[0])
    return 0.0

async def run_ffmpeg_with_progress(cmd: list[str], total_duration: float, success_msg: str):
    """
    Async generator to run FFmpeg, track progress, and yield events.
    """
    proc = None
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE
        )

        last_progress = -1
        last_error_line = ""

        while True:
            try:
                line = await proc.stderr.readuntil(b'\r')
                if not line:
                    break
                decoded_line = line.decode('utf-8', errors='replace').strip()
                last_error_line = decoded_line

                # Parse time=HH:MM:SS.ms
                match = re.search(r"time=(\d{2}:\d{2}:\d{2}\.\d{2})", decoded_line)
                if match and total_duration > 0:
                    elapsed_time = parse_time_to_seconds(match.group(1))
                    percentage = min(100.0, (elapsed_time / total_duration) * 100)

                    if int(percentage) > last_progress:
                        last_progress = int(percentage)
                        yield {"type": "log", "message": f"Progress: {percentage:.1f}%"}
            except asyncio.exceptions.IncompleteReadError as e:
                # Reached end of stream, no trailing \r
                if e.partial:
                    last_error_line = e.partial.decode('utf-8', errors='replace').strip()
                break
            except asyncio.exceptions.LimitOverrunError:
                # Line too long, just read next chunk
                chunk = await proc.stderr.read(4096)
                if not chunk:
                    break

        # Wait for the process to fully exit
        await proc.wait()

        if proc.returncode == 0:
            yield {"type": "success", "message": success_msg}
        else:
            yield {"type": "error", "message": f"FFmpeg failed: {last_error_line}"}
    except asyncio.CancelledError:
        # Expected cancellation, cleanup handled in finally
        raise
    except Exception as e:
        yield {"type": "error", "message": f"Error running FFmpeg: {str(e)}"}
    finally:
        if proc and proc.returncode is None:
            try:
                proc.kill()
                await proc.wait()
            except Exception:
                pass
