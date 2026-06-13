import pytest
from tools.ssl_expiry_checker import run

@pytest.mark.asyncio
async def test_ssl_expiry_checker_missing_host():
    results = [res async for res in run({"host": ""})]
    assert len(results) == 1
    assert results[0] == {"type": "error", "message": "Valid host name is required."}

@pytest.mark.asyncio
async def test_ssl_expiry_checker_missing_params():
    results = [res async for res in run({})]
    assert len(results) == 1
    assert results[0] == {"type": "error", "message": "Valid host name is required."}
