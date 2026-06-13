import asyncio

async def run(params: dict):
    text = params.get("text", "").strip()
    if not text:
        yield {"type": "error", "message": "Input text is required."}
        return
        
    yield {"type": "log", "message": "Tokenizing text inputs..."}
    await asyncio.sleep(0.3)
    
    try:
        chars = len(text)
        words = len(text.split())
        lines = len(text.splitlines())
        reading_time_min = words / 200 # Average reading speed 200 wpm
        
        yield {"type": "found", "message": f"Characters: {chars}"}
        yield {"type": "found", "message": f"Words: {words}"}
        yield {"type": "found", "message": f"Lines: {lines}"}
        yield {"type": "found", "message": f"Est. Reading Time: {reading_time_min:.2f} minute(s)"}
        yield {"type": "success", "message": "Counting finished."}
    except Exception as e:
        yield {"type": "error", "message": f"Command error: {str(e)}"}
