from fastapi.testclient import TestClient
from main import app, active_tasks

client = TestClient(app)

def test_cancel_task_missing_task():
    # Make sure active_tasks is empty for the non-existent task ID
    task_id = "non-existent-task-id"
    if task_id in active_tasks:
        del active_tasks[task_id]

    response = client.post(f"/api/cancel/{task_id}")

    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found."}
