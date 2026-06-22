import requests
import asyncio
from bs4 import BeautifulSoup

async def run(params: dict):
    url = params.get("url", "").strip()
    if not url:
        yield {"type": "error", "message": "Target URL is required."}
        return
        
    yield {"type": "log", "message": f"Fetching page HTML from: {url}..."}
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = await asyncio.to_thread(requests.get, url, headers=headers, timeout=10)
        if response.status_code != 200:
            yield {"type": "error", "message": f"Failed fetching webpage (HTTP {response.status_code})"}
            return
            
        soup = BeautifulSoup(response.text, "html.parser")
        
        
        title = soup.title.string if soup.title else "Untitled Page"
        yield {"type": "found", "message": f"Title: {title.strip()}"}
        
        
        for h1 in soup.find_all("h1")[:5]:
            yield {"type": "found", "message": f"Heading 1: {h1.get_text().strip()}"}
            
        
        links = soup.find_all("a")
        yield {"type": "log", "message": f"Total links detected: {len(links)}"}
        for link in links[:10]:
            href = link.get("href")
            text = link.get_text().strip()
            if href and href.startswith("http"):
                yield {"type": "found", "message": f"Link: {text} -> {href}"}
                
        yield {"type": "success", "message": "Single-page scraping completed successfully."}
    except Exception as e:
        yield {"type": "error", "message": f"Scraping failed: {str(e)}"}
