import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import asyncio
from tools.port_scanner import scan_single_port

@pytest.mark.asyncio
async def test_scan_single_port_success():
    mock_reader = AsyncMock()
    mock_writer = MagicMock()
    mock_writer.wait_closed = AsyncMock()

    # asyncio.wait_for wraps the coroutine returned by asyncio.open_connection
    async def mock_open_connection(*args, **kwargs):
        return (mock_reader, mock_writer)

    with patch('asyncio.open_connection', new=mock_open_connection):
        port, is_open = await scan_single_port('127.0.0.1', 80)
        assert port == 80
        assert is_open is True
        mock_writer.close.assert_called_once()
        mock_writer.wait_closed.assert_awaited_once()

@pytest.mark.asyncio
async def test_scan_single_port_timeout():
    async def mock_open_connection(*args, **kwargs):
        # We need this to simulate a timeout by sleeping longer than the timeout
        await asyncio.sleep(2.0)
        return (AsyncMock(), MagicMock())

    with patch('asyncio.open_connection', new=mock_open_connection):
        port, is_open = await scan_single_port('127.0.0.1', 80)
        assert port == 80
        assert is_open is False

@pytest.mark.asyncio
async def test_scan_single_port_connection_refused():
    async def mock_open_connection(*args, **kwargs):
        raise ConnectionRefusedError("Refused")

    with patch('asyncio.open_connection', new=mock_open_connection):
        port, is_open = await scan_single_port('127.0.0.1', 80)
        assert port == 80
        assert is_open is False
