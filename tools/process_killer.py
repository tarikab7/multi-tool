import psutil
import asyncio

async def run(params: dict):
    action = params.get("action", "list").strip() # list / kill
    pid_to_kill = params.get("pid", "").strip()
    
    try:
        if action == "list":
            yield {"type": "log", "message": "Retrieving process list sorting by high CPU/RAM usage..."}
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Sort by CPU
            processes = sorted(processes, key=lambda x: x.get('cpu_percent') or 0, reverse=True)
            
            for p in processes[:15]: # Show top 15
                yield {"type": "found", "message": f"PID: {p['pid']} | Name: {p['name']} | CPU: {p['cpu_percent']}% | RAM: {p['memory_percent']:.2f}%"}
            yield {"type": "success", "message": "Process list loaded successfully."}
            
        else: # kill
            if not pid_to_kill:
                yield {"type": "error", "message": "PID is required for killing process."}
                return
            pid = int(pid_to_kill)
            yield {"type": "log", "message": f"Sending SIGKILL to PID {pid}..."}
            p = psutil.Process(pid)
            p.terminate()
            yield {"type": "success", "message": f"Process {pid} terminated successfully."}
    except Exception as e:
        yield {"type": "error", "message": f"Process command failed: {str(e)}"}
