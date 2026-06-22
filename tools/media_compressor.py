import os
import json
import asyncio
import subprocess

async def get_video_duration(filepath):
    cmd = [
        'ffprobe', '-v', 'error', 
        '-show_entries', 'format=duration', 
        '-of', 'default=noprint_wrappers=1:nokey=1', 
        filepath
    ]
    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, _ = await process.communicate()
        return float(stdout.decode('utf-8').strip())
    except Exception:
        return 0.0

async def run(params: dict):
    input_path = params.get("input_path", "").strip()
    target_mb = params.get("target_mb", "8").strip()
    output_folder = params.get("output_folder", "").strip()

    if not input_path:
        yield {"type": "error", "message": "Input path is required."}
        return

    input_path = os.path.expanduser(input_path)
    if not os.path.isfile(input_path):
        yield {"type": "error", "message": f"Input file '{input_path}' not found."}
        return

    try:
        target_size_bytes = float(target_mb) * 1024 * 1024
    except ValueError:
        yield {"type": "error", "message": "Target size must be a number."}
        return

    if not output_folder:
        output_folder = os.path.dirname(input_path)
    else:
        output_folder = os.path.expanduser(output_folder)
    os.makedirs(output_folder, exist_ok=True)

    filename = os.path.basename(input_path)
    name, ext = os.path.splitext(filename)
    output_file = os.path.join(output_folder, f"{name}-compressed{ext}")

    yield {"type": "log", "message": f"Analyzing file: {filename}"}
    duration = await get_video_duration(input_path)

    if duration <= 0:
        yield {"type": "error", "message": "Could not determine media duration."}
        return

    yield {"type": "log", "message": f"Duration: {duration:.2f} seconds. Calculating bitrates..."}

    
    
    target_bitrate = int((target_size_bytes * 8) / duration)

    
    audio_bitrate = 128000 
    video_bitrate = target_bitrate - audio_bitrate

    if video_bitrate < 100000: 
        audio_bitrate = 64000
        video_bitrate = max(64000, target_bitrate - audio_bitrate)

    video_bitrate_kb = int(video_bitrate / 1000)
    audio_bitrate_kb = int(audio_bitrate / 1000)

    yield {"type": "log", "message": f"Compressing: Target Video {video_bitrate_kb}kbps, Audio {audio_bitrate_kb}kbps"}

    
    
    yield {"type": "log", "message": "Starting compression pass 1..."}
    pass1_cmd = [
        'ffmpeg', '-y', '-i', input_path,
        '-c:v', 'libx264', '-b:v', f'{video_bitrate_kb}k',
        '-pass', '1', '-an', '-f', 'null', '/dev/null'
    ]
    
    try:
        process1 = await asyncio.create_subprocess_exec(
            *pass1_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        await process1.communicate()
        yield {"type": "progress", "percent": 50.0}

        
        yield {"type": "log", "message": "Starting compression pass 2..."}
        pass2_cmd = [
            'ffmpeg', '-y', '-i', input_path,
            '-c:v', 'libx264', '-b:v', f'{video_bitrate_kb}k',
            '-pass', '2', '-c:a', 'aac', '-b:a', f'{audio_bitrate_kb}k',
            output_file
        ]
        
        process2 = await asyncio.create_subprocess_exec(
            *pass2_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        _, stderr = await process2.communicate()
        
        
        if os.path.exists("ffmpeg2pass-0.log"):
            os.remove("ffmpeg2pass-0.log")
        if os.path.exists("ffmpeg2pass-0.log.mbtree"):
            os.remove("ffmpeg2pass-0.log.mbtree")

        if process2.returncode == 0:
            yield {"type": "progress", "percent": 100.0}
            yield {"type": "log", "message": f"Saved compressed file: {output_file}"}
            yield {"type": "success", "message": f"Successfully compressed {filename} to {target_mb}MB target."}
        else:
            err_msg = stderr.decode('utf-8', errors='ignore')
            yield {"type": "error", "message": f"Compression failed: {err_msg[:200]}..."}
            
    except Exception as e:
        yield {"type": "error", "message": f"Compression execution failed: {str(e)}"}
