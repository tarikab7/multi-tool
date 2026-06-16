import pytest
from fastapi.testclient import TestClient
import json
import os
from unittest.mock import MagicMock

from main import app
import main

client = TestClient(app)

@pytest.fixture
def test_config(tmp_path, mocker):
    config_file = tmp_path / "test_config.json"
    mocker.patch("main.CONFIG_FILE", str(config_file))
    return config_file

def test_get_settings_empty(test_config):
    response = client.get("/api/settings")
    assert response.status_code == 200
    assert response.json() == {
        "spotify_client_id": "",
        "spotify_client_secret": "",
        "youtube_api_keys": [],
        "last_fm_api_key": ""
    }

def test_post_settings(test_config):
    new_settings = {
        "spotify_client_id": "test_id",
        "spotify_client_secret": "test_secret",
        "youtube_api_keys": ["key1", "key2"],
        "last_fm_api_key": "lastfm_key"
    }
    response = client.post("/api/settings", json=new_settings)
    assert response.status_code == 200
    assert response.json() == {"status": "success"}

    with open(test_config, "r") as f:
        data = json.load(f)
        assert data["spotify_client_id"] == "test_id"

def test_run_tool(test_config, mocker):
    mocker.patch("asyncio.create_task")
    response = client.post("/api/run/word_counter", json={"text": "hello world"})
    assert response.status_code == 200
    data = response.json()
    assert "task_id" in data
    task_id = data["task_id"]

    assert task_id in main.active_tasks
    assert main.active_tasks[task_id]["status"] == "running"

def test_cancel_task(test_config):
    task_id = "test_cancel_id"
    mock_task = MagicMock()
    main.active_tasks[task_id] = {
        "queue": MagicMock(),
        "status": "running",
        "task": mock_task
    }

    response = client.post(f"/api/cancel/{task_id}")
    assert response.status_code == 200
    assert response.json() == {"status": "cancelled"}
    mock_task.cancel.assert_called_once()
    assert main.active_tasks[task_id]["status"] == "cancelled"

def test_run_invalid_tool(test_config):
    response = client.post("/api/run/invalid_tool_name", json={})
    assert response.status_code == 404
