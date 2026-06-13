import os
import asyncio
import subprocess
import tempfile
import shutil
from PIL import Image, ImageDraw, ImageFont

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

def extract_frame_sync(video_path, timestamp, output_path):
    # Extracts a single frame at timestamp using ffmpeg
    # Quick seek (-ss before -i) for speed
    cmd = [
        'ffmpeg', '-y', '-ss', str(timestamp), 
        '-i', video_path, 
        '-vframes', '1', 
        '-q:v', '2', 
        output_path
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return os.path.exists(output_path)

def create_sheet_sync(frame_paths, cols, rows, output_path, video_name):
    if not frame_paths:
        return False

    # Open first image to get dimensions
    first_img = Image.open(frame_paths[0])
    w, h = first_img.size
    
    # Scale width down to keep sheet dimensions reasonable
    target_w = 320
    target_h = int(h * (target_w / w))

    # Calculate sheet dimensions
    # Leave room for header
    header_h = 60
    sheet_w = target_w * cols
    sheet_h = (target_h * rows) + header_h

    # Create sheet image
    sheet = Image.new('RGB', (sheet_w, sheet_h), color='#0a0a0f')
    draw = ImageDraw.Draw(sheet)

    # Draw header text
    # Standard fallback fonts
    draw.text((20, 15), f"Video: {video_name}", fill="#ffffff")
    draw.text((20, 35), f"Grid: {cols}x{rows} contact sheet", fill="#9ca3af")

    for idx, path in enumerate(frame_paths):
        c = idx % cols
        r = idx // cols
        
        try:
            with Image.open(path) as img:
                img_resized = img.resize((target_w, target_h), Image.Resampling.BILINEAR)
                x = c * target_w
                y = (r * target_h) + header_h
                sheet.paste(img_resized, (x, y))
        except Exception:
            pass

    sheet.save(output_path, 'JPEG', quality=90)
    return True

async def run(params: dict):
    video_path = params.get("video_path", "").strip()
    cols_str = params.get("cols", "4").strip()
    rows_str = params.get("rows", "4").strip()
    output_path = params.get("output_path", "").strip()

    if not video_path or not output_path:
        yield {"type": "error", "message": "Both video path and output sheet path are required."}
        return

    video_path = os.path.expanduser(video_path)
    output_path = os.path.expanduser(output_path)

    if not os.path.isfile(video_path):
        yield {"type": "error", "message": f"Video file '{video_path}' not found."}
        return

    try:
        cols = int(cols_str)
        rows = int(rows_str)
    except ValueError:
        yield {"type": "error", "message": "Grid dimensions must be integers."}
        return

    yield {"type": "log", "message": f"Reading video duration..."}
    duration = await get_video_duration(video_path)
    if duration <= 0:
        yield {"type": "error", "message": "Could not parse video duration."}
        return

    total_frames = cols * rows
    yield {"type": "log", "message": f"Extracting {total_frames} frames from video..."}

    # Generate timestamps (skip first/last 5% to avoid black frames)
    start_time = duration * 0.05
    end_time = duration * 0.95
    step = (end_time - start_time) / (total_frames - 1) if total_frames > 1 else 0
    timestamps = [start_time + (i * step) for i in range(total_frames)]

    tmp_dir = tempfile.mkdtemp()
    frame_paths = []

    try:
        for idx, ts in enumerate(timestamps, 1):
            out_file = os.path.join(tmp_dir, f"frame_{idx:03d}.jpg")
            success = await asyncio.to_thread(extract_frame_sync, video_path, ts, out_file)
            if success:
                frame_paths.append(out_file)
                # Formulate dynamic log
                if idx % 4 == 0 or idx == total_frames:
                    yield {"type": "log", "message": f"Extracted frame {idx}/{total_frames} at {ts:.1f}s"}
            
            progress = (idx / total_frames) * 70  # Extraction takes 70% of progress
            yield {"type": "progress", "percent": progress}

        yield {"type": "log", "message": "Assembling contact sheet grid..."}
        success = await asyncio.to_thread(
            create_sheet_sync, frame_paths, cols, rows, output_path, os.path.basename(video_path)
        )

        if success:
            yield {"type": "progress", "percent": 100.0}
            yield {"type": "log", "message": f"Contact sheet saved: {output_path}"}
            yield {"type": "success", "message": "Thumbnail sheet generated successfully."}
        else:
            yield {"type": "error", "message": "Failed to assemble thumbnail sheet."}

    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
