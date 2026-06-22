import pytest
from fastapi.testclient import TestClient
from main import app, Settings, load_config
from pydantic import ValidationError

client = TestClient(app)

def test_settings_schema_valid():
    
    settings = Settings(
        spotify_client_id="1234567890abcdef1234567890abcdef",
        spotify_client_secret="abcdef1234567890abcdef1234567890",
        youtube_api_keys=["AIzaSyTest123", "AIzaSyAnotherKey"],
        last_fm_api_key="somelastfmkey123"
    )
    assert settings.spotify_client_id == "1234567890abcdef1234567890abcdef"

def test_settings_schema_invalid_spotify():
    
    with pytest.raises(ValidationError):
        Settings(spotify_client_id="short")

def test_get_settings(mocker):
    mocker.patch("main.load_config", return_value={"spotify_client_id": "1234567890abcdef1234567890abcdef"})
    response = client.get("/api/settings")
    assert response.status_code == 200
    assert response.json()["spotify_client_id"] == "1234567890abcdef1234567890abcdef"

def test_post_settings_valid(mocker):
    mocker.patch("main.save_config")
    response = client.post("/api/settings", json={
        "spotify_client_id": "1234567890abcdef1234567890abcdef",
        "spotify_client_secret": "1234567890abcdef1234567890abcdef",
        "youtube_api_keys": ["AIzaSyTestKey"],
        "last_fm_api_key": "lastfm123"
    })
    assert response.status_code == 200

def test_post_settings_invalid_youtube():
    response = client.post("/api/settings", json={
        "spotify_client_id": "1234567890abcdef1234567890abcdef",
        "youtube_api_keys": ["InvalidKey"]
    })
    assert response.status_code == 422
    assert "Invalid YouTube API Key format" in response.text

@pytest.mark.asyncio
async def test_verify_settings_endpoint(mocker):
    
    mocker.patch("main.load_config", return_value={
        "spotify_client_id": "1234567890abcdef1234567890abcdef",
        "spotify_client_secret": "1234567890abcdef1234567890abcdef",
        "youtube_api_keys": ["AIzaSyValid", "AIzaSyInvalid"],
        "last_fm_api_key": "lastfm123"
    })

    class MockResponse:
        def __init__(self, status_code, json_data=None):
            self.status_code = status_code
            self._json_data = json_data or {}
        def json(self):
            return self._json_data

    async def mock_post(url, *args, **kwargs):
        if "spotify.com" in str(url):
            return MockResponse(200)
        return MockResponse(404)

    async def mock_get(url, *args, **kwargs):
        if "youtube" in str(url):
            if "AIzaSyValid" in str(url):
                return MockResponse(200)
            else:
                return MockResponse(401)
        if "audioscrobbler" in str(url):
            return MockResponse(200, {"results": {}})
        return MockResponse(404)

    mock_client_instance = mocker.MagicMock()
    mock_client_instance.post = mocker.AsyncMock(side_effect=mock_post)
    mock_client_instance.get = mocker.AsyncMock(side_effect=mock_get)
    mock_client_instance.__aenter__.return_value = mock_client_instance

    mocker.patch("main.httpx.AsyncClient", return_value=mock_client_instance)

    
    response = client.get("/api/settings/verify")

    assert response.status_code == 200
    data = response.json()
    assert data["spotify"] == "valid"
    assert data["youtube"] == ["valid", "invalid"]
    assert data["lastfm"] == "valid"
