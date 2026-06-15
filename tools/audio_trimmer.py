import os
import subprocess
import asyncio
from .ffmpeg_helper import run_ffmpeg_with_progress

async def run(params: dict):
    audio_path = params.get("audio_path", "").strip()
    start_time = params.get("start_time", "00:00:00").strip()
    end_time = params.get("end_time", "").strip()
    output_path = params.get("output_path", "").strip()
    
    if not audio_path or not os.path.exists(audio_path):
        yield {"type": "error", "message": "Valid audio path is required."}
        return
        
    if not output_path:
        base, ext = os.path.splitext(audio_path)
        output_path = f"{base}_trimmed{ext}"
        
    yield {"type": "log", "message": f"Trimming {audio_path} starting from {start_time}..."}
    
    # Construct FFmpeg command
    cmd = ["ffmpeg", "-y", "-i", audio_path, "-ss", start_time]
    if end_time:
        cmd.extend(["-to", end_time])
    cmd.extend(["-c", "copy", output_path])
    
    try:
        returncode = -1
        stderr = ""
        async for event in run_ffmpeg_with_progress(cmd):
            if event["type"] == "_result":
                returncode = event["returncode"]
                stderr = event["stderr"]
            else:
                yield event

        if returncode == 0:
            yield {"type": "success", "message": f"Successfully trimmed audio: {output_path}"}
        else:
            yield {"type": "error", "message": f"FFmpeg failed: {stderr}"}
    except asyncio.CancelledError:
        raise
    except Exception as e:
        yield {"type": "error", "message": f"Error running FFmpeg: {str(e)}"}
