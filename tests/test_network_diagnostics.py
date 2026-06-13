import asyncio
import subprocess
import pytest
from unittest.mock import AsyncMock, patch

from tools import network_diagnostics

@pytest.mark.asyncio
async def test_run_ping_command_generation():
    host = "127.0.0.1"

    mock_process = AsyncMock()
    mock_process.communicate.return_value = (b"mock output", b"")
    mock_process.returncode = 0

    with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
        mock_exec.return_value = mock_process

        success, output = await network_diagnostics.run_ping(host)

        # Verify the ping was called with correct arguments
        mock_exec.assert_called_once_with(
            "ping", "-c", "4", "-w", "5", host,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # Verify return logic
        assert success is True
        assert output == "mock output"
