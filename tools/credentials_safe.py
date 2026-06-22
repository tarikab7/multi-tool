import os
import json
import base64
import asyncio
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet

SAFE_FILE = os.path.join(os.path.dirname(__file__), "credentials.enc")

def derive_key(master_key: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    return base64.urlsafe_b64encode(kdf.derive(master_key.encode()))

def load_safe() -> tuple[bytes, dict]:
    
    if os.path.exists(SAFE_FILE):
        try:
            with open(SAFE_FILE, 'rb') as f:
                data = json.load(f)
                salt = base64.b64decode(data["salt"].encode())
                encrypted = data["encrypted"].encode()
                return salt, encrypted
        except Exception:
            pass
    
    salt = os.urandom(16)
    return salt, b""

def save_safe(salt: bytes, encrypted: bytes):
    data = {
        "salt": base64.b64encode(salt).decode(),
        "encrypted": encrypted.decode()
    }
    with open(SAFE_FILE, 'w') as f:
        json.dump(data, f)

def add_entry_sync(master_key, service_name, secret_value):
    salt, encrypted_data = load_safe()
    key = derive_key(master_key, salt)
    fernet = Fernet(key)

    
    registry = {}
    if encrypted_data:
        try:
            decrypted = fernet.decrypt(encrypted_data)
            registry = json.loads(decrypted.decode())
        except Exception:
            return False, "Authentication failed. Invalid master key."

    
    registry[service_name] = secret_value
    
    
    new_encrypted = fernet.encrypt(json.dumps(registry).encode())
    save_safe(salt, new_encrypted)
    return True, f"Saved API credentials for service: {service_name}"

def list_entries_sync(master_key):
    salt, encrypted_data = load_safe()
    if not encrypted_data:
        return True, {}

    key = derive_key(master_key, salt)
    fernet = Fernet(key)

    try:
        decrypted = fernet.decrypt(encrypted_data)
        registry = json.loads(decrypted.decode())
        return True, registry
    except Exception:
        return False, "Authentication failed. Invalid master key."

async def run(params: dict):
    action = params.get("action", "list") 
    service_name = params.get("service_name", "").strip()
    secret_value = params.get("secret_value", "").strip()
    master_key = params.get("master_key", "").strip()

    if not master_key:
        yield {"type": "error", "message": "Master key is required to decrypt/encrypt credentials."}
        return

    if action == "add":
        if not service_name or not secret_value:
            yield {"type": "error", "message": "Service name and API key/value are required."}
            return
            
        yield {"type": "log", "message": "Deriving PBKDF2 HMAC key & encrypting service credentials..."}
        success, msg = await asyncio.to_thread(add_entry_sync, master_key, service_name, secret_value)
        if success:
            yield {"type": "progress", "percent": 100.0}
            yield {"type": "log", "message": msg}
            yield {"type": "success", "message": "API entry added."}
        else:
            yield {"type": "error", "message": msg}
            
    else:
        
        yield {"type": "log", "message": "Deriving PBKDF2 HMAC key & decrypting credentials safe..."}
        success, result = await asyncio.to_thread(list_entries_sync, master_key)
        
        if success:
            yield {"type": "progress", "percent": 100.0}
            if isinstance(result, dict) and result:
                yield {"type": "log", "message": f"Found {len(result)} saved service credentials:"}
                for svc, val in result.items():
                    
                    obfuscated = val[:4] + "*" * (len(val) - 4) if len(val) > 4 else "***"
                    yield {"type": "log", "message": f"  🔑 {svc:<20} ➔ {obfuscated} (Length: {len(val)})"}
                yield {"type": "success", "message": "Decryption successful."}
            else:
                yield {"type": "log", "message": "Credentials Safe is currently empty."}
                yield {"type": "success", "message": "Decryption successful. Registry empty."}
        else:
            yield {"type": "error", "message": result}
