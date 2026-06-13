import asyncio

async def run(params: dict):
    ip_str = params.get("ip", "192.168.1.1").strip()
    cidr_str = params.get("cidr", "24").strip()
    
    yield {"type": "log", "message": "Calculating subnet range values..."}
    await asyncio.sleep(0.5)
    
    try:
        cidr = int(cidr_str)
        if cidr < 0 or cidr > 32:
            raise ValueError("CIDR must be between 0 and 32")
            
        parts = [int(p) for p in ip_str.split(".")]
        if len(parts) != 4 or any(p < 0 or p > 255 for p in parts):
            raise ValueError("IP address must be a valid IPv4")
            
        # Calc mask
        mask_int = (0xffffffff >> (32 - cidr)) << (32 - cidr)
        mask_parts = [
            (mask_int >> 24) & 0xff,
            (mask_int >> 16) & 0xff,
            (mask_int >> 8) & 0xff,
            mask_int & 0xff
        ]
        
        # Calc network IP
        ip_int = (parts[0] << 24) + (parts[1] << 16) + (parts[2] << 8) + parts[3]
        net_int = ip_int & mask_int
        net_parts = [
            (net_int >> 24) & 0xff,
            (net_int >> 16) & 0xff,
            (net_int >> 8) & 0xff,
            net_int & 0xff
        ]
        
        # Calc broadcast IP
        broad_int = net_int | (0xffffffff ^ mask_int)
        broad_parts = [
            (broad_int >> 24) & 0xff,
            (broad_int >> 16) & 0xff,
            (broad_int >> 8) & 0xff,
            broad_int & 0xff
        ]
        
        hosts = 2**(32 - cidr) - 2 if cidr < 31 else 0
        
        yield {"type": "found", "message": f"Netmask: {'.'.join(str(p) for p in mask_parts)}"}
        yield {"type": "found", "message": f"Network Address: {'.'.join(str(p) for p in net_parts)}"}
        yield {"type": "found", "message": f"Broadcast Address: {'.'.join(str(p) for p in broad_parts)}"}
        yield {"type": "found", "message": f"Usable Hosts Range: {'.'.join(str(p) for p in net_parts[:-1])}.{net_parts[-1]+1} - {'.'.join(str(p) for p in broad_parts[:-1])}.{broad_parts[-1]-1}"}
        yield {"type": "found", "message": f"Max Number of Hosts: {hosts}"}
        
        yield {"type": "success", "message": "Calculated network ranges successfully."}
    except Exception as e:
        yield {"type": "error", "message": f"Invalid inputs: {str(e)}"}
