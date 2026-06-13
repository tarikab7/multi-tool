import socket
import asyncio
from tools.utils import yield_log, yield_error, yield_success

async def run(params: dict):
    ip = params.get("ip", "").strip()
    if not ip:
        yield yield_error("IP address to validate is required.")
        return
        
    yield yield_log(f"Validating format patterns for {ip}...")
    
    # Try IPv4
    try:
        socket.inet_pton(socket.AF_INET, ip)
        yield {"type": "found", "message": f"Result: {ip} is a valid IPv4 address."}
        yield yield_success("IPv4 validation passed.")
        return
    except socket.error:
        pass
        
    # Try IPv6
    try:
        socket.inet_pton(socket.AF_INET6, ip)
        yield {"type": "found", "message": f"Result: {ip} is a valid IPv6 address."}
        yield yield_success("IPv6 validation passed.")
        return
    except socket.error:
        pass
        
    yield yield_error(f"Result: {ip} is NOT a valid IP address format.")
