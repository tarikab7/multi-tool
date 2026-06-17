import os
import asyncio

def get_folder_size_sync(folder_path):
    total_size = 0
    stack = [folder_path]
    while stack:
        current = stack.pop()
        try:
            with os.scandir(current) as it:
                for entry in it:
                    if entry.is_symlink():
                        continue
                    if entry.is_file():
                        total_size += entry.stat(follow_symlinks=False).st_size
                    elif entry.is_dir():
                        stack.append(entry.path)
        except Exception:
            pass
    return total_size

def format_size(size_bytes):
    if size_bytes >= 1024**3:
        return f"{size_bytes / (1024**3):.2f} GB"
    elif size_bytes >= 1024**2:
        return f"{size_bytes / (1024**2):.2f} MB"
    elif size_bytes >= 1024:
        return f"{size_bytes / 1024:.2f} KB"
    return f"{size_bytes} Bytes"

async def run(params: dict):
    directory = params.get("directory", "").strip()

    if not directory:
        yield {"type": "error", "message": "Directory path is required."}
        return

    directory = os.path.expanduser(directory)
    if not os.path.isdir(directory):
        yield {"type": "error", "message": f"Directory '{directory}' does not exist."}
        return

    yield {"type": "log", "message": f"Scanning directory sizes in: {directory}..."}

    subfolders = []
    try:
        # Get list of immediate subdirectories
        with os.scandir(directory) as it:
            for entry in it:
                if entry.is_dir():
                    subfolders.append(entry.path)
    except Exception as e:
        yield {"type": "error", "message": f"Failed listing directories: {str(e)}"}
        return

    total_folders = len(subfolders)
    if total_folders == 0:
        yield {"type": "log", "message": "No subdirectories found."}
        # Measure size of files inside main folder
        main_files_size = 0
        try:
            with os.scandir(directory) as it:
                main_files_size = sum(entry.stat(follow_symlinks=False).st_size for entry in it if entry.is_file() and not entry.is_symlink())
        except Exception:
            pass
        yield {"type": "log", "message": f"Folder size (direct files only): {format_size(main_files_size)}"}
        yield {"type": "success", "message": "Analysis complete."}
        return

    yield {"type": "log", "message": f"Found {total_folders} subfolder(s). Calculating sizes recursively..."}

    folder_sizes = []
    for idx, path in enumerate(subfolders, 1):
        name = os.path.basename(path)
        yield {"type": "log", "message": f"[{idx}/{total_folders}] Calculating: {name}..."}
        
        # Calculate size in threadpool
        size = await asyncio.to_thread(get_folder_size_sync, path)
        folder_sizes.append((name, size))
        
        progress = (idx / total_folders) * 100
        yield {"type": "progress", "percent": progress}

    # Sort folders by size descending
    folder_sizes.sort(key=lambda x: x[1], reverse=True)

    yield {"type": "log", "message": "\nSize Summary (Largest First):"}
    for name, size in folder_sizes:
        yield {"type": "log", "message": f"  📁 {name:<25} ➔ {format_size(size)}"}

    total_sum = sum(size for _, size in folder_sizes)
    yield {"type": "log", "message": f"\nTotal size of all subfolders: {format_size(total_sum)}"}
    yield {"type": "success", "message": "Folder size analysis completed."}
