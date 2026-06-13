import os
import asyncio
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

async def run(params: dict):
    file_path = params.get("file_path", "").strip()
    password = params.get("password", "").strip()
    mode = params.get("mode", "encrypt").strip() # encrypt / decrypt
    
    if not file_path or not os.path.exists(file_path):
        yield {"type": "error", "message": "Valid file path is required."}
        return
        
    if not password:
        yield {"type": "error", "message": "Password is required."}
        return
        
    yield {"type": "log", "message": f"Performing PBKDF2 key derivation & AES-256 {mode}..."}
    
    salt = b"antigravity_salt"

    # Offload the PBKDF2 to a thread to unblock the event loop
    def derive_key():
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        return kdf.derive(password.encode())

    key = await asyncio.to_thread(derive_key)
    iv = b"antigravity_iv__" # Static IV for simplicity in tool scope
    
    output_path = f"{file_path}.enc" if mode == "encrypt" else file_path.replace(".enc", "_decrypted")
    
    def do_encrypt(cipher_obj, in_path, out_path):
        encryptor = cipher_obj.encryptor()
        with open(in_path, "rb") as f_in, open(out_path, "wb") as f_out:
            data = f_in.read()
            # Pad to 16 byte block size
            padding_len = 16 - (len(data) % 16)
            data += bytes([padding_len]) * padding_len
            f_out.write(encryptor.update(data) + encryptor.finalize())

    def do_decrypt(cipher_obj, in_path, out_path):
        decryptor = cipher_obj.decryptor()
        with open(in_path, "rb") as f_in, open(out_path, "wb") as f_out:
            data = decryptor.update(f_in.read()) + decryptor.finalize()
            # Unpad
            padding_len = data[-1]
            data = data[:-padding_len]
            f_out.write(data)

    try:
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        
        if mode == "encrypt":
            await asyncio.to_thread(do_encrypt, cipher, file_path, output_path)
        else:
            await asyncio.to_thread(do_decrypt, cipher, file_path, output_path)
                
        yield {"type": "success", "message": f"Successfully completed. Output file: {output_path}"}
    except Exception as e:
        yield {"type": "error", "message": f"Encryption/Decryption failed: {str(e)}"}
