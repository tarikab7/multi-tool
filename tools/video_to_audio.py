import os
import asyncio
from tools.ffmpeg_helper import run_ffmpeg_with_progress, get_media_duration

async def run(params: dict):
    video_path = params.get("video_path", "").strip()
    format_type = params.get("format_type", "mp3").strip()
    output_path = params.get("output_path", "").strip()
    
    if not video_path or not os.path.exists(video_path):
        yield {"type": "error", "message": "Valid video path is required."}
        return
        
    if not output_path:
        base, _ = os.path.splitext(video_path)
        output_path = f"{base}.{format_type}"
        
    yield {"type": "log", "message": f"Extracting audio track to {format_type}..."}
    
    duration = await get_media_duration(video_path)

    cmd = ["ffmpeg", "-y", "-i", video_path, "-vn"]
    if format_type == "mp3":
        cmd.extend(["-acodec", "libmp3lame", "-ab", "256k"])
    elif format_type == "wav":
        cmd.extend(["-acodec", "pcm_s16le"])
    else:
        cmd.extend(["-acodec", "aac"])
    cmd.append(output_path)
    
    success_msg = f"Extracted audio track successfully: {output_path}"
    async for event in run_ffmpeg_with_progress(cmd, duration=duration, success_message=success_msg):
        yield event
