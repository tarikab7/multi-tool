import pytest
from pydantic import ValidationError
from main import Settings

def test_settings_validation():
    # Valid keys
    s = Settings(
        spotify_client_id="a"*32,
        spotify_client_secret="b"*32,
        youtube_api_keys=["AIzaSySomeKey"]
    )
    assert s.spotify_client_id == "a"*32

    # Invalid spotify key
    with pytest.raises(ValidationError):
        Settings(spotify_client_id="a"*31)

    # Invalid youtube key
    with pytest.raises(ValidationError):
        Settings(youtube_api_keys=["invalid"])
