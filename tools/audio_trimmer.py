import os
import subprocess
import asyncio
from tools.ffmpeg_helper import get_media_duration, run_ffmpeg_with_progress

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
    
    duration = 0.0
    if end_time:
        try:
            # Parse start_time and end_time to compute duration
            def parse_time(t_str):
                parts = t_str.split(':')
                if len(parts) == 3:
                    return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
                elif len(parts) == 2:
                    return int(parts[0]) * 60 + float(parts[1])
                return float(parts[0])
            st = parse_time(start_time)
            et = parse_time(end_time)
            duration = et - st
        except Exception:
            duration = await get_media_duration(audio_path)
    else:
        duration = await get_media_duration(audio_path)
        try:
            def parse_time(t_str):
                parts = t_str.split(':')
                if len(parts) == 3:
                    return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
                elif len(parts) == 2:
                    return int(parts[0]) * 60 + float(parts[1])
                return float(parts[0])
            st = parse_time(start_time)
            if duration > st:
                duration -= st
        except Exception:
            pass

    async for event in run_ffmpeg_with_progress(
        cmd,
        duration,
        f"Successfully trimmed audio: {output_path}"
    ):
        yield event
