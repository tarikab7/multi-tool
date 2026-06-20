import asyncio
import requests
from tools.utils import yield_error, yield_log, yield_success, ToolEvent

async def run(params: dict):
    mac = params.get("mac", "").strip().replace(":", "").replace("-", "").replace(".", "")[:6]
    if not mac:
        yield yield_error("Valid MAC Address is required.")
        return
        
    yield yield_log(f"Checking vendor assignment database for prefix '{mac}'...")
    
    url = f"https://api.macvendors.com/{mac}"
    try:
        response = await asyncio.to_thread(requests.get, url, timeout=5)
        if response.status_code == 200:
            vendor = response.text
            yield ToolEvent(event_type="found", message=f"OUI Vendor: {vendor}")
            yield yield_success(f"Match found: {vendor}")
        else:
            yield yield_error("Vendor prefix not found in database.")
    except Exception as e:
        yield yield_error(f"Connection failed: {str(e)}")
