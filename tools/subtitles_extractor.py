import os
import asyncio
import subprocess

async def run(params: dict):
    video_path = params.get("video_path", "").strip()
    track_index = params.get("track_index", "0").strip()
    output_srt = params.get("output_srt", "").strip()

    if not video_path:
        yield {"type": "error", "message": "Video file path is required."}
        return

    video_path = os.path.expanduser(video_path)
    if not os.path.isfile(video_path):
        yield {"type": "error", "message": f"Video file '{video_path}' not found."}
        return

    try:
        track_index = int(track_index)
    except ValueError:
        yield {"type": "error", "message": "Track index must be an integer."}
        return

    if not output_srt:
        
        name, _ = os.path.splitext(video_path)
        output_srt = f"{name}.srt"
    else:
        output_srt = os.path.expanduser(output_srt)

    yield {"type": "log", "message": f"Extracting subtitle track {track_index} from '{os.path.basename(video_path)}'..."}

    cmd = [
        'ffmpeg', '-y',
        '-i', video_path,
        '-map', f'0:s:{track_index}',
        output_srt
    ]

    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        _, stderr = await process.communicate()

        if process.returncode == 0:
            yield {"type": "progress", "percent": 100.0}
            yield {"type": "log", "message": f"Subtitles saved to: {output_srt}"}
            yield {"type": "success", "message": "Subtitle track successfully extracted."}
        else:
            err = stderr.decode('utf-8', errors='ignore')
            yield {"type": "error", "message": f"Extraction failed (check if subtitle track exists): {err[:200]}..."}
    except Exception as e:
        yield {"type": "error", "message": f"Failed to run ffmpeg subtitle extractor: {str(e)}"}
