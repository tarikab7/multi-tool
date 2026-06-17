import pytest
import os
import tempfile
import json
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
import main
from main import app, active_tasks

client = TestClient(app)

@pytest.fixture(autouse=True)
def mock_config_file(mocker):
    # Create a temporary config file path to mock main.CONFIG_FILE
    fd, path = tempfile.mkstemp()
    os.close(fd)

    # Pre-populate with empty settings to be safe
    with open(path, 'w') as f:
        json.dump({"spotify_client_id": "test_id", "spotify_client_secret": "test_secret"}, f)

    mocker.patch("main.CONFIG_FILE", path)

    yield path

    # Cleanup after test
    if os.path.exists(path):
        os.remove(path)

def test_get_settings():
    response = client.get("/api/settings")
    assert response.status_code == 200
    data = response.json()
    assert "spotify_client_id" in data
    assert data["spotify_client_id"] == "test_id"

def test_update_settings():
    new_settings = {
        "spotify_client_id": "new_id",
        "spotify_client_secret": "new_secret",
        "youtube_api_keys": ["key1"],
        "last_fm_api_key": "lastfm"
    }
    response = client.post("/api/settings", json=new_settings)
    assert response.status_code == 200
    assert response.json() == {"status": "success"}

    # Verify the settings were updated
    response = client.get("/api/settings")
    assert response.status_code == 200
    assert response.json()["spotify_client_id"] == "new_id"

def test_run_tool(mocker):
    # Mock active_tasks to prevent real async tasks from starting
    mocker.patch("main.active_tasks", {})

    # We must patch asyncio.create_task to prevent background task execution
    # and "no running event loop" errors
    mock_create_task = mocker.patch("asyncio.create_task")

    response = client.post("/api/run/word_counter", json={"text": "hello world"})
    assert response.status_code == 200
    data = response.json()
    assert "task_id" in data

    # Verify task was created in registry
    assert data["task_id"] in main.active_tasks
    task_info = main.active_tasks[data["task_id"]]
    assert task_info["status"] == "running"

    # Verify create_task was called
    mock_create_task.assert_called_once()

def test_run_invalid_tool():
    response = client.post("/api/run/nonexistent_tool", json={})
    assert response.status_code == 404
