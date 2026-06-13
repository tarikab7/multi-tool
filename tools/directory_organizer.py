import os
import shutil
import asyncio

# Extension categories mapping
CATEGORIES = {
    "Images": ('.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tiff', '.heic', '.heif', '.svg', '.raw'),
    "Documents": ('.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt', '.rtf', '.odt', '.csv', '.ods', '.odp'),
    "Audios": ('.mp3', '.wav', '.flac', '.aac', '.m4a', '.ogg', '.wma', '.alac'),
    "Videos": ('.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm', '.m4v'),
    "Archives": ('.zip', '.rar', '.tar', '.gz', '.7z', '.bz2', '.xz', '.tar.gz', '.tar.xz', '.tgz'),
    "Executables": ('.exe', '.msi', '.deb', '.rpm', '.appimage', '.sh', '.bat', '.cmd'),
    "Code": ('.py', '.js', '.html', '.css', '.c', '.cpp', '.java', '.go', '.rs', '.json', '.xml', '.sh')
}

def organize_files_sync(directory):
    moved_files = {}
    
    # List files in the target directory (only top level to prevent flattening nested directories)
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        
        # Skip folders
        if os.path.isdir(filepath):
            continue
            
        ext = os.path.splitext(filename)[1].lower()
        if not ext:
            continue

        # Find matching category
        target_cat = "Others"
        for category, extensions in CATEGORIES.items():
            if ext in extensions:
                target_cat = category
                break

        # Move file
        target_dir = os.path.join(directory, target_cat)
        os.makedirs(target_dir, exist_ok=True)
        
        dest_path = os.path.join(target_dir, filename)
        
        # Avoid overwriting files: rename if name collision exists
        base, extension = os.path.splitext(filename)
        counter = 1
        while os.path.exists(dest_path):
            new_filename = f"{base}_{counter}{extension}"
            dest_path = os.path.join(target_dir, new_filename)
            counter += 1

        try:
            shutil.move(filepath, dest_path)
            moved_files.setdefault(target_cat, []).append(filename)
        except Exception:
            pass

    return moved_files

async def run(params: dict):
    directory = params.get("directory", "").strip()

    if not directory:
        yield {"type": "error", "message": "Directory path is required."}
        return

    directory = os.path.expanduser(directory)
    if not os.path.isdir(directory):
        yield {"type": "error", "message": f"Directory '{directory}' does not exist."}
        return

    yield {"type": "log", "message": f"Organizing directory: {directory}"}
    
    moved_files = await asyncio.to_thread(organize_files_sync, directory)
    
    total_moved = sum(len(files) for files in moved_files.values())
    if total_moved == 0:
        yield {"type": "log", "message": "No files found to organize."}
        yield {"type": "success", "message": "Finished. Organized 0 files."}
        return

    # Print summary
    yield {"type": "log", "message": f"Organized {total_moved} file(s) into category folders:"}
    for cat, files in moved_files.items():
        yield {"type": "log", "message": f"  📁 {cat}/: moved {len(files)} file(s)"}

    yield {"type": "progress", "percent": 100.0}
    yield {"type": "success", "message": f"Successfully organized {total_moved} files."}
