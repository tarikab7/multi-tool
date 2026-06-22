import asyncio
from tools.utils import yield_log, yield_error, yield_success, ToolEvent

async def run(params: dict):
    share_url = params.get("share_url", "").strip()
    if not share_url:
        yield yield_error("Google Drive sharing URL is required.")
        return
        
    yield yield_log("Parsing Drive sharing link elements...")
    await asyncio.sleep(0.5)
    
    
    
    
    
    file_id = None
    if "/file/d/" in share_url:
        parts = share_url.split("/file/d/")
        if len(parts) > 1:
            file_id = parts[1].split("/")[0].split("?")[0]
    elif "id=" in share_url:
        parts = share_url.split("id=")
        if len(parts) > 1:
            file_id = parts[1].split("&")[0]
            
    if file_id:
        direct_url = f"https://docs.google.com/uc?export=download&id={file_id}"
        yield ToolEvent(type="found", message=f"File ID: {file_id}")
        yield ToolEvent(type="found", message=f"Direct Link: {direct_url}")
        yield yield_success("Successfully converted to direct download link.")
    else:
        yield yield_error("Unable to extract file ID. Ensure link has standard Drive format.")
