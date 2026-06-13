import os
import asyncio

def make_tree(path, prefix=""):
    try:
        items = sorted(os.listdir(path))
    except Exception:
        return []
        
    lines = []
    for idx, item in enumerate(items):
        full_path = os.path.join(path, item)
        is_last = (idx == len(items) - 1)
        connector = "└── " if is_last else "├── "
        lines.append(f"{prefix}{connector}{item}")
        
        if os.path.isdir(full_path):
            extension = "    " if is_last else "│   "
            lines.extend(make_tree(full_path, prefix + extension))
    return lines

async def run(params: dict):
    dir_path = params.get("dir_path", "").strip()
    if not dir_path or not os.path.isdir(dir_path):
        yield {"type": "error", "message": "Valid directory path is required."}
        return
        
    yield {"type": "log", "message": f"Mapping file structure for: {dir_path}"}
    await asyncio.sleep(0.5)
    
    lines = [os.path.basename(dir_path) or dir_path]
    tree_lines = await asyncio.to_thread(make_tree, dir_path)
    lines.extend(tree_lines)
    
    for line in lines[:300]: # Cap logs rendering
        yield {"type": "log", "message": line}
        
    if len(lines) > 300:
        yield {"type": "log", "message": f"... (Truncated {len(lines) - 300} lines)"}
        
    yield {"type": "success", "message": f"Tree rendered. Total entries: {len(lines)}"}
