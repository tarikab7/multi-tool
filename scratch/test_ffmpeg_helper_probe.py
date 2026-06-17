import asyncio
import os

async def probe_duration(filepath):
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        filepath
    ]
    proc = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    if proc.returncode == 0 and stdout:
        return float(stdout.decode().strip())
    return 0.0

async def main():
    if not os.path.exists("test.mp4"):
        print("Generating test video...")
        os.system("ffmpeg -f lavfi -i testsrc=duration=5:size=320x240:rate=30 -y test.mp4")

    dur = await probe_duration("test.mp4")
    print(f"Duration: {dur}")

if __name__ == "__main__":
    asyncio.run(main())
