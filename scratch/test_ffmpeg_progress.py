import asyncio
import os
import subprocess

from tools.video_to_audio import run

async def main():
    print("Generating dummy video...")
    dummy_video = "scratch/dummy.mp4"
    if os.path.exists(dummy_video):
        os.remove(dummy_video)

    cmd = ["ffmpeg", "-f", "lavfi", "-i", "testsrc=duration=2:size=320x240:rate=10", "-f", "lavfi", "-i", "aevalsrc=0:duration=2", "-c:v", "libx264", "-c:a", "aac", dummy_video]
    proc = await asyncio.create_subprocess_exec(*cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    await proc.communicate()

    print("Testing video_to_audio progress...")
    params = {
        "video_path": dummy_video,
        "format_type": "mp3",
        "output_path": "scratch/dummy.mp3"
    }

    progress_updates = 0
    success = False

    async for msg in run(params):
        print(msg)
        if msg["type"] == "progress":
            progress_updates += 1
            assert "percentage" in msg
        elif msg["type"] == "success":
            success = True

    print(f"Total progress updates: {progress_updates}")

    assert success, "Tool did not emit success message"
    assert progress_updates > 0, "Tool did not emit any progress updates"

    if os.path.exists(dummy_video):
        os.remove(dummy_video)
    if os.path.exists("scratch/dummy.mp3"):
        os.remove("scratch/dummy.mp3")

    print("Test passed successfully.")

if __name__ == "__main__":
    asyncio.run(main())
