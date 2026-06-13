import json
import asyncio
from tools.utils import yield_log, yield_error, yield_success

async def run(params: dict):
    raw_json = params.get("raw_json", "").strip()
    action = params.get("action", "format").strip() # format / minify
    
    if not raw_json:
        yield yield_error("JSON input string is required.")
        return
        
    yield yield_log(f"Running JSON syntax parses and {action}ting...")
    
    try:
        data = json.loads(raw_json)
        if action == "format":
            out = json.dumps(data, indent=4)
        else:
            out = json.dumps(data, separators=(',', ':'))
            
        yield {"type": "found", "message": out}
        yield yield_success("JSON parsed successfully.")
    except Exception as e:
        yield yield_error(f"Invalid JSON syntax: {str(e)}")
