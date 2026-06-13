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
    action = params.get("action", "log") # "log" or "delete" or "restore"
    create_manifest = params.get("create_manifest", False)

    if not directory:
        yield {"type": "error", "message": "Directory path is required."}
        return

    directory = os.path.expanduser(directory)
    if not os.path.isdir(directory):
        yield {"type": "error", "message": f"Directory '{directory}' does not exist."}
        return

    manifest_path = os.path.join(directory, "duplicates_manifest.json")

    if action == "restore":
        if not os.path.isfile(manifest_path):
            yield {"type": "error", "message": f"Backup manifest not found at {manifest_path}."}
            return
        yield {"type": "log", "message": f"Restoring duplicates from {manifest_path}..."}
        try:
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)

            restored_count = 0
            for item in manifest:
                original = item.get("original")
                redundant_list = item.get("redundant", [])

                if not original or not os.path.isfile(original):
                    yield {"type": "log", "message": f"  [ERROR] Original file {original} missing. Skipping restore for its duplicates."}
                    continue

                for rep in redundant_list:
                    # Make sure target directory exists
                    os.makedirs(os.path.dirname(rep), exist_ok=True)
                    if not os.path.exists(rep):
                        shutil.copy2(original, rep)
                        restored_count += 1
                        yield {"type": "log", "message": f"  [RESTORED] {rep} (from {original})"}
                    else:
                        yield {"type": "log", "message": f"  [SKIP] File already exists: {rep}"}
            yield {"type": "success", "message": f"Restore completed. Recovered {restored_count} duplicate files."}
        except Exception as e:
            yield {"type": "error", "message": f"Restore failed: {str(e)}"}
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

    # Create a flat list of all paths to hash
    all_paths = [path for paths in potential_duplicates.values() for path in paths]
    total_files_to_hash = len(all_paths)

    # Process in batches to avoid creating too many threads simultaneously
    batch_size = 50
    for i in range(0, total_files_to_hash, batch_size):
        batch_paths = all_paths[i:i+batch_size]
        tasks = [asyncio.to_thread(get_file_sha256, path) for path in batch_paths]
        results = await asyncio.gather(*tasks)

        for path, file_hash in zip(batch_paths, results):
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

    manifest_data = []

    for idx, (f_hash, paths) in enumerate(duplicates.items(), 1):
        # Sort paths by modification time (keep the oldest)
        paths.sort(key=lambda p: os.path.getmtime(p))
        original = paths[0]
        redundant = paths[1:]
        
        file_size = os.path.getsize(original)
        size_str = f"{file_size / (1024*1024):.2f} MB" if file_size > 1024*1024 else f"{file_size / 1024:.2f} KB"

        yield {"type": "log", "message": f"Group #{idx} (Size: {size_str}, Hash: {f_hash[:8]}):"}
        yield {"type": "log", "message": f"  [KEEP] {original}"}
        
        deleted_in_this_group = []
        for rep in redundant:
            saved_bytes += file_size
            if action == "delete":
                try:
                    os.remove(rep)
                    deleted_count += 1
                    deleted_in_this_group.append(rep)
                    yield {"type": "log", "message": f"  [DELETED] {rep}"}
                except Exception as e:
                    yield {"type": "log", "message": f"  [ERROR] Failed to delete {rep}: {str(e)}"}
            else:
                yield {"type": "log", "message": f"  [DUPLICATE] {rep}"}

        if action == "delete" and create_manifest and deleted_in_this_group:
            manifest_data.append({
                "original": original,
                "hash": f_hash,
                "redundant": deleted_in_this_group
            })

    if action == "delete" and create_manifest and manifest_data:
        try:
            with open(manifest_path, 'w') as f:
                json.dump(manifest_data, f, indent=4)
            yield {"type": "log", "message": f"Backup manifest created at {manifest_path}."}
        except Exception as e:
            yield {"type": "error", "message": f"Failed to write backup manifest: {str(e)}"}

    saved_mb = saved_bytes / (1024 * 1024)
    if action == "delete":
        yield {"type": "success", "message": f"Completed. Deleted {deleted_count} duplicate files. Reclaimed {saved_mb:.2f} MB."}
    else:
        yield {"type": "success", "message": f"Completed. Found {sum(len(p)-1 for p in duplicates.values())} duplicate files. Potential savings: {saved_mb:.2f} MB."}
