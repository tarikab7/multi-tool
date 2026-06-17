import os
import subprocess
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
        
    duration_sec = await get_media_duration(video_path)

    yield {"type": "log", "message": "Step 1: Detecting video shakiness transients..."}
    # Pass 1 of vidstab
    cmd1 = ["ffmpeg", "-y", "-i", video_path, "-vf", "vidstabdetect=shakiness=10:accuracy=15:result=transforms.trf", "-f", "null", "-"]
    
    try:
        async for event in run_ffmpeg_with_progress(*cmd1, duration_seconds=duration_sec):
            if event["type"] == "progress":
                yield {"type": "progress", "progress": event["progress"] * 0.5}
            elif event["type"] == "error":
                yield {"type": "error", "message": event["message"]}
                return
        
        yield {"type": "log", "message": "Step 2: Re-rendering video frames with motion compensation..."}
        # Pass 2 of vidstab
        cmd2 = ["ffmpeg", "-y", "-i", video_path, "-vf", "vidstabtransform=smoothing=30:input=transforms.trf", output_path]
        
        async for event in run_ffmpeg_with_progress(*cmd2, duration_seconds=duration_sec):
            if event["type"] == "progress":
                yield {"type": "progress", "progress": 50.0 + (event["progress"] * 0.5)}
            elif event["type"] == "error":
                if os.path.exists("transforms.trf"):
                    os.remove("transforms.trf")
                yield {"type": "error", "message": event["message"]}
                return
            elif event["type"] == "success":
                pass

        if os.path.exists("transforms.trf"):
            os.remove("transforms.trf")
            
        yield {"type": "success", "message": f"Stabilized video written to: {output_path}"}
    except Exception as e:
        yield {"type": "error", "message": f"Error running stabilization: {str(e)}"}
