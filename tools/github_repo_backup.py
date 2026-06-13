import os
import requests
import asyncio

async def run(params: dict):
    repo_url = params.get("repo_url", "").strip() # e.g. https://github.com/user/repo
    dest_dir = params.get("dest_dir", "github_backups").strip()
    
    if not repo_url:
        yield {"type": "error", "message": "GitHub repository URL is required."}
        return
        
    # Extract owner and repo name
    parts = repo_url.rstrip("/").split("/")
    if len(parts) < 2:
        yield {"type": "error", "message": "Invalid repo URL structure."}
        return
        
    owner = parts[-2]
    repo = parts[-1]
    
    os.makedirs(dest_dir, exist_ok=True)
    dest_path = os.path.join(dest_dir, f"{repo}_main.zip")
    
    zip_url = f"https://github.com/{owner}/{repo}/archive/refs/heads/main.zip"
    # Fallback to master
    zip_url_master = f"https://github.com/{owner}/{repo}/archive/refs/heads/master.zip"
    
    yield {"type": "log", "message": f"Requesting backup archive for {owner}/{repo}..."}
    
    try:
        response = await asyncio.to_thread(requests.get, zip_url, timeout=15)
        if response.status_code != 200:
            yield {"type": "log", "message": "Main branch failed. Trying master branch..."}
            response = await asyncio.to_thread(requests.get, zip_url_master, timeout=15)
            
        if response.status_code == 200:
            with open(dest_path, "wb") as f:
                f.write(response.content)
            yield {"type": "success", "message": f"Backup saved successfully: {dest_path}"}
        else:
            yield {"type": "error", "message": f"Failed accessing repo archive (HTTP {response.status_code})"}
    except Exception as e:
        yield {"type": "error", "message": f"Backup connection error: {str(e)}"}
