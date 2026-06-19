import os
import subprocess
import asyncio
from tools.ffmpeg_helper import get_media_duration, parse_time_to_seconds, run_ffmpeg_with_progress

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
    
    # Calculate duration
    start_s = parse_time_to_seconds(start_time)
    if end_time:
        target_duration = parse_time_to_seconds(end_time) - start_s
    else:
        full_duration = await get_media_duration(audio_path)
        if full_duration:
            target_duration = full_duration - start_s
        else:
            target_duration = 0

    # Construct FFmpeg command
    cmd = ["ffmpeg", "-y", "-i", audio_path, "-ss", start_time]
    if end_time:
        cmd.extend(["-to", end_time])
    cmd.extend(["-c", "copy", output_path])
    
    async for event in run_ffmpeg_with_progress(cmd, target_duration, f"Successfully trimmed audio: {output_path}"):
        yield event
