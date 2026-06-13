import os
from mutagen.id3 import ID3

async def run(params: dict):
    mp3_path = params.get("mp3_path", "").strip()
    if not mp3_path or not os.path.exists(mp3_path):
        yield {"type": "error", "message": "Valid MP3 path is required."}
        return
        
    yield {"type": "log", "message": f"Stripping ID3 frames from {os.path.basename(mp3_path)}..."}
    try:
        audio = ID3(mp3_path)
        audio.delete()
        audio.save()
        yield {"type": "success", "message": "Successfully stripped all ID3 tags."}
    except Exception as e:
        yield {"type": "error", "message": f"Failed stripping tags: {str(e)}"}
