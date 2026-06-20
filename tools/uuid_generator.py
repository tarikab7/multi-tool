import uuid
import asyncio
from tools.utils import yield_error, yield_log, yield_success, ToolEvent

async def run(params: dict):
    version = params.get("version", "v4").strip() # v1, v4
    count = int(params.get("count", "5"))
    
    yield yield_log(f"Generating {count} UUID {version} values...")
    await asyncio.sleep(0.2)
    
    try:
        for i in range(count):
            uid = uuid.uuid4() if version == "v4" else uuid.uuid1()
            yield ToolEvent(event_type="found", message=str(uid))
        yield yield_success(f"Generated {count} UUIDs successfully.")
    except Exception as e:
        yield yield_error(f"Generation error: {str(e)}")
