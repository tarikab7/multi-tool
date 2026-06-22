import asyncio
import requests

async def run(params: dict):
    url = params.get("url", "").strip()
    action = params.get("action", "shorten").strip() 
    
    if not url:
        yield {"type": "error", "message": "Target URL is required."}
        return
        
    try:
        if action == "shorten":
            yield {"type": "log", "message": "Querying tinyurl API keylessly..."}
            api_url = f"http://tinyurl.com/api-create.php?url={requests.utils.quote(url)}"
            response = await asyncio.to_thread(requests.get, api_url, timeout=8)
            if response.status_code == 200:
                short_url = response.text
                yield {"type": "found", "message": f"Short URL: {short_url}"}
                yield {"type": "success", "message": f"Shortened link: {short_url}"}
            else:
                yield {"type": "error", "message": "TinyURL service returned error status."}
        else: 
            yield {"type": "log", "message": "Following URL redirect path to find original link..."}
            response = await asyncio.to_thread(requests.head, url, allow_redirects=True, timeout=8)
            yield {"type": "found", "message": f"Expanded Destination: {response.url}"}
            yield {"type": "success", "message": "Successfully expanded redirect link."}
    except Exception as e:
        yield {"type": "error", "message": f"URL resolution error: {str(e)}"}
