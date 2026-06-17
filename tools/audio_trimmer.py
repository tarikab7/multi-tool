import os
import subprocess
import asyncio
from tools.ffmpeg_helper import run_ffmpeg_with_progress, get_media_duration

def parse_time(t_str):
    if not t_str: return 0.0
    parts = t_str.split(':')
    if len(parts) == 3:
        return float(parts[0])*3600 + float(parts[1])*60 + float(parts[2])
    elif len(parts) == 2:
        return float(parts[0])*60 + float(parts[1])
    return float(parts[0])

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
        start_sec = parse_time(start_time)
        if end_time:
            end_sec = parse_time(end_time)
            duration_sec = max(0.0, end_sec - start_sec)
        else:
            total_duration = await get_media_duration(audio_path)
            duration_sec = max(0.0, total_duration - start_sec)

        async for event in run_ffmpeg_with_progress(*cmd, duration_seconds=duration_sec):
            if event["type"] == "success":
                yield {"type": "success", "message": f"Successfully trimmed audio: {output_path}"}
            else:
                yield event
    except Exception as e:
        yield {"type": "error", "message": f"Error running FFmpeg: {str(e)}"}
