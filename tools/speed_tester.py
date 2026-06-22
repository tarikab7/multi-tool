import time
import requests
import asyncio


SPEED_TEST_URL = "https://speed.cloudflare.com/__down?bytes=10485760"

def run_download_test():
    try:
        start_time = time.time()
        
        
        response = requests.get(SPEED_TEST_URL, stream=True, timeout=15)
        response.raise_for_status()

        total_bytes = 10485760 
        bytes_downloaded = 0
        chunk_size = 262144 
        
        last_progress_time = start_time
        
        yield {"type": "log", "message": "Downloading 10MB speed test payload from Cloudflare CDN..."}

        for chunk in response.iter_content(chunk_size=chunk_size):
            if not chunk:
                continue
            bytes_downloaded += len(chunk)
            
            
            progress = (bytes_downloaded / total_bytes) * 100
            yield {"type": "progress", "percent": progress}
            
            
            current_time = time.time()
            if current_time - last_progress_time >= 1.0:
                elapsed = current_time - start_time
                speed_mbps = (bytes_downloaded * 8) / (1024 * 1024 * elapsed)
                yield {"type": "log", "message": f"  Downloaded {bytes_downloaded / (1024*1024):.2f}MB - Current speed: {speed_mbps:.2f} Mbps"}
                last_progress_time = current_time

        end_time = time.time()
        total_time = end_time - start_time
        
        final_speed_mbps = (bytes_downloaded * 8) / (1024 * 1024 * total_time)
        
        yield {"type": "log", "message": f"\nTest completed in {total_time:.2f} seconds."}
        yield {"type": "log", "message": f"➔ Average Download Speed: {final_speed_mbps:.2f} Mbps"}
        yield {"type": "success", "message": f"Speed Test Finished: {final_speed_mbps:.2f} Mbps"}

    except Exception as e:
        yield {"type": "error", "message": f"Speed test failed: {str(e)}"}

async def run(params: dict):
    yield {"type": "log", "message": "Initializing local network speed test..."}
    
    loop = asyncio.get_running_loop()
    
    
    def run_iterator():
        return list(run_download_test())

    try:
        events = await loop.run_in_executor(None, run_iterator)
        for event in events:
            yield event
    except Exception as e:
        yield {"type": "error", "message": f"Execution error: {str(e)}"}
