import os
import subprocess
import asyncio
from tools.ffmpeg_helper import run_ffmpeg_with_progress

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
    
    # Calculate expected duration if possible
    expected_duration = None
    start_sec = 0.0
    try:
        def time_to_sec(t_str):
            parts = t_str.split(':')
            if len(parts) == 3:
                return float(parts[0])*3600 + float(parts[1])*60 + float(parts[2])
            elif len(parts) == 2:
                return float(parts[0])*60 + float(parts[1])
            return float(t_str)

        start_sec = time_to_sec(start_time) if start_time else 0
        if end_time:
            end_sec = time_to_sec(end_time)
            expected_duration = end_sec - start_sec if end_sec > start_sec else None
    except Exception:
        pass

    # Construct FFmpeg command
    cmd = ["ffmpeg", "-y", "-i", audio_path, "-ss", start_time]
    if end_time:
        cmd.extend(["-to", end_time])
    cmd.extend(["-c", "copy", output_path])
    
    try:
        async for update in run_ffmpeg_with_progress(*cmd, expected_duration=expected_duration, start_offset=start_sec):
            if update["type"] == "success":
                yield {"type": "success", "message": f"Successfully trimmed audio: {output_path}"}
            else:
                yield update
    except Exception as e:
        yield {"type": "error", "message": f"Error running FFmpeg: {str(e)}"}
