import pytest
from tools.utils import ToolEvent, yield_log, yield_progress, yield_success, yield_error

def test_tool_event():
    event = ToolEvent(type="test", key="value")
    assert event.type == "test"
    assert event.key == "value"
    assert event.as_dict() == {"type": "test", "key": "value"}

def test_yield_log():
    event = yield_log("Hello")
    assert isinstance(event, ToolEvent)
    assert event.type == "log"
    assert event.message == "Hello"
    assert event.as_dict() == {"type": "log", "message": "Hello"}

def test_yield_progress():
    event = yield_progress(50.5)
    assert isinstance(event, ToolEvent)
    assert event.type == "progress"
    assert event.percent == 50.5
    assert event.as_dict() == {"type": "progress", "percent": 50.5}

def test_yield_success():
    event = yield_success("Done", data={"count": 5})
    assert isinstance(event, ToolEvent)
    assert event.type == "success"
    assert event.message == "Done"
    assert event.count == 5
    assert event.as_dict() == {"type": "success", "message": "Done", "count": 5}

def test_yield_error():
    event = yield_error("Failed")
    assert isinstance(event, ToolEvent)
    assert event.type == "error"
    assert event.message == "Failed"
    assert event.as_dict() == {"type": "error", "message": "Failed"}

import asyncio
from tools import sql_formatter

@pytest.mark.asyncio
async def test_sql_formatter():
    params = {"sql": "SELECT * FROM users"}
    generator = sql_formatter.run(params)
    events = []
    async for event in generator:
        if isinstance(event, ToolEvent):
            events.append(event.as_dict())
        else:
            events.append(event)

    assert len(events) >= 3
    assert events[0] == {"type": "log", "message": "Running syntax formatter on SQL statement..."}
    assert events[-1] == {"type": "success", "message": "SQL formatted successfully."}

    found_events = [e for e in events if e.get("type") == "found"]
    assert len(found_events) > 0
    assert "SELECT" in found_events[0]["message"]
