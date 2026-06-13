import pytest
import os
import asyncio
from tools.file_encrypter import run

@pytest.mark.asyncio
async def test_encrypt_decrypt_integration(tmp_path):
    # Setup
    test_file = tmp_path / "test_file.txt"
    test_file.write_text("Hello, secret world!")

    # Encrypt
    encrypt_params = {
        "file_path": str(test_file),
        "password": "strong_password",
        "mode": "encrypt"
    }

    encrypt_results = []
    async for res in run(encrypt_params):
        encrypt_results.append(res)

    assert any(res["type"] == "success" for res in encrypt_results)
    assert os.path.exists(f"{test_file}.enc")

    # Decrypt
    decrypt_params = {
        "file_path": f"{test_file}.enc",
        "password": "strong_password",
        "mode": "decrypt"
    }

    decrypt_results = []
    async for res in run(decrypt_params):
        decrypt_results.append(res)

    assert any(res["type"] == "success" for res in decrypt_results)
    assert os.path.exists(f"{test_file}_decrypted")

    # Verify content
    with open(f"{test_file}_decrypted", "r") as f:
        content = f.read()
    assert content == "Hello, secret world!"
