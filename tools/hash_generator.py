import os
import hashlib
import asyncio

def _compute_hashes(file_path: str):
    hashes = {
        "md5": hashlib.md5(),
        "sha1": hashlib.sha1(),
        "sha256": hashlib.sha256(),
        "sha512": hashlib.sha512()
    }
    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            for h in hashes.values():
                h.update(chunk)
    return hashes

async def run(params: dict):
    file_path = params.get("file_path", "").strip()
    
    if not file_path or not os.path.exists(file_path):
        yield {"type": "error", "message": "Valid file path is required."}
        return
        
    yield {"type": "log", "message": f"Hashing {os.path.basename(file_path)} in blocks..."}
    
    try:
        # Offload file reading and hashing to a background thread
        hashes = await asyncio.to_thread(_compute_hashes, file_path)
                
        for name, h in hashes.items():
            hex_val = h.hexdigest()
            yield {"type": "found", "message": f"{name.upper()}: {hex_val}"}
            
        yield {"type": "success", "message": "Hash generation completed."}
    except Exception as e:
        yield {"type": "error", "message": f"Error hashing file: {str(e)}"}
