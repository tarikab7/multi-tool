import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from tools.utils import ToolEvent, yield_log, yield_progress, yield_success, yield_error
from main import run_tool_task

def test_tool_event_to_dict():
    event = ToolEvent(type="log", message="test message")
    assert event.to_dict() == {"type": "log", "message": "test message"}

def test_yield_log():
    event = yield_log("hello")
    assert isinstance(event, ToolEvent)
    assert event.to_dict() == {"type": "log", "message": "hello"}

def test_yield_progress():
    event = yield_progress(50.5)
    assert isinstance(event, ToolEvent)
    assert event.to_dict() == {"type": "progress", "percent": 50.5}

def test_yield_success():
    event = yield_success("done", {"result": "ok"})
    assert isinstance(event, ToolEvent)
    assert event.to_dict() == {"type": "success", "message": "done", "result": "ok"}

    event2 = yield_success("done")
    assert event2.to_dict() == {"type": "success", "message": "done"}

def test_yield_error():
    event = yield_error("failed")
    assert isinstance(event, ToolEvent)
    assert event.to_dict() == {"type": "error", "message": "failed"}

@pytest.mark.asyncio
async def test_run_tool_task_with_to_dict():
    # Mocking active_tasks registry in main
    import main
    task_id = "test_task"
    queue = asyncio.Queue()
    main.active_tasks[task_id] = {"queue": queue, "status": "running"}

    async def dummy_tool(params):
        yield yield_log("start")
        yield yield_success("end")

    await run_tool_task(task_id, dummy_tool, {})

    events = []
    while not queue.empty():
        events.append(await queue.get())

    # We expect 3 events: log, success, and None (end of stream)
    assert len(events) == 3
    assert events[0] == {"type": "log", "message": "start"}
    assert events[1] == {"type": "success", "message": "end"}
    assert events[2] is None
    assert main.active_tasks[task_id]["status"] == "finished"

    # Clean up
    del main.active_tasks[task_id]

@pytest.mark.asyncio
async def test_run_tool_task_with_dict():
    # Test backward compatibility
    import main
    task_id = "test_task_dict"
    queue = asyncio.Queue()
    main.active_tasks[task_id] = {"queue": queue, "status": "running"}

    async def dummy_tool(params):
        yield {"type": "log", "message": "start dict"}
        yield {"type": "success", "message": "end dict"}

    await run_tool_task(task_id, dummy_tool, {})

    events = []
    while not queue.empty():
        events.append(await queue.get())

    assert len(events) == 3
    assert events[0] == {"type": "log", "message": "start dict"}
    assert events[1] == {"type": "success", "message": "end dict"}
    assert events[2] is None
    assert main.active_tasks[task_id]["status"] == "finished"

    # Clean up
    del main.active_tasks[task_id]
