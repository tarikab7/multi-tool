import pytest
from unittest.mock import patch
from tools.ssl_expiry_checker import run

@pytest.mark.asyncio
async def test_ssl_expiry_checker_port_parsing():
    """Test that the SSL expiry checker correctly parses the host and port."""

    # Test without port (should default to 443)
    params = {"host": "example.com"}
    with patch("socket.create_connection") as mock_conn, \
         patch("ssl.create_default_context"):
        mock_conn.side_effect = Exception("Stop execution")

        results = [res async for res in run(params)]

        mock_conn.assert_called_once()
        args, _ = mock_conn.call_args
        assert args[0] == ("example.com", 443)
        assert any(r.get("type") == "error" and "Stop execution" in r.get("message", "") for r in results)

    # Test with custom port as string
    params = {"host": "example.com", "port": "8443"}
    with patch("socket.create_connection") as mock_conn, \
         patch("ssl.create_default_context"):
        mock_conn.side_effect = Exception("Stop execution")

        results = [res async for res in run(params)]

        mock_conn.assert_called_once()
        args, _ = mock_conn.call_args
        assert args[0] == ("example.com", 8443)
        assert any(r.get("type") == "error" and "Stop execution" in r.get("message", "") for r in results)

    # Test with custom port as integer
    params = {"host": "example.com", "port": 8443}
    with patch("socket.create_connection") as mock_conn, \
         patch("ssl.create_default_context"):
        mock_conn.side_effect = Exception("Stop execution")

        results = [res async for res in run(params)]

        mock_conn.assert_called_once()
        args, _ = mock_conn.call_args
        assert args[0] == ("example.com", 8443)
        assert any(r.get("type") == "error" and "Stop execution" in r.get("message", "") for r in results)

    # Test with host containing port "example.com:443"
    params = {"host": "example.com:8443"}
    with patch("socket.create_connection") as mock_conn, \
         patch("ssl.create_default_context"):
        mock_conn.side_effect = Exception("Stop execution")

        results = [res async for res in run(params)]

        mock_conn.assert_called_once()
        args, _ = mock_conn.call_args
        # The port in the host should be stripped and the default (443) or provided port should be used.
        assert args[0] == ("example.com", 443)
        assert any(r.get("type") == "error" and "Stop execution" in r.get("message", "") for r in results)
