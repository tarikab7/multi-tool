import os
import json
import pytest
from fastapi.testclient import TestClient
from main import app, active_tasks

client = TestClient(app)

def test_get_settings(mocker, tmp_path):
    # Create a dummy config file
    config_file = tmp_path / "config.json"
    dummy_config = {"spotify_client_id": "test_id", "spotify_client_secret": "test_secret"}
    with open(config_file, "w") as f:
        json.dump(dummy_config, f)

    mocker.patch("main.CONFIG_FILE", str(config_file))

    response = client.get("/api/settings")
    assert response.status_code == 200
    data = response.json()
    assert data["spotify_client_id"] == "test_id"
    assert data["spotify_client_secret"] == "test_secret"

def test_update_settings(mocker, tmp_path):
    config_file = tmp_path / "config.json"
    mocker.patch("main.CONFIG_FILE", str(config_file))

    payload = {
        "spotify_client_id": "new_id",
        "spotify_client_secret": "new_secret",
        "youtube_api_keys": ["key1"],
        "last_fm_api_key": "lastfm_key"
    }

    response = client.post("/api/settings", json=payload)
    assert response.status_code == 200
    assert response.json() == {"status": "success"}

    # Verify file was written
    with open(config_file, "r") as f:
        saved_config = json.load(f)
    assert saved_config["spotify_client_id"] == "new_id"

def test_run_tool(mocker):
    # Clear active_tasks to ensure clean state
    active_tasks.clear()

    # Mock asyncio.create_task to prevent actually running the background loop in the sync test client
    mock_create_task = mocker.patch("main.asyncio.create_task")

    # We will test running 'word_counter' as an example
    payload = {"text": "hello world"}
    response = client.post("/api/run/word_counter", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert "task_id" in data
    task_id = data["task_id"]

    # Verify the task is in active_tasks registry
    assert task_id in active_tasks
    assert active_tasks[task_id]["status"] == "running"

    # Verify create_task was called
    mock_create_task.assert_called_once()
