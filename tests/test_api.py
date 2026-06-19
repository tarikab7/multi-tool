import os
import json
import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

from main import app, active_tasks, Settings

client = TestClient(app)

@pytest.fixture
def mock_config_file(tmp_path, mocker):
    config_file = tmp_path / "config.json"
    mocker.patch("main.CONFIG_FILE", str(config_file))
    return str(config_file)

def test_get_settings_empty(mock_config_file):
    response = client.get("/api/settings")
    assert response.status_code == 200
    assert response.json() == Settings().model_dump()

def test_post_settings(mock_config_file):
    settings = Settings(
        spotify_client_id="test_id",
        spotify_client_secret="test_secret",
        youtube_api_keys=["key1", "key2"],
        last_fm_api_key="test_last_fm"
    )
    response = client.post("/api/settings", json=settings.model_dump())
    assert response.status_code == 200
    assert response.json() == {"status": "success"}

    # Verify saving worked
    response = client.get("/api/settings")
    assert response.status_code == 200
    assert response.json() == settings.model_dump()

def test_run_tool_success():
    # Test valid tool
    response = client.post("/api/run/word_counter", json={"text": "Hello world"})
    assert response.status_code == 200
    data = response.json()
    assert "task_id" in data
    task_id = data["task_id"]

    assert task_id in active_tasks

def test_run_tool_not_found():
    response = client.post("/api/run/non_existent_tool", json={})
    assert response.status_code == 404
