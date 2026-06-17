import pytest
from tools.password_strength import run

@pytest.mark.asyncio
async def test_password_strength_missing_password():
    gen = run({})
    events = [event async for event in gen]
    dicts = [e.to_dict() if hasattr(e, 'to_dict') else e for e in events]

    assert len(dicts) == 1
    assert dicts[0]["type"] == "error"
    assert "required" in dicts[0]["message"]

@pytest.mark.asyncio
async def test_password_strength_success():
    gen = run({"password": "TestPassword123!"})
    events = [event async for event in gen]
    dicts = [e.to_dict() if hasattr(e, 'to_dict') else e for e in events]

    assert len(dicts) == 6
    assert dicts[0]["type"] == "log"
    assert dicts[1]["type"] == "found"
    assert dicts[2]["type"] == "found"
    assert dicts[3]["type"] == "found"
    assert dicts[4]["type"] == "found"
    assert dicts[5]["type"] == "success"
    assert dicts[5]["message"] == "Password analysis finished."
