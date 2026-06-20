import socket
import ssl
import datetime
import asyncio
from tools.utils import yield_error, yield_log, yield_success, ToolEvent

async def run(params: dict):
    host = params.get("host", "").strip().replace("http://", "").replace("https://", "").split("/")[0].split(":")[0]
    port = int(params.get("port", "443"))
    
    if not host:
        yield yield_error("Valid host name is required.")
        return
        
    yield yield_log(f"Retrieving SSL certificate details from {host}:{port}...")
    
    try:
        context = ssl.create_default_context()
        conn = socket.create_connection((host, port), timeout=5)
        sock = context.wrap_socket(conn, server_hostname=host)
        
        cert = sock.getpeercert()
        
        # Expiry date parsing: e.g. "Jun 13 14:00:00 2026 GMT"
        expiry_str = cert.get('notAfter')
        if expiry_str:
            expiry_date = datetime.datetime.strptime(expiry_str, "%b %d %H:%M:%S %Y %Z")
            days_left = (expiry_date - datetime.datetime.utcnow()).days
            
            yield ToolEvent(event_type="found", message=f"Issuer: {dict(x[0] for x in cert.get('issuer', []))}")
            yield ToolEvent(event_type="found", message=f"Expires On: {expiry_str}")
            yield ToolEvent(event_type="found", message=f"Days Remaining: {days_left} days")
            
            if days_left <= 0:
                yield yield_log("WARNING: Certificate has EXPIRED!")
            elif days_left < 30:
                yield yield_log("WARNING: Certificate expires in less than 30 days!")
                
            yield yield_success(f"SSL status: OK ({days_left} days remaining)")
        else:
            yield yield_error("Unable to read certificate validity headers.")
            
        sock.close()
    except Exception as e:
        yield yield_error(f"SSL check failed: {str(e)}")
