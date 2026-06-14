import os
import asyncio
import subprocess
from tools.utils import yield_log, yield_success, yield_error, yield_progress

async def run(params: dict):
    mode = params.get("mode", "create") # "create" or "extract"
    input_path = params.get("input_path", "").strip()
    fps = params.get("fps", "10").strip()
    width = params.get("width", "480").strip()
    output_path = params.get("output_path", "").strip()

    if not input_path:
        yield yield_error("Input file path is required.")
        return

    input_path = os.path.expanduser(input_path)
    if not os.path.isfile(input_path):
        yield yield_error(f"Input file '{input_path}' not found.")
        return

    output_path = os.path.expanduser(output_path)
    
    if mode == "create":
        # Create GIF from Video
        if not output_path.lower().endswith(".gif"):
            yield yield_error("Output path must end with '.gif'.")
            return
            
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        yield yield_log("Generating high-quality GIF with custom color palette...")
        
        # High quality palette generation & mapping filter
        filter_str = f"[0:v]fps={fps},scale={width}:-1:flags=lanczos,split[a][b];[a]palettegen[p];[b][p]paletteuse"
        
        cmd = ['ffmpeg', '-y', '-i', input_path, '-filter_complex', filter_str, output_path]
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            _, stderr = await process.communicate()
            
            if process.returncode == 0:
                yield yield_progress(100.0)
                yield yield_log(f"Saved GIF to: {output_path}")
                yield yield_success("Successfully created GIF.")
            else:
                err = stderr.decode('utf-8', errors='ignore')
                yield yield_error(f"GIF generation failed: {err[:200]}...")
        except Exception as e:
            yield yield_error(f"Failed to run ffmpeg: {str(e)}")
            
    else:
        # Extract frames from GIF/Video
        os.makedirs(output_path, exist_ok=True)
        yield yield_log(f"Extracting frames into: {output_path}")
        
        # Extracts all frames as PNG
        out_pattern = os.path.join(output_path, "frame_%04d.png")
        cmd = ['ffmpeg', '-y', '-i', input_path, '-vsync', '0', out_pattern]
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            _, stderr = await process.communicate()
            
            if process.returncode == 0:
                count = len([f for f in os.listdir(output_path) if f.startswith("frame_")])
                yield yield_progress(100.0)
                yield yield_log(f"Extracted {count} frame(s) as PNG.")
                yield yield_success(f"Successfully extracted {count} frames.")
            else:
                err = stderr.decode('utf-8', errors='ignore')
                yield yield_error(f"Frame extraction failed: {err[:200]}...")
        except Exception as e:
            yield yield_error(f"Failed to run ffmpeg: {str(e)}")
