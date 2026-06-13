import pytest
from pydantic import ValidationError
from fastapi.testclient import TestClient
from main import app, Settings
import httpx
from unittest.mock import patch, AsyncMock

client = TestClient(app)

def test_settings_validation_valid():
    settings = Settings(
        spotify_client_id="a"*32,
        spotify_client_secret="b"*32,
        youtube_api_keys=["AIzaSy_test_key_123"],
        last_fm_api_key="c"*32
    )
    assert settings.spotify_client_id == "a"*32

def test_settings_validation_invalid_spotify():
    with pytest.raises(ValidationError):
        Settings(spotify_client_id="invalid_length")

def test_settings_validation_invalid_youtube():
    with pytest.raises(ValidationError):
        Settings(youtube_api_keys=["invalid_key_format"])

@pytest.mark.asyncio
@patch('httpx.AsyncClient.post', new_callable=AsyncMock)
@patch('httpx.AsyncClient.get', new_callable=AsyncMock)
async def test_settings_verify_endpoint(mock_get, mock_post):
    # Mock Spotify token success
    mock_response_spotify = httpx.Response(200, json={"access_token": "token"})
    mock_post.return_value = mock_response_spotify

    # Mock YouTube success
    mock_response_youtube = httpx.Response(200, json={"items": []})

    # Mock LastFM success
    mock_response_lastfm = httpx.Response(200, json={"topartists": []})

    mock_get.side_effect = [mock_response_youtube, mock_response_lastfm]

    payload = {
        "spotify_client_id": "a"*32,
        "spotify_client_secret": "b"*32,
        "youtube_api_keys": ["AIzaSy1234567890"],
        "last_fm_api_key": "c"*32
    }

    # Since it's a test client, we can just hit the API endpoint
    response = client.post("/api/settings/verify", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["spotify"] == "valid"
    assert "valid" in data["youtube"]
    assert data["last_fm"] == "valid"
