import os
import subprocess
import asyncio

async def run(params: dict):
    gif_path = params.get("gif_path", "").strip()
    output_path = params.get("output_path", "").strip()
    
    if not gif_path or not os.path.exists(gif_path):
        yield {"type": "error", "message": "Valid GIF path is required."}
        return
        
    if not output_path:
        base, _ = os.path.splitext(gif_path)
        output_path = f"{base}.mp4"
        
    yield {"type": "log", "message": "Converting animated GIF to H.264 MP4 stream..."}
    
    # -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" ensures dimensions are divisible by 2
    cmd = ["ffmpeg", "-y", "-i", gif_path, "-movflags", "+faststart", "-pix_fmt", "yuv420p", "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2", output_path]
    
    try:
        proc = await asyncio.create_subprocess_exec(*cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = await proc.communicate()
        if proc.returncode == 0:
            yield {"type": "success", "message": f"GIF converted to MP4: {output_path}"}
        else:
            yield {"type": "error", "message": f"FFmpeg failed: {stderr.decode()}"}
    except Exception as e:
        yield {"type": "error", "message": f"Error running conversion: {str(e)}"}
