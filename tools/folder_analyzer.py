import os
import asyncio
from tools.utils import yield_log, yield_success, yield_error, yield_progress

def get_folder_size_sync(folder_path):
    total_size = 0
    try:
        for root, _, files in os.walk(folder_path):
            for file in files:
                filepath = os.path.join(root, file)
                # Skip symlinks to avoid infinite loops
                if not os.path.islink(filepath):
                    total_size += os.path.getsize(filepath)
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
        yield yield_error("Directory path is required.")
        return

    directory = os.path.expanduser(directory)
    if not os.path.isdir(directory):
        yield yield_error(f"Directory '{directory}' does not exist.")
        return

    yield yield_log(f"Scanning directory sizes in: {directory}...")

    subfolders = []
    try:
        # Get list of immediate subdirectories
        entries = os.listdir(directory)
        for entry in entries:
            path = os.path.join(directory, entry)
            if os.path.isdir(path):
                subfolders.append(path)
    except Exception as e:
        yield yield_error(f"Failed listing directories: {str(e)}")
        return

    total_folders = len(subfolders)
    if total_folders == 0:
        yield yield_log("No subdirectories found.")
        # Measure size of files inside main folder
        main_files_size = sum(os.path.getsize(os.path.join(directory, f)) for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f)))
        yield yield_log(f"Folder size (direct files only): {format_size(main_files_size)}")
        yield yield_success("Analysis complete.")
        return

    yield yield_log(f"Found {total_folders} subfolder(s). Calculating sizes recursively...")

    folder_sizes = []
    for idx, path in enumerate(subfolders, 1):
        name = os.path.basename(path)
        yield yield_log(f"[{idx}/{total_folders}] Calculating: {name}...")
        
        # Calculate size in threadpool
        size = await asyncio.to_thread(get_folder_size_sync, path)
        folder_sizes.append((name, size))
        
        progress = (idx / total_folders) * 100
        yield yield_progress(progress)

    # Sort folders by size descending
    folder_sizes.sort(key=lambda x: x[1], reverse=True)

    yield yield_log("\nSize Summary (Largest First):")
    for name, size in folder_sizes:
        yield yield_log(f"  📁 {name:<25} ➔ {format_size(size)}")

    total_sum = sum(size for _, size in folder_sizes)
    yield yield_log(f"\nTotal size of all subfolders: {format_size(total_sum)}")
    yield yield_success("Folder size analysis completed.")
