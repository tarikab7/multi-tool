import os
import psutil
import asyncio

async def run(params: dict):
    try:
        interval = int(params.get("interval", 2))
        interval = max(1, min(10, interval))
    except ValueError:
        yield {"type": "error", "message": "Interval speed must be an integer."}
        return

    yield {"type": "log", "message": "System Resource Monitor Active (Streaming logs...)"}
    yield {"type": "log", "message": "Click 'Stop Operation' in the logs panel to end monitoring."}

    
    psutil.cpu_percent(interval=None)
    await asyncio.sleep(0.1)

    try:
        while True:
            
            cpu = psutil.cpu_percent(interval=None)
            ram = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            
            ram_used = ram.used / (1024**3)
            ram_total = ram.total / (1024**3)
            disk_used = disk.used / (1024**3)
            disk_total = disk.total / (1024**3)

            msg = (
                f"CPU Load: {cpu:04.1f}% | "
                f"RAM: {ram.percent}% ({ram_used:.2f}GB / {ram_total:.2f}GB) | "
                f"Storage: {disk.percent}% ({disk_used:.1f}GB / {disk_total:.1f}GB free)"
            )
            
            yield {"type": "log", "message": msg}
            
            
            await asyncio.sleep(interval)
            
    except asyncio.CancelledError:
        yield {"type": "log", "message": "Monitoring stopped by user request."}
        yield {"type": "success", "message": "Resource monitoring complete."}
    except Exception as e:
        yield {"type": "error", "message": f"Monitor error: {str(e)}"}
