import os
import hashlib
import asyncio
import json
import shutil

def get_file_sha256(filepath):
    hasher = hashlib.sha256()
    try:
        with open(filepath, 'rb') as f:
            # Read in 64kb chunks
            for chunk in iter(lambda: f.read(65536), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception:
        return None

def scan_duplicates(directory, min_size_bytes):
    # Map size -> list of filepaths
    size_map = {}
    
    # 1. Group files by size first (extremely fast compared to hashing everything!)
    for root, _, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            try:
                # Skip symlinks
                if os.path.islink(filepath):
                    continue
                size = os.path.getsize(filepath)
                if size >= min_size_bytes:
                    size_map.setdefault(size, []).append(filepath)
            except Exception:
                continue

    # Filter out sizes that have only 1 file
    potential_duplicates = {size: paths for size, paths in size_map.items() if len(paths) > 1}
    return potential_duplicates

async def run(params: dict):
    directory = params.get("directory", "").strip()
    min_size_kb = params.get("min_size_kb", "0").strip()
    action = params.get("action", "log") # "log", "delete", "backup_delete", "restore"

    if not directory:
        yield {"type": "error", "message": "Directory path is required."}
        return

    directory = os.path.expanduser(directory)
    if not os.path.isdir(directory):
        yield {"type": "error", "message": f"Directory '{directory}' does not exist."}
        return

    manifest_path = os.path.join(directory, "duplicates_manifest.json")

    if action == "restore":
        yield {"type": "log", "message": f"Attempting to restore from '{manifest_path}'..."}
        if not os.path.isfile(manifest_path):
            yield {"type": "error", "message": f"Manifest file not found at {manifest_path}."}
            return

        try:
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
        except Exception as e:
            yield {"type": "error", "message": f"Failed to read manifest: {str(e)}"}
            return

        if not manifest:
            yield {"type": "log", "message": "Manifest is empty. Nothing to restore."}
            yield {"type": "success", "message": "Restore completed. 0 files restored."}
            return

        restored_count = 0
        for deleted_path, original_path in manifest.items():
            if not os.path.exists(original_path):
                yield {"type": "log", "message": f"  [ERROR] Cannot restore {deleted_path}. Original {original_path} is missing."}
                continue

            try:
                # Ensure the target directory exists
                os.makedirs(os.path.dirname(deleted_path), exist_ok=True)
                shutil.copy2(original_path, deleted_path)
                restored_count += 1
                yield {"type": "log", "message": f"  [RESTORED] {deleted_path}"}
            except Exception as e:
                yield {"type": "log", "message": f"  [ERROR] Failed to restore {deleted_path}: {str(e)}"}

        yield {"type": "success", "message": f"Restore completed. Restored {restored_count} files from manifest."}
        return

    try:
        min_size_bytes = int(float(min_size_kb) * 1024)
    except ValueError:
        yield {"type": "error", "message": "Min size must be a number."}
        return

    yield {"type": "log", "message": f"Scanning '{directory}' for files..."}
    potential_duplicates = await asyncio.to_thread(scan_duplicates, directory, min_size_bytes)
    
    total_potential_groups = len(potential_duplicates)
    if total_potential_groups == 0:
        yield {"type": "log", "message": "No duplicate files found."}
        yield {"type": "success", "message": "Scan completed. 0 duplicate groups found."}
        return

    yield {"type": "log", "message": f"Found {total_potential_groups} groups of identical sizes. Hashing contents..."}

    # Map hash -> list of filepaths
    hash_map = {}
    processed_count = 0
    total_files_to_hash = sum(len(paths) for paths in potential_duplicates.values())


    # Create hashing tasks for all potential duplicates
    # We must ensure the path stays associated with its hash result when completing out of order
    async def hash_file_with_path(filepath):
        h = await asyncio.to_thread(get_file_sha256, filepath)
        return (filepath, h)

    tasks = []
    for paths in potential_duplicates.values():
        for path in paths:
            tasks.append(hash_file_with_path(path))

    # Process tasks as they complete
    for future in asyncio.as_completed(tasks):
        path, file_hash = await future
        if file_hash:
            hash_map.setdefault(file_hash, []).append(path)
            
        processed_count += 1
        if processed_count % 10 == 0 or processed_count == total_files_to_hash:
            progress = (processed_count / total_files_to_hash) * 100
            yield {"type": "progress", "percent": progress}

    # Find actual duplicates (hashes with > 1 file)
    duplicates = {h: paths for h, paths in hash_map.items() if len(paths) > 1}
    
    if not duplicates:
        yield {"type": "log", "message": "No duplicate file contents found."}
        yield {"type": "success", "message": "Scan completed. 0 duplicate groups found."}
        return

    yield {"type": "log", "message": f"Found {len(duplicates)} duplicate content group(s):"}
    
    saved_bytes = 0
    deleted_count = 0
    manifest = {}

    for idx, (f_hash, paths) in enumerate(duplicates.items(), 1):
        # Sort paths by modification time (keep the oldest)
        paths.sort(key=lambda p: os.path.getmtime(p))
        original = paths[0]
        redundant = paths[1:]
        
        file_size = os.path.getsize(original)
        size_str = f"{file_size / (1024*1024):.2f} MB" if file_size > 1024*1024 else f"{file_size / 1024:.2f} KB"

        yield {"type": "log", "message": f"Group #{idx} (Size: {size_str}, Hash: {f_hash[:8]}):"}
        yield {"type": "log", "message": f"  [KEEP] {original}"}
        
        for rep in redundant:
            saved_bytes += file_size
            if action in ("delete", "backup_delete"):
                try:
                    os.remove(rep)
                    deleted_count += 1
                    if action == "backup_delete":
                        manifest[rep] = original
                    yield {"type": "log", "message": f"  [DELETED] {rep}"}
                except Exception as e:
                    yield {"type": "log", "message": f"  [ERROR] Failed to delete {rep}: {str(e)}"}
            else:
                yield {"type": "log", "message": f"  [DUPLICATE] {rep}"}

    if action == "backup_delete" and manifest:
        try:
            with open(manifest_path, 'w') as f:
                json.dump(manifest, f, indent=4)
            yield {"type": "log", "message": f"Saved backup manifest to {manifest_path}"}
        except Exception as e:
            yield {"type": "log", "message": f"  [ERROR] Failed to save backup manifest: {str(e)}"}

    saved_mb = saved_bytes / (1024 * 1024)
    if action in ("delete", "backup_delete"):
        yield {"type": "success", "message": f"Completed. Deleted {deleted_count} duplicate files. Reclaimed {saved_mb:.2f} MB."}
    else:
        yield {"type": "success", "message": f"Completed. Found {sum(len(p)-1 for p in duplicates.values())} duplicate files. Potential savings: {saved_mb:.2f} MB."}
