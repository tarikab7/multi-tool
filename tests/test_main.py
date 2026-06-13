import pytest
import asyncio
import main

@pytest.fixture
def mock_task_id():
    task_id = "test_task_123"
    queue = asyncio.Queue()
    main.active_tasks[task_id] = {
        "queue": queue,
        "status": "running",
        "task": None
    }
    yield task_id
    # cleanup
    if task_id in main.active_tasks:
        del main.active_tasks[task_id]

async def dummy_tool(params):
    yield {"type": "log", "message": "step 1"}
    yield {"type": "log", "message": "step 2"}

async def empty_tool(params):
    # an async generator that yields nothing
    if False:
        yield

@pytest.mark.asyncio
async def test_run_tool_task_queues_all_events(mock_task_id):
    await main.run_tool_task(mock_task_id, dummy_tool, {})

    queue = main.active_tasks[mock_task_id]["queue"]
    events = []
    while not queue.empty():
        events.append(await queue.get())

    assert len(events) == 3
    assert events[0] == {"type": "log", "message": "step 1"}
    assert events[1] == {"type": "log", "message": "step 2"}
    assert events[2] is None
    assert main.active_tasks[mock_task_id]["status"] == "finished"

@pytest.mark.asyncio
async def test_run_tool_task_empty_generator(mock_task_id):
    await main.run_tool_task(mock_task_id, empty_tool, {})

    queue = main.active_tasks[mock_task_id]["queue"]
    events = []
    while not queue.empty():
        events.append(await queue.get())

    assert len(events) == 1
    assert events[0] is None
    assert main.active_tasks[mock_task_id]["status"] == "finished"
