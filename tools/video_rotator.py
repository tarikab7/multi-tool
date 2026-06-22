import os
import subprocess
import asyncio

async def run(params: dict):
    video_path = params.get("video_path", "").strip()
    angle = params.get("angle", "90").strip() 
    output_path = params.get("output_path", "").strip()
    
    if not video_path or not os.path.exists(video_path):
        yield {"type": "error", "message": "Valid video path is required."}
        return
        
    if not output_path:
        base, ext = os.path.splitext(video_path)
        output_path = f"{base}_rotated{ext}"
        
    yield {"type": "log", "message": f"Rotating/flipping video by filter '{angle}'..."}
    
    vf_filter = ""
    if angle == "90":
        vf_filter = "transpose=1"
    elif angle == "180":
        vf_filter = "transpose=2,transpose=2"
    elif angle == "270":
        vf_filter = "transpose=2"
    elif angle == "flip_h":
        vf_filter = "hflip"
    elif angle == "flip_v":
        vf_filter = "vflip"
        
    cmd = ["ffmpeg", "-y", "-i", video_path, "-vf", vf_filter, "-metadata:s:v", "rotate=0", output_path]
    
    try:
        proc = await asyncio.create_subprocess_exec(*cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = await proc.communicate()
        if proc.returncode == 0:
            yield {"type": "success", "message": f"Video rotated successfully: {output_path}"}
        else:
            yield {"type": "error", "message": f"FFmpeg failed: {stderr.decode()}"}
    except Exception as e:
        yield {"type": "error", "message": f"Error running rotation: {str(e)}"}
