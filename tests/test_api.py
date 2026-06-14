import json
import pytest
from fastapi.testclient import TestClient
from main import app, active_tasks
import os

client = TestClient(app)

@pytest.fixture(autouse=True)
def clean_tasks_and_settings(mocker):
    # Cleanup task registry
    active_tasks.clear()

    # Mock config file path to a temp test file
    test_config = os.path.join(os.path.dirname(os.path.dirname(__file__)), "test_config.json")
    mocker.patch("main.CONFIG_FILE", test_config)

    # Ensure it's clean before test
    if os.path.exists(test_config):
        os.remove(test_config)

    yield

    # Cleanup after test
    active_tasks.clear()
    if os.path.exists(test_config):
        os.remove(test_config)

def test_get_settings():
    response = client.get("/api/settings")
    assert response.status_code == 200
    data = response.json()
    assert "spotify_client_id" in data
    assert "youtube_api_keys" in data

def test_post_settings():
    new_settings = {
        "spotify_client_id": "test_client",
        "spotify_client_secret": "test_secret",
        "youtube_api_keys": ["key1", "key2"],
        "last_fm_api_key": "test_last_fm"
    }
    response = client.post("/api/settings", json=new_settings)
    assert response.status_code == 200
    assert response.json() == {"status": "success"}

    # Verify it updated
    response = client.get("/api/settings")
    assert response.status_code == 200
    data = response.json()
    assert data["spotify_client_id"] == "test_client"
    assert data["youtube_api_keys"] == ["key1", "key2"]

def test_run_tool_and_cancel():
    # Start a run for a valid tool
    payload = {"text": "hello world"}
    response = client.post("/api/run/word_counter", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "task_id" in data
    task_id = data["task_id"]

    # Wait for the task to start processing and test cancel
    # If the task finished too quickly, cancel should return already_finished
    # However we will explicitly check the status
    if active_tasks[task_id]["status"] == "running":
        response = client.post(f"/api/cancel/{task_id}")
        assert response.status_code == 200
        assert response.json() == {"status": "cancelled"}
        assert active_tasks[task_id]["status"] == "cancelled"
    else:
        # It already finished, so cancellation is a no-op that returns already_finished
        response = client.post(f"/api/cancel/{task_id}")
        assert response.status_code == 200
        assert response.json() == {"status": "already_finished"}

def test_run_tool_not_found():
    response = client.post("/api/run/nonexistent_tool", json={})
    assert response.status_code == 404

def test_cancel_nonexistent_task():
    response = client.post("/api/cancel/invalid-id")
    assert response.status_code == 404

def test_stream_logs_invalid_task():
    response = client.get("/api/stream/invalid-id")
    assert response.status_code == 404
