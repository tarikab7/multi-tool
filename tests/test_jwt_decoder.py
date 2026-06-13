import pytest
from tools.jwt_decoder import run

@pytest.mark.asyncio
async def test_jwt_decoder_missing_token():
    params = {}
    results = [res async for res in run(params)]
    assert len(results) == 1
    assert results[0]["type"] == "error"
    assert "JWT string token is required" in results[0]["message"]
