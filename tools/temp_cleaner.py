import os
import tempfile
import asyncio

async def run(params: dict):
    yield {"type": "log", "message": "Scanning OS cache directories and temp files..."}
    await asyncio.sleep(1)
    
    temp_dir = tempfile.gettempdir()
    cleaned_bytes = 0
    error_count = 0
    file_count = 0
    
    try:
        for root, dirs, files in os.walk(temp_dir):
            for name in files:
                file_path = os.path.join(root, name)
                try:
                    size = os.path.getsize(file_path)
                    os.remove(file_path)
                    cleaned_bytes += size
                    file_count += 1
                except Exception:
                    error_count += 1
            await asyncio.sleep(0.001)
            
        cleaned_mb = cleaned_bytes / (1024 * 1024)
        yield {"type": "log", "message": f"Cleared {file_count} temporary files."}
        yield {"type": "log", "message": f"Locked/Busy files skipped: {error_count}"}
        yield {"type": "success", "message": f"Freed {cleaned_mb:.2f} MB of disk space."}
    except Exception as e:
        yield {"type": "error", "message": f"Temp cleanup failed: {str(e)}"}
