import requests
import asyncio
import subprocess

def query_doh_record(domain, record_type):
    url = "https://cloudflare-dns.com/dns-query"
    headers = {"accept": "application/dns-json"}
    params = {"name": domain, "type": record_type}
    try:
        response = requests.get(url, params=params, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            answers = data.get("Answer", [])
            results = []
            for ans in answers:
                results.append(f"{ans.get('name')} ➔ {ans.get('data')} (TTL: {ans.get('TTL')})")
            return results
    except Exception:
        pass
    return []

def query_geoip(host):
    # ipapi.co returns details for current IP if path is empty, or specified IP/domain
    url = "https://ipapi.co/json/"
    if host:
        url = f"https://ipapi.co/{host}/json/"
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        return {"error": str(e)}
    return {}

async def run_ping(host):
    # -c 4 means ping 4 times on Linux
    # Use -w 5 to set a 5-second total timeout
    cmd = ['ping', '-c', '4', '-w', '5', host]
    
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    
    if process.returncode == 0:
        return True, stdout.decode('utf-8', errors='ignore')
    else:
        err = stderr.decode('utf-8', errors='ignore')
        out = stdout.decode('utf-8', errors='ignore')
        return False, out if out else err

async def run(params: dict):
    host = params.get("host", "").strip()
    op_type = params.get("op_type", "ping") # "ping", "dns", "geoip"

    # Clean domain if entered
    if host:
        host = host.replace("http://", "").replace("https://", "").split("/")[0].split(":")[0]

    if op_type == "ping":
        if not host:
            yield {"type": "error", "message": "Host address is required for Ping test."}
            return
        yield {"type": "log", "message": f"Pinging target host '{host}'..."}
        success, output = await run_ping(host)
        
        # Stream the ping console output line by line
        for line in output.splitlines():
            if line.strip():
                yield {"type": "log", "message": line}
                
        yield {"type": "progress", "percent": 100.0}
        if success:
            yield {"type": "success", "message": "Ping response received successfully."}
        else:
            yield {"type": "error", "message": "Failed to receive response from host."}
            
    elif op_type == "dns":
        if not host:
            yield {"type": "error", "message": "Domain is required for DNS lookup."}
            return
        yield {"type": "log", "message": f"Querying Cloudflare DNS-over-HTTPS (DoH) for '{host}'..."}
        
        record_types = ["A", "AAAA", "MX", "TXT", "NS"]
        loop = asyncio.get_running_loop()
        
        for idx, rec_type in enumerate(record_types, 1):
            yield {"type": "log", "message": f"Fetching {rec_type} records..."}
            results = await loop.run_in_executor(None, query_doh_record, host, rec_type)
            if results:
                for res in results:
                    yield {"type": "log", "message": f"  [DNS] {res}"}
            else:
                yield {"type": "log", "message": f"  [DNS] No active {rec_type} records found."}
                
            progress = (idx / len(record_types)) * 100
            yield {"type": "progress", "percent": progress}
            
        yield {"type": "success", "message": "DNS records retrieved successfully."}

    else:
        # Geo-IP lookup
        lookup_type = f"IP: {host}" if host else "Self (Your public IP)"
        yield {"type": "log", "message": f"Retrieving geographical location details for {lookup_type}..."}
        
        loop = asyncio.get_running_loop()
        data = await loop.run_in_executor(None, query_geoip, host)
        
        yield {"type": "progress", "percent": 100.0}
        
        if "error" in data:
            yield {"type": "error", "message": f"Geo-IP lookup failed: {data['error']}"}
        elif "ip" in data:
            yield {"type": "log", "message": f"IP Address:  {data.get('ip')}"}
            yield {"type": "log", "message": f"Country:     {data.get('country_name')} ({data.get('country_code')})"}
            yield {"type": "log", "message": f"Region/City: {data.get('region')} / {data.get('city')}"}
            yield {"type": "log", "message": f"Latitude:    {data.get('latitude')}"}
            yield {"type": "log", "message": f"Longitude:   {data.get('longitude')}"}
            yield {"type": "log", "message": f"ISP:         {data.get('org')}"}
            yield {"type": "log", "message": f"ASN:         {data.get('asn')}"}
            yield {"type": "success", "message": "Geo-IP lookup completed."}
        else:
            yield {"type": "error", "message": "Failed to parse Geo-IP details from response."}
