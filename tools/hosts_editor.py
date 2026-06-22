import os
import asyncio
from tools.utils import yield_log, yield_error, yield_success, yield_progress

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
        yield yield_log(f"Reading active loopback rules from: {HOSTS_PATH}...")
        rules = await asyncio.to_thread(read_hosts_entries)
        
        if rules:
            yield yield_log(f"Found {len(rules)} loopback redirection entries:")
            for ip, domains in rules:
                yield yield_log(f"  IP: {ip:<10} ➔ {', '.join(domains)}")
        else:
            yield yield_log("No custom loopback redirection rules found in hosts file.")
            
        yield yield_progress(100.0)
        yield yield_success("Hosts lookup complete.")
        
    else:
        # Add rule
        if not domain:
            yield yield_error("Domain name is required to block.")
            return
            
        # Clean domain
        domain = domain.replace("http://", "").replace("https://", "").split("/")[0]
        
        yield yield_log(f"Attempting to add blocking entry for: {domain}...")
        success, result = await asyncio.to_thread(add_hosts_entry, domain)
        
        yield yield_progress(100.0)
        if success:
            yield yield_log(result)
            yield yield_success(f"Domain {domain} is now blocked.")
        else:
            yield yield_log("Permission Denied: Root/Administrator access is required to write to /etc/hosts.")
            yield yield_log("\nTo apply this rule, execute the following command in your terminal:")
            yield yield_log(f"  👉 {result}")
            yield yield_success("Action completed (manual step required).")
