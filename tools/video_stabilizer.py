import os
import subprocess
import asyncio
from .ffmpeg_helper import run_ffmpeg_with_progress

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
    
    pass1_success = False
    async for res in run_ffmpeg_with_progress(cmd1, duration=None, success_msg="Pass 1 completed."):
        if res["type"] == "success":
            pass1_success = True
        elif res["type"] == "error":
            yield res
            return
        else:
            # Yield progress for pass 1, but maybe prepend log to distinguish
            yield {"type": res["type"], "message": f"[Pass 1] {res['message']}"}

    if not pass1_success:
        return

    yield {"type": "log", "message": "Step 2: Re-rendering video frames with motion compensation..."}
    # Pass 2 of vidstab
    cmd2 = ["ffmpeg", "-y", "-i", video_path, "-vf", "vidstabtransform=smoothing=30:input=transforms.trf", output_path]

    success_msg = f"Stabilized video written to: {output_path}"
    async for res in run_ffmpeg_with_progress(cmd2, duration=None, success_msg=success_msg):
        if res["type"] in ("progress", "success", "error"):
            if res["type"] == "progress":
                yield {"type": res["type"], "message": f"[Pass 2] {res['message']}"}
            else:
                yield res

    if os.path.exists("transforms.trf"):
        os.remove("transforms.trf")
