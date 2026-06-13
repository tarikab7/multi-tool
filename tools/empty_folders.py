import os
import asyncio

async def run(params: dict):
    dir_path = params.get("dir_path", "").strip()
    delete_folders = params.get("delete_folders", "false") == "true"
    
    if not dir_path or not os.path.isdir(dir_path):
        yield {"type": "error", "message": "Valid directory path is required."}
        return
        
    yield {"type": "log", "message": f"Scanning empty folders recursively under {dir_path}..."}
    
    empty_dirs = []
    
    def find_empty_dirs(path):
        try:
            for root, dirs, files in os.walk(path, topdown=False):
                # Check if dir contains absolutely nothing
                if not os.listdir(root):
                    empty_dirs.append(root)
        except Exception:
            pass

    await asyncio.to_thread(find_empty_dirs, dir_path)
    
    if empty_dirs:
        for folder in empty_dirs:
            yield {"type": "found", "message": f"Empty: {folder}"}
            
        if delete_folders:
            for folder in empty_dirs:
                try:
                    os.rmdir(folder)
                    yield {"type": "log", "message": f"Deleted: {folder}"}
                except Exception:
                    pass
            yield {"type": "success", "message": f"Successfully deleted {len(empty_dirs)} empty folders."}
        else:
            yield {"type": "success", "message": f"Found {len(empty_dirs)} empty folders."}
    else:
        yield {"type": "success", "message": "Clean directory tree. 0 empty folders found."}
