import asyncio
import math

async def run(params: dict):
    password = params.get("password", "").strip()
    if not password:
        yield {"type": "error", "message": "Password string is required."}
        return
        
    yield {"type": "log", "message": "Calculating entropy sets..."}
    await asyncio.sleep(0.3)
    
    try:
        length = len(password)
        pool = 0
        
        # Heuristic character sets detection
        if any(c.islower() for c in password): pool += 26
        if any(c.isupper() for c in password): pool += 26
        if any(c.isdigit() for c in password): pool += 10
        if any(not c.isalnum() for c in password): pool += 32
        
        entropy = length * math.log2(pool) if pool > 0 else 0
        
        # Estimate strength
        strength = "Weak"
        if entropy > 80: strength = "Very Strong"
        elif entropy > 60: strength = "Strong"
        elif entropy > 40: strength = "Moderate"
        
        yield {"type": "found", "message": f"Length: {length}"}
        yield {"type": "found", "message": f"Alphabet pool size: {pool}"}
        yield {"type": "found", "message": f"Entropy: {entropy:.2f} bits"}
        yield {"type": "found", "message": f"Strength: {strength}"}
        
        yield {"type": "success", "message": "Password analysis finished."}
    except Exception as e:
        yield {"type": "error", "message": f"Calculation error: {str(e)}"}
