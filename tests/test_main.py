from fastapi.testclient import TestClient
from main import app, active_tasks
import pytest

client = TestClient(app)

def test_cancel_task_missing():
    # Attempt to cancel a task that does not exist
    response = client.post("/api/cancel/invalid-task-id")

    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found."}

def test_cancel_task_already_finished():
    # Setup a mock task that is already finished
    task_id = "finished-task-id"
    active_tasks[task_id] = {
        "status": "finished",
        "task": None
    }

    response = client.post(f"/api/cancel/{task_id}")

    assert response.status_code == 200
    assert response.json() == {"status": "already_finished"}

    # Cleanup
    del active_tasks[task_id]

def test_cancel_task_running():
    class MockTask:
        def __init__(self):
            self.cancelled = False
        def cancel(self):
            self.cancelled = True

    task_id = "running-task-id"
    mock_task = MockTask()

    active_tasks[task_id] = {
        "status": "running",
        "task": mock_task
    }

    response = client.post(f"/api/cancel/{task_id}")

    assert response.status_code == 200
    assert response.json() == {"status": "cancelled"}
    assert active_tasks[task_id]["status"] == "cancelled"
    assert mock_task.cancelled is True

    # Cleanup
    del active_tasks[task_id]
