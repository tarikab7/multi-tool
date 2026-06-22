import os
import pytest
from unittest.mock import patch, MagicMock

from tools.mp3_tagger import sanitize_filename, run

def test_sanitize_filename():
    assert sanitize_filename("A<B>C:D\"E/F\\G|H?I*J") == "A_B_C_D_E_F_G_H_I_J"
    assert sanitize_filename("Normal Filename") == "Normal Filename"

@pytest.mark.asyncio
async def test_run_missing_directory():
    params = {}
    events = [event async for event in run(params)]
    assert len(events) == 1
    assert events[0]["type"] == "error"
    assert "MP3 directory is required" in events[0]["message"]

@pytest.mark.asyncio
async def test_run_directory_does_not_exist(mocker):
    mocker.patch("os.path.isdir", return_value=False)
    params = {"mp3_directory": "/does/not/exist"}
    events = [event async for event in run(params)]
    assert len(events) == 1
    assert events[0]["type"] == "error"
    assert "does not exist" in events[0]["message"]

@pytest.mark.asyncio
async def test_run_no_mp3_files(mocker):
    mocker.patch("os.path.isdir", return_value=True)
    mocker.patch("os.listdir", return_value=["file1.txt", "file2.jpg"])
    params = {"mp3_directory": "/my/music"}
    events = [event async for event in run(params)]
    assert len(events) == 2
    assert events[0]["type"] == "log"
    assert "No MP3 files found" in events[0]["message"]
    assert events[1]["type"] == "success"
    assert "0 files processed" in events[1]["message"]

@pytest.mark.asyncio
async def test_run_success(mocker):
    mocker.patch("os.path.isdir", return_value=True)
    mocker.patch("os.listdir", return_value=["song1.mp3", "song2.MP3"])

    mock_easyid3 = mocker.MagicMock()
    mock_easyid3.get.side_effect = lambda k, d: ["Test Title"] if k == "title" else ["Test Artist"]
    mocker.patch("tools.mp3_tagger.EasyID3", return_value=mock_easyid3)

    mock_music_data = {
        "title": "Fetched Title",
        "artist": "Fetched Artist",
        "genre": "Pop",
        "album": "Hit Album",
        "cover_url": "http://example.com/cover.jpg"
    }
    mocker.patch("tools.mp3_tagger.fetch_itunes_data", return_value=mock_music_data)
    mocker.patch("tools.mp3_tagger.update_metadata", return_value="/my/music/Fetched Artist - Fetched Title.mp3")

    params = {"mp3_directory": "/my/music"}
    events = [event async for event in run(params)]

    
    types = [e["type"] for e in events]
    assert "progress" in types
    assert "success" in types

    
    logs = [e["message"] for e in events if e["type"] == "log"]
    assert any("Processing tags for: song1.mp3" in msg for msg in logs)
    assert any("Saved tag: Fetched Artist - Fetched Title.mp3" in msg for msg in logs)
