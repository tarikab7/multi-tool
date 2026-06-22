import asyncio
import requests

async def run(params: dict):
    url = params.get("url", "").strip()
    if not url:
        yield {"type": "error", "message": "Target URL is required."}
        return
        
    if not url.startswith("http"):
        url = "http://" + url
        
    yield {"type": "log", "message": f"Inspecting HTTP response headers for: {url}..."}
    
    try:
        
        response = await asyncio.to_thread(requests.get, url, allow_redirects=True, timeout=8)
        
        
        if response.history:
            yield {"type": "log", "message": "--- Redirection Hops ---"}
            for idx, hop in enumerate(response.history, 1):
                yield {"type": "found", "message": f"Hop {idx}: {hop.status_code} Redirect to -> {hop.headers.get('Location')}"}
                
        yield {"type": "log", "message": f"--- Final Response Status: {response.status_code} ---"}
        for k, v in response.headers.items():
            yield {"type": "found", "message": f"{k}: {v}"}
            
        yield {"type": "success", "message": "HTTP header inspection completed successfully."}
    except Exception as e:
        yield {"type": "error", "message": f"Connection error: {str(e)}"}
