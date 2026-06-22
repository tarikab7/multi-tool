import os
import asyncio
import requests

def load_wordlist(file_path):
    if not os.path.isfile(file_path):
        return []
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            return [line.strip() for line in file if line.strip()]
    except Exception:
        return []

async def run(params: dict):
    mode = params.get("mode", "end") 
    base_url = params.get("base_url", "").strip()
    end_url = params.get("end_url", "").strip()
    wordlist_file = params.get("wordlist_file", "").strip()

    if not base_url:
        yield {"type": "error", "message": "Base URL is required."}
        return
    if not wordlist_file:
        yield {"type": "error", "message": "Wordlist file path is required."}
        return

    
    if mode == "middle":
        base_url = base_url.rstrip('/') + '/'
        end_url = '/' + end_url.lstrip('/')
    else:
        base_url = base_url.rstrip('/') + '/'

    wordlist_file = os.path.expanduser(wordlist_file)
    if not os.path.isfile(wordlist_file):
        yield {"type": "error", "message": f"Wordlist file '{wordlist_file}' not found."}
        return

    yield {"type": "log", "message": f"Loading directories from: {wordlist_file}"}
    directories = await asyncio.to_thread(load_wordlist, wordlist_file)
    total_directories = len(directories)

    yield {"type": "log", "message": f"Loaded {total_directories} directory names. Starting scan..."}

    if total_directories == 0:
        yield {"type": "success", "message": "Finished. Wordlist was empty."}
        return

    found_directories = []
    
    
    for idx, directory in enumerate(directories, 1):
        
        try:
            
            await asyncio.sleep(0.01)
        except asyncio.CancelledError:
            yield {"type": "log", "message": "Scan cancelled by user."}
            break

        if mode == "middle":
            url = f"{base_url}{directory}{end_url}"
        else:
            url = f"{base_url}{directory}"

        try:
            
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(
                None, 
                lambda: requests.head(url, allow_redirects=True, timeout=5)
            )
            
            status_code = response.status_code
            if not (400 <= status_code < 600):
                found_info = {
                    "directory": directory,
                    "url": url,
                    "final_url": response.url,
                    "status_code": status_code
                }
                found_directories.append(found_info)
                yield {
                    "type": "found", 
                    "message": f"Found: {directory} (Status: {status_code}) -> {response.url}",
                    "data": found_info
                }
        except Exception as e:
            
            pass

        if idx % 10 == 0 or idx == total_directories:
            yield {"type": "progress", "percent": (idx / total_directories) * 100}

    yield {
        "type": "success", 
        "message": f"Scan finished. Found {len(found_directories)} valid directories.",
        "results": found_directories
    }
