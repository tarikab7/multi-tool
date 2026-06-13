import socket
import asyncio

async def run(params: dict):
    ip = params.get("ip", "").strip()
    if not ip:
        yield {"type": "error", "message": "IP address to validate is required."}
        return
        
    yield {"type": "log", "message": f"Validating format patterns for {ip}..."}
    
    # Try IPv4
    try:
        socket.inet_pton(socket.AF_INET, ip)
        yield {"type": "found", "message": f"Result: {ip} is a valid IPv4 address."}
        yield {"type": "success", "message": "IPv4 validation passed."}
        return
    except socket.error:
        pass
        
    # Try IPv6
    try:
        socket.inet_pton(socket.AF_INET6, ip)
        yield {"type": "found", "message": f"Result: {ip} is a valid IPv6 address."}
        yield {"type": "success", "message": "IPv6 validation passed."}
        return
    except socket.error:
        pass
        
    yield {"type": "error", "message": f"Result: {ip} is NOT a valid IP address format."}
