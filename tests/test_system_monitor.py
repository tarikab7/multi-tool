import pytest
import asyncio
from tools.system_monitor import run

@pytest.mark.asyncio
async def test_system_monitor_invalid_interval():
    results = [res async for res in run({"interval": "invalid"})]
    assert len(results) == 1
    assert results[0]["type"] == "error"
    assert results[0]["message"] == "Interval speed must be an integer."

@pytest.mark.asyncio
async def test_system_monitor_valid_run():
    gen = run({"interval": 1})

    res1 = await anext(gen)
    assert res1["type"] == "log"
    assert "System Resource Monitor Active" in res1["message"]

    res2 = await anext(gen)
    assert res2["type"] == "log"
    assert "Click 'Stop Operation'" in res2["message"]

    res3 = await anext(gen)
    assert res3["type"] == "log"
    assert "CPU Load:" in res3["message"]
    assert "RAM:" in res3["message"]
    assert "Storage:" in res3["message"]

    await gen.aclose()
