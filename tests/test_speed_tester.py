import pytest
from unittest.mock import MagicMock
from tools.speed_tester import run

@pytest.mark.asyncio
async def test_speed_tester_success(mocker):
    mock_get = mocker.patch("tools.speed_tester.requests.get")
    mock_response = MagicMock()
    # Mocking chunk data of 256KB to match chunks expected by speed_tester
    chunk_data = b"0" * 262144
    # 10MB total / 256KB chunks = 40 chunks
    mock_response.iter_content.return_value = [chunk_data] * 40
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    events = [e async for e in run({})]

    success_events = [e for e in events if e.get("type") == "success"]
    assert len(success_events) == 1
    assert "Speed Test Finished:" in success_events[0]["message"]

@pytest.mark.asyncio
async def test_speed_tester_error(mocker):
    mock_get = mocker.patch("tools.speed_tester.requests.get")
    mock_get.side_effect = Exception("Connection Refused")

    events = [e async for e in run({})]
    error_events = [e for e in events if e.get("type") == "error"]
    assert len(error_events) == 1
    assert "Speed test failed: Connection Refused" in error_events[0]["message"]
