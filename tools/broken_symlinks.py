import os
import asyncio
from tools.utils import yield_log, yield_error, yield_success

async def run(params: dict):
    dir_path = params.get("dir_path", "").strip()
    delete_links = params.get("delete_links", "false") == "true"
    
    if not dir_path or not os.path.isdir(dir_path):
        yield yield_error("Valid scanning directory is required.")
        return
        
    yield yield_log(f"Scanning {dir_path} recursively for symlinks...")
    
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
            yield yield_log(f"Found {len(broken_links)} broken symlinks.")
            if delete_links:
                for link in broken_links:
                    os.remove(link)
                    yield yield_log(f"Deleted broken link: {link}")
                yield yield_success(f"Successfully deleted {len(broken_links)} broken symlinks.")
            else:
                yield yield_success("Scan finished. Pointers displayed above.")
        else:
            yield yield_success("Scan completed. 0 broken links discovered.")
    except Exception as e:
        yield yield_error(f"Scan failed: {str(e)}")
