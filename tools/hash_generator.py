import os
import hashlib
import asyncio

async def run(params: dict):
    file_path = params.get("file_path", "").strip()
    
    if not file_path or not os.path.exists(file_path):
        yield {"type": "error", "message": "Valid file path is required."}
        return
        
    yield {"type": "log", "message": f"Hashing {os.path.basename(file_path)} in blocks..."}
    
    hashes = {
        "md5": hashlib.md5(),
        "sha1": hashlib.sha1(),
        "sha256": hashlib.sha256(),
        "sha512": hashlib.sha512()
    }
    
    try:
        
        with open(file_path, "rb") as f:
            while True:
                chunk = f.read(65536)
                if not chunk:
                    break
                for h in hashes.values():
                    h.update(chunk)
                await asyncio.sleep(0.001) 
                
        for name, h in hashes.items():
            hex_val = h.hexdigest()
            yield {"type": "found", "message": f"{name.upper()}: {hex_val}"}
            
        yield {"type": "success", "message": "Hash generation completed."}
    except Exception as e:
        yield {"type": "error", "message": f"Error hashing file: {str(e)}"}
