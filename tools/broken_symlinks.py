import os
import asyncio

async def run(params: dict):
    dir_path = params.get("dir_path", "").strip()
    delete_links = params.get("delete_links", "false") == "true"
    
    if not dir_path or not os.path.isdir(dir_path):
        yield {"type": "error", "message": "Valid scanning directory is required."}
        return
        
    yield {"type": "log", "message": f"Scanning {dir_path} recursively for symlinks..."}
    
    broken_links = []
    try:
        for root, dirs, files in os.walk(dir_path):
            for name in dirs + files:
                full_path = os.path.join(root, name)
                if os.path.islink(full_path):
                    target = os.readlink(full_path)
                    # Check if target exists
                    if not os.path.exists(full_path):
                        broken_links.append(full_path)
                        yield {"type": "found", "message": f"Broken Link: {name} -> {target}"}
                        
            await asyncio.sleep(0.001)
            
        if broken_links:
            yield {"type": "log", "message": f"Found {len(broken_links)} broken symlinks."}
            if delete_links:
                for link in broken_links:
                    os.remove(link)
                    yield {"type": "log", "message": f"Deleted broken link: {link}"}
                yield {"type": "success", "message": f"Successfully deleted {len(broken_links)} broken symlinks."}
            else:
                yield {"type": "success", "message": "Scan finished. Pointers displayed above."}
        else:
            yield {"type": "success", "message": "Scan completed. 0 broken links discovered."}
    except Exception as e:
        yield {"type": "error", "message": f"Scan failed: {str(e)}"}
