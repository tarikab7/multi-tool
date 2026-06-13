import pytest
from tools.ip_validator import run

@pytest.mark.asyncio
async def test_run_valid_ipv4():
    params = {"ip": "192.168.1.1"}
    results = [res async for res in run(params)]
    assert any(res["type"] == "success" for res in results)
    assert any("IPv4 validation passed" in res.get("message", "") for res in results)

@pytest.mark.asyncio
async def test_run_valid_ipv6():
    params = {"ip": "2001:0db8:85a3:0000:0000:8a2e:0370:7334"}
    results = [res async for res in run(params)]
    assert any(res["type"] == "success" for res in results)
    assert any("IPv6 validation passed" in res.get("message", "") for res in results)

@pytest.mark.asyncio
async def test_run_invalid_ip():
    params = {"ip": "invalid-ip"}
    results = [res async for res in run(params)]
    assert any(res["type"] == "error" for res in results)
    assert any("NOT a valid IP address format" in res.get("message", "") for res in results)

@pytest.mark.asyncio
async def test_run_empty_ip():
    params = {"ip": ""}
    results = [res async for res in run(params)]
    assert any(res["type"] == "error" for res in results)
    assert any("IP address to validate is required" in res.get("message", "") for res in results)
