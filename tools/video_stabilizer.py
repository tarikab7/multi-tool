import os
import subprocess
import asyncio

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
        proc1 = await asyncio.create_subprocess_exec(*cmd1, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        await proc1.communicate()
        
        yield {"type": "log", "message": "Step 2: Re-rendering video frames with motion compensation..."}
        # Pass 2 of vidstab
        cmd2 = ["ffmpeg", "-y", "-i", video_path, "-vf", "vidstabtransform=smoothing=30:input=transforms.trf", output_path]
        proc2 = await asyncio.create_subprocess_exec(*cmd2, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = await proc2.communicate()
        
        if os.path.exists("transforms.trf"):
            os.remove("transforms.trf")
            
        if proc2.returncode == 0:
            yield {"type": "success", "message": f"Stabilized video written to: {output_path}"}
        else:
            yield {"type": "error", "message": f"Stabilizer failed: {stderr.decode()}"}
    except Exception as e:
        yield {"type": "error", "message": f"Error running stabilization: {str(e)}"}
