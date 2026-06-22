import uuid
import asyncio

async def run(params: dict):
    version = params.get("version", "v4").strip() 
    count = int(params.get("count", "5"))
    
    yield {"type": "log", "message": f"Generating {count} UUID {version} values..."}
    await asyncio.sleep(0.2)
    
    try:
        for i in range(count):
            uid = uuid.uuid4() if version == "v4" else uuid.uuid1()
            yield {"type": "found", "message": str(uid)}
        yield {"type": "success", "message": f"Generated {count} UUIDs successfully."}
    except Exception as e:
        yield {"type": "error", "message": f"Generation error: {str(e)}"}
