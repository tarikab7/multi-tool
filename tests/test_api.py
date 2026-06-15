import pytest
from fastapi.testclient import TestClient
import os
import json
import asyncio

# Import main before using it in the tests, so we can patch its constants if needed
import main
from main import app, active_tasks, load_config

client = TestClient(app)

@pytest.fixture
def mock_config_file(tmp_path, mocker):
    config_file = tmp_path / "config.json"
    mocker.patch("main.CONFIG_FILE", str(config_file))
    return config_file

def test_get_settings_empty(mock_config_file):
    response = client.get("/api/settings")
    assert response.status_code == 200
    assert response.json() == {
        "spotify_client_id": "",
        "spotify_client_secret": "",
        "youtube_api_keys": [],
        "last_fm_api_key": ""
    }

def test_post_settings(mock_config_file):
    settings_data = {
        "spotify_client_id": "test_id",
        "spotify_client_secret": "test_secret",
        "youtube_api_keys": ["key1", "key2"],
        "last_fm_api_key": "test_last_fm"
    }
    response = client.post("/api/settings", json=settings_data)
    assert response.status_code == 200
    assert response.json() == {"status": "success"}

    # Verify get_settings returns the updated config
    response = client.get("/api/settings")
    assert response.status_code == 200
    assert response.json() == settings_data

    # Verify it wrote to the file
    with open(mock_config_file, "r") as f:
        saved_data = json.load(f)
    assert saved_data == settings_data

def test_run_tool_not_found():
    response = client.post("/api/run/non_existent_tool", json={})
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

def test_run_tool_success():
    # Test a simple tool like word_counter
    response = client.post("/api/run/word_counter", json={"text": "hello world"})
    assert response.status_code == 200
    data = response.json()
    assert "task_id" in data
    task_id = data["task_id"]

    assert task_id in active_tasks
    assert active_tasks[task_id]["status"] in ("running", "finished")

def test_cancel_task_not_found():
    response = client.post("/api/cancel/nonexistent_id")
    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found."}

def test_cancel_task_success(mocker):
    # Replace the run_tool_task function in the test client's running server memory
    # Because FastAPI starts the background task, the sleep inside word_counter is apparently resolving instantly or being bypassed. Let's just create a dummy task and add it to the active_tasks dict directly, then cancel it through the endpoint to test the endpoint's logic.
    task_id = "test-cancel-id"
    import uuid
    import asyncio
    mocker.patch("uuid.uuid4", return_value=task_id)

    from unittest.mock import MagicMock
    # Put a mock task in the active_tasks registry manually
    # instead of creating a real task, just use a MagicMock that has cancel()
    dummy_task = MagicMock()

    # Queue doesn't strictly need a loop here because we only check if the endpoint doesn't crash
    # But just in case, we mock the Queue as well to avoid RuntimeError about no running event loop
    active_tasks[task_id] = {
        "queue": MagicMock(),
        "status": "running",
        "task": dummy_task
    }

    cancel_response = client.post(f"/api/cancel/{task_id}")
    assert cancel_response.status_code == 200
    assert cancel_response.json() == {"status": "cancelled"}
    assert active_tasks[task_id]["status"] == "cancelled"

    # Verify cancel was called
    dummy_task.cancel.assert_called_once()


def test_stream_logs():
    # Start a fast tool
    response = client.post("/api/run/json_minifier", json={"raw_json": '{"a": 1}'})
    task_id = response.json()["task_id"]

    # Give the task a tiny bit of time to run to finish and yield its output,
    # since it's running in background via TestClient.
    import time
    time.sleep(0.5)

    # Stream the logs
    with client.stream("GET", f"/api/stream/{task_id}") as response:
        assert response.status_code == 200
        lines = list(response.iter_lines())

        # It should yield events as SSE
        # E.g.
        # event: log
        # data: {"type": "log", "message": "Running JSON syntax parses and formatting..."}

        found_events = []
        for line in lines:
            if line.startswith("data: "):
                event_data = json.loads(line[6:])
                found_events.append(event_data)

    assert any(e.get("type") == "log" for e in found_events)
    assert any(e.get("type") == "found" for e in found_events)
    assert any(e.get("type") == "success" for e in found_events)

    # After streaming finishes and task is complete, it should be removed from active_tasks
    assert task_id not in active_tasks
