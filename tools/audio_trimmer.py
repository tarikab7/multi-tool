import os
import subprocess
import asyncio
from tools.utils import yield_log, yield_error, yield_success

async def run(params: dict):
    audio_path = params.get("audio_path", "").strip()
    start_time = params.get("start_time", "00:00:00").strip()
    end_time = params.get("end_time", "").strip()
    output_path = params.get("output_path", "").strip()
    
    if not audio_path or not os.path.exists(audio_path):
        yield yield_error("Valid audio path is required.")
        return
        
    if not output_path:
        base, ext = os.path.splitext(audio_path)
        output_path = f"{base}_trimmed{ext}"
        
    yield yield_log(f"Trimming {audio_path} starting from {start_time}...")
    
    # Construct FFmpeg command
    cmd = ["ffmpeg", "-y", "-i", audio_path, "-ss", start_time]
    if end_time:
        cmd.extend(["-to", end_time])
    cmd.extend(["-c", "copy", output_path])
    
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode == 0:
            yield yield_success(f"Successfully trimmed audio: {output_path}")
        else:
            yield yield_error(f"FFmpeg failed: {stderr.decode()}")
    except Exception as e:
        yield yield_error(f"Error running FFmpeg: {str(e)}")
