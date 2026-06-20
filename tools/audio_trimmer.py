import os
import asyncio
from datetime import datetime
from tools.ffmpeg_helper import run_ffmpeg_with_progress, get_media_duration

def time_to_seconds(time_str):
    try:
        if ":" in time_str:
            t = datetime.strptime(time_str, "%H:%M:%S")
            return t.hour * 3600 + t.minute * 60 + t.second
        else:
            return float(time_str)
    except ValueError:
        return 0

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
    start_sec = time_to_seconds(start_time)
    duration = 0.0
    if end_time:
        duration = time_to_seconds(end_time) - start_sec
    else:
        total_duration = await get_media_duration(audio_path)
        if total_duration > 0:
            duration = total_duration - start_sec

    # Construct FFmpeg command
    cmd = ["ffmpeg", "-y", "-i", audio_path, "-ss", start_time]
    if end_time:
        cmd.extend(["-to", end_time])
    cmd.extend(["-c", "copy", output_path])
    
    success_msg = f"Successfully trimmed audio: {output_path}"
    async for event in run_ffmpeg_with_progress(cmd, duration=duration, success_message=success_msg):
        yield event
