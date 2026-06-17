import pytest
from tools.sql_formatter import run

@pytest.mark.asyncio
async def test_sql_formatter_missing_sql():
    gen = run({})
    events = [event async for event in gen]

    assert len(events) == 1
    err = events[0]
    if hasattr(err, "to_dict"):
        err = err.to_dict()
    assert err["type"] == "error"
    assert "required" in err["message"]

@pytest.mark.asyncio
async def test_sql_formatter_success():
    gen = run({"sql": "SELECT * FROM users WHERE id = 1"})
    events = [event async for event in gen]

    # Process events to dicts
    dicts = [e.to_dict() if hasattr(e, 'to_dict') else e for e in events]

    assert len(dicts) == 3
    assert dicts[0]["type"] == "log"
    assert dicts[1]["type"] == "found"
    assert "SELECT" in dicts[1]["message"]
    assert dicts[2]["type"] == "success"
    assert dicts[2]["message"] == "SQL formatted successfully."
