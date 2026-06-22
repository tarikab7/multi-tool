import os
import asyncio

async def run(params: dict):
    file_path = params.get("file_path", "").strip()
    chunk_size_mb = int(params.get("chunk_size_mb", "10"))
    mode = params.get("mode", "split").strip() 
    
    if not file_path:
        yield {"type": "error", "message": "Valid file path is required."}
        return
        
    chunk_size = chunk_size_mb * 1024 * 1024
    
    try:
        if mode == "split":
            if not os.path.exists(file_path):
                yield {"type": "error", "message": "File does not exist."}
                return
                
            yield {"type": "log", "message": f"Splitting {os.path.basename(file_path)} into {chunk_size_mb}MB chunks..."}
            part_num = 1
            with open(file_path, "rb") as f_in:
                while True:
                    chunk = f_in.read(chunk_size)
                    if not chunk:
                        break
                    part_name = f"{file_path}.part{part_num}"
                    with open(part_name, "wb") as f_out:
                        f_out.write(chunk)
                    yield {"type": "log", "message": f"Created chunk: {os.path.basename(part_name)}"}
                    part_num += 1
                    await asyncio.sleep(0.01)
            yield {"type": "success", "message": f"File successfully split into {part_num - 1} chunks."}
            
        else: 
            
            base_file = file_path.replace(".part1", "")
            yield {"type": "log", "message": f"Assembling chunks back into: {os.path.basename(base_file)}..."}
            
            part_num = 1
            with open(base_file, "wb") as f_out:
                while True:
                    part_name = f"{base_file}.part{part_num}"
                    if not os.path.exists(part_name):
                        break
                    with open(part_name, "rb") as f_in:
                        f_out.write(f_in.read())
                    yield {"type": "log", "message": f"Merged chunk: {os.path.basename(part_name)}"}
                    part_num += 1
                    await asyncio.sleep(0.01)
                    
            if part_num == 1:
                yield {"type": "error", "message": "No parts (.part1, .part2...) found to merge."}
            else:
                yield {"type": "success", "message": f"Successfully joined {part_num - 1} chunks into {base_file}."}
    except Exception as e:
        yield {"type": "error", "message": f"Operation failed: {str(e)}"}
