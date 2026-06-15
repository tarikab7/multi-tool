import pytest
import httpx
from pydantic import ValidationError
from fastapi.testclient import TestClient

from main import app, Settings

client = TestClient(app)

def test_settings_schema_valid():
    # Valid spotify keys
    s = Settings(
        spotify_client_id="a" * 32,
        spotify_client_secret="b" * 32,
        youtube_api_keys=["AIzaSyTest123"],
        last_fm_api_key="12345"
    )
    assert s.spotify_client_id == "a" * 32
    assert s.youtube_api_keys == ["AIzaSyTest123"]

def test_settings_schema_invalid_spotify():
    with pytest.raises(ValidationError) as exc:
        Settings(spotify_client_id="short")
    assert "Spotify keys must be 32 hex characters" in str(exc.value)

    with pytest.raises(ValidationError) as exc2:
        Settings(spotify_client_secret="invalid_hex_chars_12345678901234")
    assert "Spotify keys must be 32 hex characters" in str(exc2.value)

def test_settings_schema_invalid_youtube():
    with pytest.raises(ValidationError) as exc:
        Settings(youtube_api_keys=["invalid_key"])
    assert "YouTube API keys must start with \"AIzaSy\"" in str(exc.value)

@pytest.mark.asyncio
async def test_verify_settings_endpoint(mocker):
    # Mock load_config
    mocker.patch("main.load_config", return_value={
        "spotify_client_id": "a"*32,
        "spotify_client_secret": "b"*32,
        "youtube_api_keys": ["AIzaSy123"],
        "last_fm_api_key": "lastfm123"
    })

    # Mock httpx responses
    mock_post = mocker.AsyncMock()
    mock_post.return_value.status_code = 200

    mock_get = mocker.AsyncMock()
    mock_get.return_value.status_code = 200

    mocker.patch("httpx.AsyncClient.post", mock_post)
    mocker.patch("httpx.AsyncClient.get", mock_get)

    # Use TestClient for the API route
    response = client.get("/api/settings/verify")
    assert response.status_code == 200
    data = response.json()
    assert data["spotify"] == "valid"
    assert data["youtube"] == "valid"
    assert data["last_fm"] == "valid"

    # Now verify missing cases
    mocker.patch("main.load_config", return_value={})
    response_missing = client.get("/api/settings/verify")
    assert response_missing.status_code == 200
    data_missing = response_missing.json()
    assert data_missing["spotify"] == "missing"
    assert data_missing["youtube"] == "missing"
    assert data_missing["last_fm"] == "missing"
