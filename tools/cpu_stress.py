import asyncio
import time
import multiprocessing

def heavy_math(duration):
    t_end = time.time() + duration
    while time.time() < t_end:
        # CPU intensive operation
        _ = 12345.67 * 9876.54

async def run(params: dict):
    duration = int(params.get("duration", "10"))
    cores = int(params.get("cores", "2"))
    
    yield {"type": "log", "message": f"Spawning stress load on {cores} core(s) for {duration} seconds..."}
    await asyncio.sleep(0.5)
    
    try:
        processes = []
        for _ in range(cores):
            p = multiprocessing.Process(target=heavy_math, args=(duration,))
            p.start()
            processes.append(p)
            
        yield {"type": "log", "message": "Stressor processes active. Core loads maximum."}
        
        # Wait asynchronously
        for _ in range(duration):
            await asyncio.sleep(1)
            yield {"type": "log", "message": "Heating cores... stress load active."}
            
        for p in processes:
            p.join()
            
        yield {"type": "success", "message": f"Core stress load finished safely. Stressed for {duration}s."}
    except Exception as e:
        yield {"type": "error", "message": f"Load error: {str(e)}"}
