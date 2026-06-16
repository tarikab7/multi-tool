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

def scan_directory(directory, min_size_bytes):
    all_files = []
    
    def _scan(path):
        try:
            with os.scandir(path) as it:
                for entry in it:
                    if entry.is_symlink():
                        continue
                    elif entry.is_dir():
                        _scan(entry.path)
                    elif entry.is_file():
                        try:
                            stat = entry.stat()
                            if stat.st_size >= min_size_bytes:
                                all_files.append(entry.path)
                        except Exception:
                            pass
        except Exception:
            pass

    _scan(directory)
    return all_files

async def run(params: dict):
    directory = params.get("directory", "").strip()
    min_size_kb = params.get("min_size_kb", "0").strip()
    action = params.get("action", "log") # "log" or "delete"

    if not directory:
        yield {"type": "error", "message": "Directory path is required."}
        return

    directory = os.path.expanduser(directory)
    if not os.path.isdir(directory):
        yield {"type": "error", "message": f"Directory '{directory}' does not exist."}
        return

    if action == "restore":
        manifest_path = os.path.join(directory, "duplicates_manifest.json")
        if not os.path.exists(manifest_path):
            yield {"type": "error", "message": f"Manifest not found: {manifest_path}"}
            return

        yield {"type": "log", "message": f"Reading manifest from {manifest_path}..."}
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
        except Exception as e:
            yield {"type": "error", "message": f"Failed to read manifest: {str(e)}"}
            return

        restored_count = 0
        failed_count = 0
        for duplicate_path, original_path in manifest.items():
            if not os.path.exists(original_path):
                yield {"type": "log", "message": f"  [ERROR] Original file missing: {original_path}"}
                failed_count += 1
                continue

            if os.path.exists(duplicate_path):
                yield {"type": "log", "message": f"  [SKIP] File already exists at: {duplicate_path}"}
                continue

            try:
                # Ensure the directory exists
                os.makedirs(os.path.dirname(duplicate_path), exist_ok=True)
                shutil.copy2(original_path, duplicate_path)
                restored_count += 1
                yield {"type": "log", "message": f"  [RESTORED] {duplicate_path} from {original_path}"}
            except Exception as e:
                yield {"type": "log", "message": f"  [ERROR] Failed to restore {duplicate_path}: {str(e)}"}
                failed_count += 1

        yield {"type": "success", "message": f"Restore completed. Restored: {restored_count}, Failed: {failed_count}."}
        return

    try:
        min_size_bytes = int(float(min_size_kb) * 1024)
    except ValueError:
        yield {"type": "error", "message": "Min size must be a number."}
        return

    yield {"type": "log", "message": f"Scanning '{directory}' for files..."}
    all_files = await asyncio.to_thread(scan_directory, directory, min_size_bytes)
    
    total_files_to_hash = len(all_files)
    if total_files_to_hash == 0:
        yield {"type": "log", "message": "No files found to check."}
        yield {"type": "success", "message": "Scan completed. 0 files found."}
        return

    yield {"type": "log", "message": f"Found {total_files_to_hash} files. Hashing contents..."}

    # Map hash -> list of filepaths
    hash_map = {}
    processed_count = 0

    semaphore = asyncio.Semaphore(50)

    async def hash_file_with_sem(path):
        async with semaphore:
            return path, await asyncio.to_thread(get_file_sha256, path)

    tasks = [asyncio.create_task(hash_file_with_sem(path)) for path in all_files]

    for coro in asyncio.as_completed(tasks):
        path, file_hash = await coro
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
            if action in ("delete", "delete_backup"):
                try:
                    os.remove(rep)
                    deleted_count += 1
                    if action == "delete_backup":
                        manifest[rep] = original
                    yield {"type": "log", "message": f"  [DELETED] {rep}"}
                except Exception as e:
                    yield {"type": "log", "message": f"  [ERROR] Failed to delete {rep}: {str(e)}"}
            else:
                yield {"type": "log", "message": f"  [DUPLICATE] {rep}"}

    if action == "delete_backup" and manifest:
        manifest_path = os.path.join(directory, "duplicates_manifest.json")
        try:
            with open(manifest_path, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=4)
            yield {"type": "log", "message": f"Saved backup manifest to {manifest_path}"}
        except Exception as e:
            yield {"type": "log", "message": f"Failed to save manifest: {str(e)}"}

    saved_mb = saved_bytes / (1024 * 1024)
    if action in ("delete", "delete_backup"):
        yield {"type": "success", "message": f"Completed. Deleted {deleted_count} duplicate files. Reclaimed {saved_mb:.2f} MB."}
    else:
        yield {"type": "success", "message": f"Completed. Found {sum(len(p)-1 for p in duplicates.values())} duplicate files. Potential savings: {saved_mb:.2f} MB."}
