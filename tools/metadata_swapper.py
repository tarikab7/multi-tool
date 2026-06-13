import os
import asyncio

def swap_file_dates(file_path):
    # Get the current file timestamps
    stat_info = os.stat(file_path)
    
    # Extract access time, modified time, and metadata change time
    # On Linux, ctime is metadata change, mtime is modification, atime is access.
    # The original script did: os.utime(file_path, (modified_time, creation_time))
    # which effectively sets atime = modified_time, mtime = ctime.
    # Let's keep this exact legacy behavior but wrapped safely.
    mtime = stat_info.st_mtime
    ctime = stat_info.st_ctime
    
    os.utime(file_path, (mtime, ctime))
    return True

async def run(params: dict):
    directory = params.get("directory", "").strip()

    if not directory:
        yield {"type": "error", "message": "Directory path is required."}
        return

    directory = os.path.expanduser(directory)
    if not os.path.exists(directory):
        yield {"type": "error", "message": f"Directory '{directory}' does not exist."}
        return

    # Gather files
    files_to_process = []
    for root, _, files in os.walk(directory):
        for file in files:
            files_to_process.append(os.path.join(root, file))

    total_files = len(files_to_process)
    yield {"type": "log", "message": f"Found {total_files} file(s) to swap dates."}

    if total_files == 0:
        yield {"type": "success", "message": "Finished. 0 files processed."}
        return

    swapped_count = 0
    error_count = 0

    for idx, file_path in enumerate(files_to_process, 1):
        filename = os.path.basename(file_path)
        try:
            success = await asyncio.to_thread(swap_file_dates, file_path)
            if success:
                swapped_count += 1
                yield {"type": "log", "message": f"[{idx}/{total_files}] Swapped dates for: {filename}"}
            else:
                error_count += 1
        except Exception as e:
            error_count += 1
            yield {"type": "log", "message": f"[{idx}/{total_files}] Error swapping {filename}: {str(e)}"}

        if idx % 10 == 0 or idx == total_files:
            yield {"type": "progress", "percent": (idx / total_files) * 100}

    yield {"type": "success", "message": f"Completed. Swapped {swapped_count} files. Errors: {error_count}."}
