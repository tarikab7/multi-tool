import os
import re
import asyncio
from collections import Counter

async def run(params: dict):
    log_path = params.get("log_path", "").strip()
    
    if not log_path or not os.path.exists(log_path):
        yield {"type": "error", "message": "Valid log file path is required."}
        return
        
    yield {"type": "log", "message": "Parsing log patterns (IP hits, status codes)..."}
    await asyncio.sleep(1)
    
    ip_counter = Counter()
    status_counter = Counter()
    total_lines = 0
    
    # Common Log Format regex: 127.0.0.1 - - [date] "GET /path HTTP/1.1" 200 1234
    log_pattern = re.compile(r'^(\S+) \S+ \S+ \[.*?\] "\S+ \S+ \S+" (\d{3})')
    
    try:
        with open(log_path, "r", errors="ignore") as f:
            for line in f:
                total_lines += 1
                match = log_pattern.match(line)
                if match:
                    ip, status = match.groups()
                    ip_counter[ip] += 1
                    status_counter[status] += 1
                if total_lines % 5000 == 0:
                    await asyncio.sleep(0.001)
                    
        yield {"type": "log", "message": f"Successfully parsed {total_lines} log lines."}
        
        yield {"type": "log", "message": "--- Top 5 IP Addresses ---"}
        for ip, count in ip_counter.most_common(5):
            yield {"type": "found", "message": f"IP: {ip} - {count} hits"}
            
        yield {"type": "log", "message": "--- HTTP Status Code Distribution ---"}
        for status, count in status_counter.items():
            yield {"type": "found", "message": f"Status: {status} - {count} times"}
            
        yield {"type": "success", "message": "Log file analysis completed."}
    except Exception as e:
        yield {"type": "error", "message": f"Analysis failed: {str(e)}"}
