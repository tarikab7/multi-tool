import os
import subprocess
import asyncio
from tools.ffmpeg_helper import get_media_duration, run_ffmpeg_with_progress

async def run(params: dict):
    video_path = params.get("video_path", "").strip()
    output_path = params.get("output_path", "").strip()
    
    if not video_path or not os.path.exists(video_path):
        yield {"type": "error", "message": "Valid video file path is required."}
        return
        
    if not output_path:
        base, ext = os.path.splitext(video_path)
        output_path = f"{base}_stabilized{ext}"
        
    duration = await get_media_duration(video_path)

    yield {"type": "log", "message": "Step 1: Detecting video shakiness transients..."}
    # Pass 1 of vidstab
    cmd1 = ["ffmpeg", "-y", "-i", video_path, "-vf", "vidstabdetect=shakiness=10:accuracy=15:result=transforms.trf", "-f", "null", "-"]
    
    pass1_success = False
    async for msg in run_ffmpeg_with_progress(cmd1, duration, success_message=None):
        # We handle success of pass1 manually
        if msg["type"] == "error":
            yield msg
            return
        elif msg["type"] == "progress":
            # Scale pass 1 to 0-50%
            yield {"type": "progress", "percentage": msg["percentage"] * 0.5}
    pass1_success = True

    if pass1_success:
        yield {"type": "log", "message": "Step 2: Re-rendering video frames with motion compensation..."}
        # Pass 2 of vidstab
        cmd2 = ["ffmpeg", "-y", "-i", video_path, "-vf", "vidstabtransform=smoothing=30:input=transforms.trf", output_path]
        
        success_message = f"Stabilized video written to: {output_path}"
        async for msg in run_ffmpeg_with_progress(cmd2, duration, success_message):
            if msg["type"] == "progress":
                # Scale pass 2 to 50-100%
                yield {"type": "progress", "percentage": 50.0 + msg["percentage"] * 0.5}
            else:
                yield msg

    if os.path.exists("transforms.trf"):
        os.remove("transforms.trf")
