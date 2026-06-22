import pytest
import os
import requests
from tools.qr_generator import run, generate_qr_sync

@pytest.mark.asyncio
async def test_missing_parameters():
    params = {"text": ""}
    events = [event async for event in run(params)]
    assert len(events) == 1
    assert events[0]["type"] == "error"
    assert "Both text/link content and output image path are required" in events[0]["message"]

@pytest.mark.asyncio
async def test_invalid_extension():
    params = {"text": "hello", "output_path": "output.jpg"}
    events = [event async for event in run(params)]
    assert len(events) == 1
    assert events[0]["type"] == "error"
    assert "Output path must end with '.png'" in events[0]["message"]

@pytest.mark.asyncio
async def test_invalid_size():
    params = {"text": "hello", "output_path": "output.png", "size": "abc"}
    events = [event async for event in run(params)]
    assert len(events) == 1
    assert events[0]["type"] == "error"
    assert "Size must be a valid integer" in events[0]["message"]

@pytest.mark.asyncio
async def test_successful_generation(mocker):
    params = {"text": "hello", "output_path": "test_output.png", "size": "300"}

    mock_response = mocker.Mock()
    mock_response.content = b"fake_png_data"
    mock_get = mocker.patch("requests.get", return_value=mock_response)

    # Run the generator
    events = [event async for event in run(params)]

    # Assert successful flow events
    assert len(events) == 4
    assert events[0]["type"] == "log"
    assert "Querying QR Server API" in events[0]["message"]

    assert events[1]["type"] == "progress"
    assert events[1]["percent"] == 100.0

    assert events[2]["type"] == "log"
    assert "QR Code successfully saved" in events[2]["message"]

    assert events[3]["type"] == "success"
    assert events[3]["message"] == "QR Code generated."

    # Verify file was written with mocked content
    assert os.path.exists("test_output.png")
    with open("test_output.png", "rb") as f:
        assert f.read() == b"fake_png_data"

    # Clean up
    os.remove("test_output.png")
    mock_get.assert_called_once()

@pytest.mark.asyncio
async def test_api_failure(mocker):
    params = {"text": "hello", "output_path": "test_output.png", "size": "300"}

    # Setup mock to raise HTTPError
    mock_get = mocker.patch("requests.get", side_effect=requests.exceptions.HTTPError("API failed"))

    # Run the generator
    events = [event async for event in run(params)]

    assert len(events) == 2
    assert events[0]["type"] == "log"
    assert "Querying QR Server API" in events[0]["message"]

    assert events[1]["type"] == "error"
    assert "QR Code generation failed" in events[1]["message"]
    assert "API failed" in events[1]["message"]

    mock_get.assert_called_once()
