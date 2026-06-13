import asyncio
import subprocess

async def run(params: dict):
    subnet = params.get("subnet", "192.168.1").strip()
    
    yield {"type": "log", "message": f"Initiating fast sweeping ICMP ping on LAN network {subnet}.X..."}
    
    active_ips = []
    
    async def ping_ip(ip):
        cmd = ["ping", "-c", "1", "-W", "1", ip]
        proc = await asyncio.create_subprocess_exec(*cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        await proc.wait()
        if proc.returncode == 0:
            return ip
        return None

    # Sweep IPs .1 to .50 for tool timeout safety
    tasks = [ping_ip(f"{subnet}.{i}") for i in range(1, 51)]
    
    results = await asyncio.gather(*tasks)
    for res in results:
        if res:
            active_ips.append(res)
            yield {"type": "found", "message": f"Device online: {res}"}
            
    yield {"type": "success", "message": f"Subnet sweep completed. Found {len(active_ips)} active devices."}
