import os
import json
import asyncio
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
import pytest
import main
from main import app, active_tasks, Settings

client = TestClient(app)

@pytest.fixture
def mock_config(tmp_path, mocker):
    test_config_path = tmp_path / "config.json"
    mocker.patch("main.CONFIG_FILE", str(test_config_path))
    return str(test_config_path)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200 or response.status_code == 404

def test_get_settings(mock_config):
    response = client.get("/api/settings")
    assert response.status_code == 200
    data = response.json()
    assert "spotify_client_id" in data

def test_update_settings(mock_config):
    payload = {
        "spotify_client_id": "test_id",
        "spotify_client_secret": "test_secret",
        "youtube_api_keys": ["key1"],
        "last_fm_api_key": "test_last_fm"
    }
    response = client.post("/api/settings", json=payload)
    assert response.status_code == 200
    assert response.json() == {"status": "success"}

    # Verify get works after post
    response = client.get("/api/settings")
    assert response.json()["spotify_client_id"] == "test_id"

def test_run_tool(mock_config, mocker):
    # Mock create_task to avoid running actual tasks in synchronous TestClient
    mock_create_task = mocker.patch("asyncio.create_task")
    mock_task = MagicMock()
    mock_create_task.return_value = mock_task

    payload = {"text": "hello world"}
    response = client.post("/api/run/word_counter", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "task_id" in data

    task_id = data["task_id"]
    assert task_id in main.active_tasks

    # Clean up
    del main.active_tasks[task_id]

def test_run_tool_not_found(mock_config):
    payload = {"text": "hello"}
    response = client.post("/api/run/nonexistent_tool", json=payload)
    assert response.status_code == 404

def test_cancel_task(mock_config, mocker):
    mock_task = MagicMock()

    # Create fake task
    task_id = "fake_task_id"
    main.active_tasks[task_id] = {
        "queue": asyncio.Queue(),
        "status": "running",
        "task": mock_task
    }

    response = client.post(f"/api/cancel/{task_id}")
    assert response.status_code == 200
    assert response.json() == {"status": "cancelled"}

    # Verify task was cancelled
    mock_task.cancel.assert_called_once()
    assert main.active_tasks[task_id]["status"] == "cancelled"

    # Clean up
    del main.active_tasks[task_id]

def test_cancel_task_not_found(mock_config):
    response = client.post("/api/cancel/invalid_id")
    assert response.status_code == 404

def test_stream_logs_not_found(mock_config):
    response = client.get("/api/stream/invalid_id")
    assert response.status_code == 404

def test_browse_path():
    response = client.get("/api/browse?path=.")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
