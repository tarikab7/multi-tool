import asyncio
import requests

async def run(params: dict):
    mac = params.get("mac", "").strip().replace(":", "").replace("-", "").replace(".", "")[:6]
    if not mac:
        yield {"type": "error", "message": "Valid MAC Address is required."}
        return
        
    yield {"type": "log", "message": f"Checking vendor assignment database for prefix '{mac}'..."}
    
    url = f"https://api.macvendors.com/{mac}"
    try:
        response = await asyncio.to_thread(requests.get, url, timeout=5)
        if response.status_code == 200:
            vendor = response.text
            yield {"type": "found", "message": f"OUI Vendor: {vendor}"}
            yield {"type": "success", "message": f"Match found: {vendor}"}
        else:
            yield {"type": "error", "message": "Vendor prefix not found in database."}
    except Exception as e:
        yield {"type": "error", "message": f"Connection failed: {str(e)}"}
