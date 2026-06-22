import requests
import asyncio
import xml.etree.ElementTree as ET

async def run(params: dict):
    feed_url = params.get("feed_url", "").strip()
    if not feed_url:
        yield {"type": "error", "message": "RSS Feed URL is required."}
        return
        
    yield {"type": "log", "message": f"Retrieving and parsing feed: {feed_url}..."}
    
    try:
        response = await asyncio.to_thread(requests.get, feed_url, timeout=10)
        if response.status_code != 200:
            yield {"type": "error", "message": f"Failed fetching RSS feed (HTTP {response.status_code})"}
            return
            
        root = ET.fromstring(response.content)
        
        
        items = root.findall(".//item")
        yield {"type": "log", "message": f"Detected {len(items)} feed items."}
        
        for item in items[:10]: 
            title = item.find("title").text if item.find("title") is not None else "No Title"
            link = item.find("link").text if item.find("link") is not None else ""
            pub_date = item.find("pubDate").text if item.find("pubDate") is not None else ""
            
            yield {"type": "found", "message": f"{pub_date} - {title} ({link})"}
            
        yield {"type": "success", "message": "RSS Feed parsed successfully."}
    except Exception as e:
        yield {"type": "error", "message": f"Error parsing feed: {str(e)}"}
