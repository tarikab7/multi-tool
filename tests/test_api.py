import pytest
from fastapi.testclient import TestClient
from main import app, active_tasks, Settings
import json
import uuid
import os
import asyncio

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code in [200, 404]

def test_get_settings(mocker):
    mocker.patch("main.load_config", return_value={"spotify_client_id": "test_id"})
    response = client.get("/api/settings")
    assert response.status_code == 200
    assert response.json()["spotify_client_id"] == "test_id"

def test_update_settings(mocker):
    mocker.patch("main.save_config")
    response = client.post("/api/settings", json={"spotify_client_id": "new_id"})
    assert response.status_code == 200
    assert response.json()["status"] == "success"

def test_run_tool_not_found():
    response = client.post("/api/run/non_existent_tool", json={})
    assert response.status_code == 404

@pytest.fixture
def clean_active_tasks():
    yield
    active_tasks.clear()

def test_run_tool_endpoint_success(mocker, clean_active_tasks):
    # Mocking active_tasks registry and task
    mocker.patch("main.load_config", return_value={})

    # We use a mocked generator that does not sleep
    async def mock_run(params):
        yield {"type": "log", "message": "mock"}
        yield {"type": "success", "message": "mock"}

    mocker.patch("tools.word_counter.run", side_effect=mock_run)

    response = client.post("/api/run/word_counter", json={"text": "Hello world"})
    assert response.status_code == 200
    assert "task_id" in response.json()
    task_id = response.json()["task_id"]
    assert task_id in active_tasks
    assert active_tasks[task_id]["status"] in ["running", "finished"]

def test_cancel_task_not_found(clean_active_tasks):
    response = client.post("/api/cancel/non_existent_task")
    assert response.status_code == 404

def test_cancel_task_success(mocker, clean_active_tasks):
    mock_task = mocker.MagicMock()
    test_task_id = str(uuid.uuid4())

    # We can't easily mock an asyncio queue without an event loop
    # We just need any object so we skip Queue
    mock_queue = mocker.MagicMock()
    active_tasks[test_task_id] = {
        "queue": mock_queue,
        "status": "running",
        "task": mock_task
    }

    response = client.post(f"/api/cancel/{test_task_id}")
    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"
    mock_task.cancel.assert_called_once()
    assert active_tasks[test_task_id]["status"] == "cancelled"

def test_stream_logs_not_found():
    response = client.get("/api/stream/non_existent_task")
    assert response.status_code == 404

def test_browse_path_not_found():
    response = client.get("/api/browse?path=/non/existent/path/123456")
    assert response.status_code == 404

def test_browse_path_success(mocker, tmp_path):
    # create a tmp dir
    d = tmp_path / "subdir"
    d.mkdir()
    f = d / "file.txt"
    f.write_text("hello")

    response = client.get(f"/api/browse?path={d}")
    assert response.status_code == 200
    data = response.json()
    assert data["current_path"] == str(d)
    assert len(data["items"]) >= 1
