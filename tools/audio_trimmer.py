import os
import subprocess
import asyncio
from tools.ffmpeg_helper import run_ffmpeg_with_progress, get_media_duration, parse_time_to_seconds

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
    
    try:
        if end_time:
            duration = parse_time_to_seconds(end_time) - parse_time_to_seconds(start_time)
        else:
            orig_duration = await get_media_duration(audio_path)
            duration = orig_duration - parse_time_to_seconds(start_time)
            if duration < 0:
                duration = 0

        
        cmd = ["ffmpeg", "-y", "-i", audio_path, "-ss", start_time]
        if end_time:
            cmd.extend(["-to", end_time])
        cmd.extend(["-c", "copy", output_path])

        has_error = False
        async for update in run_ffmpeg_with_progress(cmd, duration):
            if update["type"] == "error":
                has_error = True
            yield update

        if not has_error:
            yield {"type": "success", "message": f"Successfully trimmed audio: {output_path}"}

    except Exception as e:
        yield {"type": "error", "message": f"Error running FFmpeg: {str(e)}"}
