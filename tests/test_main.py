from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_stream_logs_missing_task():
    response = client.get("/api/stream/invalid_task_id")
    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found."}
