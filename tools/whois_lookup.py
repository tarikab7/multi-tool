import asyncio
import requests

async def run(params: dict):
    domain = params.get("domain", "").strip().replace("http://", "").replace("https://", "").split("/")[0]
    if not domain:
        yield {"type": "error", "message": "Domain is required."}
        return
        
    yield {"type": "log", "message": f"Fetching WHOIS registry records for: {domain}..."}
    
    
    url = f"https://rdap.org/domain/{domain}"
    
    try:
        response = await asyncio.to_thread(requests.get, url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            
            yield {"type": "found", "message": f"Domain Name: {data.get('ldhName')}"}
            
            
            for event in data.get("events", []):
                action = event.get("eventAction", "unknown")
                date = event.get("eventDate", "")
                yield {"type": "found", "message": f"{action.capitalize()} Date: {date}"}
                
            
            for entity in data.get("entities", []):
                roles = entity.get("roles", [])
                if "registrar" in roles:
                    vcard = entity.get("vcardArray", [])
                    if len(vcard) > 1:
                        details = vcard[1]
                        for det in details:
                            if det[0] == "fn":
                                yield {"type": "found", "message": f"Registrar: {det[3]}"}
                                
            yield {"type": "success", "message": "RDAP WHOIS query completed."}
        else:
            yield {"type": "error", "message": f"WHOIS data unavailable (HTTP {response.status_code})"}
    except Exception as e:
        yield {"type": "error", "message": f"WHOIS query failed: {str(e)}"}
