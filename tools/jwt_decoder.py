import json
import base64
import asyncio

async def run(params: dict):
    jwt_str = params.get("jwt", "").strip()
    if not jwt_str:
        yield {"type": "error", "message": "JWT string token is required."}
        return
        
    yield {"type": "log", "message": "Extracting payload sections..."}
    
    try:
        parts = jwt_str.split(".")
        if len(parts) < 2:
            raise ValueError("Invalid JWT format (must contain header and payload parts).")
            
        header_b64 = parts[0]
        payload_b64 = parts[1]
        
        # Add padding if needed
        def decode_b64(b64):
            rem = len(b64) % 4
            if rem > 0:
                b64 += "=" * (4 - rem)
            return base64.b64decode(b64).decode()
            
        header = json.loads(decode_b64(header_b64))
        payload = json.loads(decode_b64(payload_b64))
        
        yield {"type": "found", "message": "--- Token Header ---"}
        yield {"type": "found", "message": json.dumps(header, indent=4)}
        yield {"type": "found", "message": "--- Token Payload ---"}
        yield {"type": "found", "message": json.dumps(payload, indent=4)}
        
        yield {"type": "success", "message": "JWT decoded successfully."}
    except Exception as e:
        yield {"type": "error", "message": f"Decoding failed: {str(e)}"}
