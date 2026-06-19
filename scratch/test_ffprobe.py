import asyncio
import subprocess

async def get_duration(file_path):
    cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", file_path
    ]
    proc = await asyncio.create_subprocess_exec(*cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = await proc.communicate()
    if proc.returncode == 0:
        return float(stdout.decode().strip())
    return None

async def main():
    print(await get_duration("test_video.mp4"))

asyncio.run(main())
