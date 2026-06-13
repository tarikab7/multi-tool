import os
import asyncio

HOSTS_PATH = "/etc/hosts"

def read_hosts_entries():
    rules = []
    if os.path.exists(HOSTS_PATH):
        try:
            with open(HOSTS_PATH, 'r') as f:
                for line in f:
                    line = line.strip()
                    # Look for active redirections (e.g. starting with 127.0.0.1 or ::1)
                    if line and not line.startswith('#'):
                        parts = line.split()
                        if len(parts) >= 2:
                            ip = parts[0]
                            domains = parts[1:]
                            if ip in ("127.0.0.1", "::1", "0.0.0.0"):
                                rules.append((ip, domains))
        except Exception:
            pass
    return rules

def add_hosts_entry(domain):
    line_to_add = f"\n127.0.0.1 {domain} # blocked by Antigravity Suite\n"
    try:
        # Check if we have write access
        with open(HOSTS_PATH, 'a') as f:
            f.write(line_to_add)
        return True, f"Successfully blocked {domain} locally."
    except PermissionError:
        return False, f"echo '127.0.0.1 {domain} # blocked' | sudo tee -a /etc/hosts"

async def run(params: dict):
    action = params.get("action", "view") # "view" or "add"
    domain = params.get("domain", "").strip()

    if action == "view":
        yield {"type": "log", "message": f"Reading active loopback rules from: {HOSTS_PATH}..."}
        rules = await asyncio.to_thread(read_hosts_entries)
        
        if rules:
            yield {"type": "log", "message": f"Found {len(rules)} loopback redirection entries:"}
            for ip, domains in rules:
                yield {"type": "log", "message": f"  IP: {ip:<10} ➔ {', '.join(domains)}"}
        else:
            yield {"type": "log", "message": "No custom loopback redirection rules found in hosts file."}
            
        yield {"type": "progress", "percent": 100.0}
        yield {"type": "success", "message": "Hosts lookup complete."}
        
    else:
        # Add rule
        if not domain:
            yield {"type": "error", "message": "Domain name is required to block."}
            return
            
        # Clean domain
        domain = domain.replace("http://", "").replace("https://", "").split("/")[0]
        
        yield {"type": "log", "message": f"Attempting to add blocking entry for: {domain}..."}
        success, result = await asyncio.to_thread(add_hosts_entry, domain)
        
        yield {"type": "progress", "percent": 100.0}
        if success:
            yield {"type": "log", "message": result}
            yield {"type": "success", "message": f"Domain {domain} is now blocked."}
        else:
            yield {"type": "log", "message": "Permission Denied: Root/Administrator access is required to write to /etc/hosts."}
            yield {"type": "log", "message": "\nTo apply this rule, execute the following command in your terminal:"}
            yield {"type": "log", "message": f"  👉 {result}"}
            yield {"type": "success", "message": "Action completed (manual step required)."}
