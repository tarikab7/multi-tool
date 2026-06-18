import asyncio
import requests
from tools.utils import yield_log, yield_error, yield_success

async def run(params: dict):
    url = params.get("url", "").strip()
    action = params.get("action", "shorten").strip() # shorten / expand
    
    if not url:
        yield yield_error("Target URL is required.")
        return
        
    try:
        if action == "shorten":
            yield yield_log("Querying tinyurl API keylessly...")
            api_url = f"http://tinyurl.com/api-create.php?url={requests.utils.quote(url)}"
            response = await asyncio.to_thread(requests.get, api_url, timeout=8)
            if response.status_code == 200:
                short_url = response.text
                yield {"type": "found", "message": f"Short URL: {short_url}"}
                yield yield_success(f"Shortened link: {short_url}")
            else:
                yield yield_error("TinyURL service returned error status.")
        else: # expand
            yield yield_log("Following URL redirect path to find original link...")
            response = await asyncio.to_thread(requests.head, url, allow_redirects=True, timeout=8)
            yield {"type": "found", "message": f"Expanded Destination: {response.url}"}
            yield yield_success("Successfully expanded redirect link.")
    except Exception as e:
        yield yield_error(f"URL resolution error: {str(e)}")
