import asyncio

async def run(params: dict):
    share_url = params.get("share_url", "").strip()
    if not share_url:
        yield {"type": "error", "message": "Google Drive sharing URL is required."}
        return
        
    yield {"type": "log", "message": "Parsing Drive sharing link elements..."}
    await asyncio.sleep(0.5)
    
    # Types of Drive links:
    # https://drive.google.com/file/d/1A2B3C/view?usp=sharing
    # https://drive.google.com/open?id=1A2B3C
    
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
        yield {"type": "found", "message": f"File ID: {file_id}"}
        yield {"type": "found", "message": f"Direct Link: {direct_url}"}
        yield {"type": "success", "message": "Successfully converted to direct download link."}
    else:
        yield {"type": "error", "message": "Unable to extract file ID. Ensure link has standard Drive format."}
