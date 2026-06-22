import asyncio
import requests

async def run(params: dict):
    domain = params.get("domain", "").strip().replace("http://", "").replace("https://", "").split("/")[0]
    record_type = params.get("record_type", "A").strip()
    
    if not domain:
        yield {"type": "error", "message": "Domain name is required."}
        return
        
    yield {"type": "log", "message": f"Checking DNS records for {domain} across global public DNS servers..."}
    
    
    resolvers = {
        "Cloudflare (1.1.1.1)": "https://cloudflare-dns.com/dns-query",
        "Google (8.8.8.8)": "https://dns.google/resolve",
        "Quad9 (9.9.9.9)": "https://dns.quad9.net/dns-query"
    }
    
    headers = {"Accept": "application/dns-json"}
    
    for name, endpoint in resolvers.items():
        yield {"type": "log", "message": f"Querying {name} resolver..."}
        try:
            url = f"{endpoint}?name={domain}&type={record_type}"
            response = await asyncio.to_thread(requests.get, url, headers=headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                answers = data.get("Answer", [])
                results = []
                for ans in answers:
                    results.append(ans.get("data"))
                yield {"type": "found", "message": f"{name} response: {', '.join(results) if results else 'No records'}"}
            else:
                yield {"type": "log", "message": f"{name} query returned HTTP status {response.status_code}"}
        except Exception as e:
            yield {"type": "log", "message": f"{name} query failed: {str(e)}"}
        await asyncio.sleep(0.1)
        
    yield {"type": "success", "message": "DNS Propagation checks finished."}
