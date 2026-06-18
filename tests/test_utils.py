import pytest
from tools.utils import ToolEvent, yield_log, yield_progress, yield_success, yield_error

def test_tool_event_to_dict():
    event = ToolEvent(type="test", message="hello", data={"key": "value"})
    expected = {"type": "test", "message": "hello", "data": {"key": "value"}}
    assert event.to_dict() == expected

def test_yield_log():
    event = yield_log("Test log")
    assert isinstance(event, ToolEvent)
    assert event.to_dict() == {"type": "log", "message": "Test log"}

def test_yield_progress():
    event = yield_progress(45.5)
    assert isinstance(event, ToolEvent)
    assert event.to_dict() == {"type": "progress", "progress": 45.5}

def test_yield_success_without_data():
    event = yield_success("Done")
    assert isinstance(event, ToolEvent)
    assert event.to_dict() == {"type": "success", "message": "Done"}

def test_yield_success_with_data():
    event = yield_success("Done", data={"result": 42})
    assert isinstance(event, ToolEvent)
    assert event.to_dict() == {"type": "success", "message": "Done", "data": {"result": 42}}

def test_yield_error():
    event = yield_error("Failed")
    assert isinstance(event, ToolEvent)
    assert event.to_dict() == {"type": "error", "message": "Failed"}
