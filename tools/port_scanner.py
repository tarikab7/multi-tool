import asyncio

async def scan_single_port(host, port):
    try:
        
        conn = asyncio.open_connection(host, port)
        reader, writer = await asyncio.wait_for(conn, timeout=1.0)
        writer.close()
        try:
            await writer.wait_closed()
        except Exception:
            pass
        return port, True
    except Exception:
        return port, False

async def run(params: dict):
    host = params.get("host", "127.0.0.1").strip()
    range_str = params.get("range_str", "20-1024").strip()

    if not host:
        yield {"type": "error", "message": "Host is required."}
        return

    
    ports = []
    try:
        if "-" in range_str:
            start, end = map(int, range_str.split("-"))
            ports = list(range(start, end + 1))
        elif "," in range_str:
            ports = [int(p.strip()) for p in range_str.split(",") if p.strip()]
        else:
            ports = [int(range_str)]
    except ValueError:
        yield {"type": "error", "message": "Invalid ports format. Use e.g. '21-80' or '80,443'."}
        return

    
    if len(ports) > 2000:
        yield {"type": "error", "message": "Port scanner limit is 2000 ports per scan."}
        return

    total_ports = len(ports)
    yield {"type": "log", "message": f"Starting concurrent scan on {host} for {total_ports} ports..."}

    
    batch_size = 100
    open_ports = []
    scanned_count = 0

    for i in range(0, total_ports, batch_size):
        batch = ports[i:i + batch_size]
        tasks = [scan_single_port(host, port) for port in batch]
        
        results = await asyncio.gather(*tasks)
        
        for port, is_open in results:
            if is_open:
                open_ports.append(port)
                yield {"type": "found", "message": f"Port {port} is OPEN.", "data": {"port": port}}
        
        scanned_count += len(batch)
        progress = (scanned_count / total_ports) * 100
        yield {"type": "progress", "percent": progress}

    open_ports.sort()
    if open_ports:
        yield {"type": "log", "message": f"\nScan finished. Open ports: {', '.join(map(str, open_ports))}"}
        yield {"type": "success", "message": f"Successfully completed. Found {len(open_ports)} open port(s)."}
    else:
        yield {"type": "log", "message": "\nScan finished. No open ports found."}
        yield {"type": "success", "message": "Scan completed. 0 open ports found."}
