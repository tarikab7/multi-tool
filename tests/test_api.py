import pytest
from fastapi.testclient import TestClient
from main import app, active_tasks
import uuid

client = TestClient(app)

def test_get_settings():
    response = client.get("/api/settings")
    assert response.status_code == 200
    data = response.json()
    assert "spotify_client_id" in data
    assert "spotify_client_secret" in data
    assert "youtube_api_keys" in data
    assert "last_fm_api_key" in data

def test_post_settings():
    payload = {
        "spotify_client_id": "test_id",
        "spotify_client_secret": "test_secret",
        "youtube_api_keys": ["key1", "key2"],
        "last_fm_api_key": "test_lastfm"
    }
    response = client.post("/api/settings", json=payload)
    assert response.status_code == 200
    assert response.json() == {"status": "success"}

    # Verify settings were updated
    response = client.get("/api/settings")
    assert response.json() == payload

def test_run_tool():
    payload = {"text": "Hello world"}
    response = client.post("/api/run/word_counter", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "task_id" in data

    task_id = data["task_id"]
    assert task_id in active_tasks

    # We shouldn't wait too long as the test needs to finish. The tool is quick.
    # Cancel just to test cancellation endpoint
    cancel_response = client.post(f"/api/cancel/{task_id}")
    assert cancel_response.status_code == 200
    cancel_data = cancel_response.json()
    assert cancel_data["status"] in ["cancelled", "already_finished"]

def test_cancel_nonexistent_task():
    response = client.post("/api/cancel/invalid-task-id")
    assert response.status_code == 404

def test_run_nonexistent_tool():
    response = client.post("/api/run/invalid_tool", json={})
    assert response.status_code == 404

def test_stream_nonexistent_task():
    response = client.get("/api/stream/invalid-task-id")
    assert response.status_code == 404
