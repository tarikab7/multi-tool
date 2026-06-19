import asyncio
import os
from tools.ffmpeg_helper import get_media_duration, run_ffmpeg_with_progress

async def main():
    print("Creating a 2-second dummy video for testing...")
    cmd_dummy = ["ffmpeg", "-y", "-f", "lavfi", "-i", "testsrc=duration=2:size=320x240:rate=10", "dummy.mp4"]
    proc = await asyncio.create_subprocess_exec(*cmd_dummy, stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL)
    await proc.wait()

    print("Testing get_media_duration...")
    duration = await get_media_duration("dummy.mp4")
    print(f"Duration: {duration}")
    assert duration is not None
    assert 1.9 < duration < 2.1

    print("Testing run_ffmpeg_with_progress...")
    # Convert dummy to another format to trigger progress
    cmd_progress = ["ffmpeg", "-y", "-i", "dummy.mp4", "dummy.avi"]

    events = []
    async for event in run_ffmpeg_with_progress(cmd_progress, duration, "Success!"):
        print(f"Event: {event}")
        events.append(event)

    assert any(e.get("type") == "log" and "Progress:" in e.get("message", "") for e in events)
    assert events[-1].get("type") == "success"

    print("All tests passed!")

    # Cleanup
    if os.path.exists("dummy.mp4"):
        os.remove("dummy.mp4")
    if os.path.exists("dummy.avi"):
        os.remove("dummy.avi")

if __name__ == "__main__":
    asyncio.run(main())
