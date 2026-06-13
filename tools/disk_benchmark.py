import os
import time
import asyncio
import tempfile

async def run(params: dict):
    test_file_size_mb = int(params.get("size_mb", "50"))
    yield {"type": "log", "message": f"Creating {test_file_size_mb}MB test file for throughput benchmark..."}
    
    block_size = 1024 * 1024 # 1MB
    data = b"X" * block_size
    
    temp_file = tempfile.mktemp()
    
    try:
        # Write benchmark
        t_start_w = time.time()
        with open(temp_file, "wb") as f:
            for _ in range(test_file_size_mb):
                f.write(data)
                f.flush()
                os.fsync(f.fileno())
        t_end_w = time.time()
        write_time = t_end_w - t_start_w
        write_speed = test_file_size_mb / write_time
        
        yield {"type": "found", "message": f"Write speed: {write_speed:.2f} MB/sec"}
        await asyncio.sleep(0.5)
        
        # Read benchmark
        t_start_r = time.time()
        with open(temp_file, "rb") as f:
            while True:
                chunk = f.read(block_size)
                if not chunk:
                    break
        t_end_r = time.time()
        read_time = t_end_r - t_start_r
        read_speed = test_file_size_mb / read_time
        
        yield {"type": "found", "message": f"Read speed: {read_speed:.2f} MB/sec"}
        
        if os.path.exists(temp_file):
            os.remove(temp_file)
            
        yield {"type": "success", "message": f"Benchmark completed successfully."}
    except Exception as e:
        if os.path.exists(temp_file):
            os.remove(temp_file)
        yield {"type": "error", "message": f"Benchmark failed: {str(e)}"}
