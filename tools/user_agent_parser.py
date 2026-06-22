import asyncio

async def run(params: dict):
    ua = params.get("user_agent", "").strip()
    if not ua:
        yield {"type": "error", "message": "User-Agent string is required."}
        return
        
    yield {"type": "log", "message": "Analyzing User-Agent segments..."}
    await asyncio.sleep(0.5)
    
    os_name = "Unknown OS"
    browser = "Unknown Browser"
    
    
    if "Windows NT 10.0" in ua: os_name = "Windows 10 / 11"
    elif "Windows NT 6.3" in ua: os_name = "Windows 8.1"
    elif "Windows NT 6.1" in ua: os_name = "Windows 7"
    elif "Android" in ua: os_name = "Android OS"
    elif "iPhone" in ua: os_name = "Apple iOS (iPhone)"
    elif "Macintosh" in ua: os_name = "macOS"
    elif "Linux" in ua: os_name = "Linux"
    
    if "Firefox" in ua: browser = "Mozilla Firefox"
    elif "Chrome" in ua and "Safari" in ua and "Edge" not in ua: browser = "Google Chrome"
    elif "Safari" in ua and "Chrome" not in ua: browser = "Apple Safari"
    elif "Edg" in ua: browser = "Microsoft Edge"
    elif "Trident" in ua or "MSIE" in ua: browser = "Internet Explorer"
    
    yield {"type": "found", "message": f"Operating System: {os_name}"}
    yield {"type": "found", "message": f"Browser Application: {browser}"}
    yield {"type": "success", "message": "User Agent details extracted."}
