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
    
    try:
        # We don't really care about progress output for pass 1 if it's too fast, but we can stream it.
        # However, we only care to stream events if it takes long. Both take long.
        async for event in run_ffmpeg_with_progress(cmd1):
            if event["type"] == "_result":
                if event["returncode"] != 0:
                    yield {"type": "error", "message": f"Stabilizer pass 1 failed: {event['stderr']}"}
                    return
            else:
                yield event
        
        yield {"type": "log", "message": "Step 2: Re-rendering video frames with motion compensation..."}
        # Pass 2 of vidstab
        cmd2 = ["ffmpeg", "-y", "-i", video_path, "-vf", "vidstabtransform=smoothing=30:input=transforms.trf", output_path]

        returncode = -1
        stderr = ""
        async for event in run_ffmpeg_with_progress(cmd2):
            if event["type"] == "_result":
                returncode = event["returncode"]
                stderr = event["stderr"]
            else:
                yield event
        
        if os.path.exists("transforms.trf"):
            os.remove("transforms.trf")
            
        if returncode == 0:
            yield {"type": "success", "message": f"Stabilized video written to: {output_path}"}
        else:
            yield {"type": "error", "message": f"Stabilizer pass 2 failed: {stderr}"}
    except asyncio.CancelledError:
        raise
    except Exception as e:
        yield {"type": "error", "message": f"Error running stabilization: {str(e)}"}
