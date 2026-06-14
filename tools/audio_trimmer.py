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

    duration = None
    if end_time:
        cmd.extend(["-to", end_time])
        try:
            # Parse duration from start/end times if possible
            def to_secs(t):
                if ":" in t:
                    parts = t.split(":")
                    if len(parts) == 3: return float(parts[0])*3600 + float(parts[1])*60 + float(parts[2])
                    elif len(parts) == 2: return float(parts[0])*60 + float(parts[1])
                return float(t)
            duration = to_secs(end_time) - to_secs(start_time)
            if duration <= 0: duration = None
        except Exception:
            pass

    cmd.extend(["-c", "copy", output_path])
    
    success_msg = f"Successfully trimmed audio: {output_path}"
    async for res in run_ffmpeg_with_progress(cmd, duration=duration, success_msg=success_msg):
        yield res
