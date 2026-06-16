from tools.utils import ToolEvent, yield_log, yield_progress, yield_success, yield_error

def test_tool_event_to_dict():
    event = ToolEvent("test_type", key1="value1", key2=2)
    assert event.to_dict() == {"type": "test_type", "key1": "value1", "key2": 2}

def test_yield_log():
    event = yield_log("This is a log message")
    assert isinstance(event, ToolEvent)
    assert event.type == "log"
    assert event.kwargs == {"message": "This is a log message"}
    assert event.to_dict() == {"type": "log", "message": "This is a log message"}

def test_yield_progress():
    event = yield_progress(45.5)
    assert isinstance(event, ToolEvent)
    assert event.type == "progress"
    assert event.kwargs == {"percent": 45.5}
    assert event.to_dict() == {"type": "progress", "percent": 45.5}

def test_yield_success_without_data():
    event = yield_success("Operation completed successfully")
    assert isinstance(event, ToolEvent)
    assert event.type == "success"
    assert event.kwargs == {"message": "Operation completed successfully"}
    assert event.to_dict() == {"type": "success", "message": "Operation completed successfully"}

def test_yield_success_with_data():
    event = yield_success("Operation completed successfully", data={"result": 42})
    assert isinstance(event, ToolEvent)
    assert event.type == "success"
    assert event.kwargs == {"message": "Operation completed successfully", "data": {"result": 42}}
    assert event.to_dict() == {"type": "success", "message": "Operation completed successfully", "data": {"result": 42}}

def test_yield_error():
    event = yield_error("An error occurred")
    assert isinstance(event, ToolEvent)
    assert event.type == "error"
    assert event.kwargs == {"message": "An error occurred"}
    assert event.to_dict() == {"type": "error", "message": "An error occurred"}
