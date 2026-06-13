import asyncio
from tools.ffmpeg_helper import run_ffmpeg_with_progress
import os

async def main():
    # first create a dummy wav file
    cmd1 = ["ffmpeg", "-y", "-f", "lavfi", "-i", "sine=frequency=1000:duration=5", "test_audio.wav"]
    proc1 = await asyncio.create_subprocess_exec(*cmd1, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    await proc1.communicate()

    # now test the progress helper
    cmd2 = ["ffmpeg", "-y", "-i", "test_audio.wav", "-ss", "00:00:01", "-c", "copy", "test_audio_trimmed.wav"]
    async for update in run_ffmpeg_with_progress(cmd2, "Test complete"):
        print(update)

    os.remove("test_audio.wav")
    os.remove("test_audio_trimmed.wav")

asyncio.run(main())
