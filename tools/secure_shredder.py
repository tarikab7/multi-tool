import os
import random
import string
import asyncio

def shred_file_sync(filepath, passes):
    try:
        size = os.path.getsize(filepath)
        if size == 0:
            os.remove(filepath)
            return True

        # Open in write-binary mode
        with open(filepath, 'ba+', buffering=0) as f:
            for p in range(passes):
                # Seek to beginning
                f.seek(0)
                # Write pass pattern (alternating random bytes and zeros)
                chunk_size = 65536
                bytes_written = 0
                while bytes_written < size:
                    to_write = min(chunk_size, size - bytes_written)
                    if p % 2 == 0:
                        # Write random noise pass
                        f.write(os.urandom(to_write))
                    else:
                        # Write zero pass
                        f.write(b'\x00' * to_write)
                    bytes_written += to_write
                # Flush OS disk buffer
                f.flush()
                os.fsync(f.fileno())

        # Rename to clear filename metadata (to prevent forensic file table lookup)
        random_name = ''.join(random.choices(string.ascii_lowercase, k=10))
        temp_path = os.path.join(os.path.dirname(filepath), random_name)
        os.rename(filepath, temp_path)
        
        # Delete file
        os.remove(temp_path)
        return True
    except Exception:
        return False

async def run(params: dict):
    target_path = params.get("target_path", "").strip()
    passes_str = params.get("passes", "3").strip()

    if not target_path:
        yield {"type": "error", "message": "Target path is required."}
        return

    target_path = os.path.expanduser(target_path)
    if not os.path.exists(target_path):
        yield {"type": "error", "message": f"Target path '{target_path}' does not exist."}
        return

    try:
        passes = int(passes_str)
        passes = max(1, min(10, passes)) # bound passes between 1 and 10
    except ValueError:
        yield {"type": "error", "message": "Passes must be an integer."}
        return

    files_to_shred = []
    if os.path.isfile(target_path):
        files_to_shred.append(target_path)
    elif os.path.isdir(target_path):
        # Shred directory recursively (all files)
        for root, _, files in os.walk(target_path):
            for file in files:
                files_to_shred.append(os.path.join(root, file))
                
    total_files = len(files_to_shred)
    if total_files == 0:
        if os.path.isdir(target_path):
            os.rmdir(target_path)
        yield {"type": "log", "message": "No files found to shred."}
        yield {"type": "success", "message": "Finished shredding."}
        return

    yield {"type": "log", "message": f"Starting secure shredding of {total_files} file(s) ({passes} passes)..."}

    shredded_count = 0
    for idx, filepath in enumerate(files_to_shred, 1):
        filename = os.path.basename(filepath)
        yield {"type": "log", "message": f"[{idx}/{total_files}] Shredding '{filename}'..."}
        
        success = await asyncio.to_thread(shred_file_sync, filepath, passes)
        if success:
            shredded_count += 1
        else:
            yield {"type": "log", "message": f"[{idx}/{total_files}] Failed to secure shred: {filename}"}

        progress = (idx / total_files) * 100
        yield {"type": "progress", "percent": progress}

    # If directory, clean up empty directories
    if os.path.isdir(target_path):
        for root, dirs, _ in os.walk(target_path, topdown=False):
            for d in dirs:
                try:
                    os.rmdir(os.path.join(root, d))
                except Exception:
                    pass
        try:
            os.rmdir(target_path)
        except Exception:
            pass

    yield {"type": "success", "message": f"Completed. Securely shredded {shredded_count} of {total_files} files."}
