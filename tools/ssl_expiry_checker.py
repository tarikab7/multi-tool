import socket
import ssl
import datetime
import asyncio

async def run(params: dict):
    host = params.get("host", "").strip().replace("http://", "").replace("https://", "").split("/")[0].split(":")[0]
    port = int(params.get("port", "443"))
    
    if not host:
        yield {"type": "error", "message": "Valid host name is required."}
        return
        
    yield {"type": "log", "message": f"Retrieving SSL certificate details from {host}:{port}..."}
    
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
            
            yield {"type": "found", "message": f"Issuer: {dict(x[0] for x in cert.get('issuer', []))}"}
            yield {"type": "found", "message": f"Expires On: {expiry_str}"}
            yield {"type": "found", "message": f"Days Remaining: {days_left} days"}
            
            if days_left <= 0:
                yield {"type": "log", "message": "WARNING: Certificate has EXPIRED!"}
            elif days_left < 30:
                yield {"type": "log", "message": "WARNING: Certificate expires in less than 30 days!"}
                
            yield {"type": "success", "message": f"SSL status: OK ({days_left} days remaining)"}
        else:
            yield {"type": "error", "message": "Unable to read certificate validity headers."}
            
        sock.close()
    except Exception as e:
        yield {"type": "error", "message": f"SSL check failed: {str(e)}"}
