import os
import asyncio
from tools.ffmpeg_helper import run_ffmpeg_with_progress, get_media_duration

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
    
    try:
        pass1_success = False
        async for event in run_ffmpeg_with_progress(cmd1, duration=duration, success_message=""):
            if event["type"] == "success":
                pass1_success = True
            elif event["type"] == "progress":
                # Rescale progress for pass 1 (0-50%)
                yield {"type": "progress", "progress": round(event["progress"] / 2.0, 2)}
            else:
                yield event

        if not pass1_success:
            return

        yield {"type": "log", "message": "Step 2: Re-rendering video frames with motion compensation..."}
        # Pass 2 of vidstab
        cmd2 = ["ffmpeg", "-y", "-i", video_path, "-vf", "vidstabtransform=smoothing=30:input=transforms.trf", output_path]
        
        success_msg = f"Stabilized video written to: {output_path}"
        async for event in run_ffmpeg_with_progress(cmd2, duration=duration, success_message=success_msg):
            if event["type"] == "progress":
                # Rescale progress for pass 2 (50-100%)
                yield {"type": "progress", "progress": round(50.0 + (event["progress"] / 2.0), 2)}
            else:
                yield event

    finally:
        if os.path.exists("transforms.trf"):
            os.remove("transforms.trf")
