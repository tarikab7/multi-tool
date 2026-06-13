import os
import subprocess
import asyncio
from tools.ffmpeg_helper import run_ffmpeg_with_progress

async def run(params: dict):
    video_path = params.get("video_path", "").strip()
    output_path = params.get("output_path", "").strip()
    
    if not video_path or not os.path.exists(video_path):
        yield {"type": "error", "message": "Valid video file path is required."}
        return
        
    if not output_path:
        base, ext = os.path.splitext(video_path)
        output_path = f"{base}_stabilized{ext}"
        
    yield {"type": "log", "message": "Step 1: Detecting video shakiness transients..."}
    # Pass 1 of vidstab
    cmd1 = ["ffmpeg", "-y", "-i", video_path, "-vf", "vidstabdetect=shakiness=10:accuracy=15:result=transforms.trf", "-f", "null", "-"]
    
    try:
        async for update in run_ffmpeg_with_progress(cmd1, "Pass 1 complete"):
            if update["type"] == "success":
                continue  # Filter out success message from pass 1
            yield update

        yield {"type": "log", "message": "Step 2: Re-rendering video frames with motion compensation..."}
        # Pass 2 of vidstab
        cmd2 = ["ffmpeg", "-y", "-i", video_path, "-vf", "vidstabtransform=smoothing=30:input=transforms.trf", output_path]
        
        async for update in run_ffmpeg_with_progress(cmd2, f"Stabilized video written to: {output_path}"):
            yield update

        if os.path.exists("transforms.trf"):
            os.remove("transforms.trf")
            
    except Exception as e:
        yield {"type": "error", "message": f"Error running stabilization: {str(e)}"}
