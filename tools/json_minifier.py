import json
import asyncio

async def run(params: dict):
    raw_json = params.get("raw_json", "").strip()
    action = params.get("action", "format").strip() # format / minify
    
    if not raw_json:
        yield {"type": "error", "message": "JSON input string is required."}
        return
        
    yield {"type": "log", "message": f"Running JSON syntax parses and {action}ting..."}
    
    try:
        data = json.loads(raw_json)
        if action == "format":
            out = json.dumps(data, indent=4)
        else:
            out = json.dumps(data, separators=(',', ':'))
            
        yield {"type": "found", "message": out}
        yield {"type": "success", "message": "JSON parsed successfully."}
    except Exception as e:
        yield {"type": "error", "message": f"Invalid JSON syntax: {str(e)}"}
