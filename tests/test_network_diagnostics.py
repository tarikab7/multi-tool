import pytest
from unittest.mock import patch, MagicMock
from tools.network_diagnostics import query_geoip

def test_query_geoip_empty_response():
    # Scenario 1: requests.get returns status_code != 200
    with patch('tools.network_diagnostics.requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        result = query_geoip("invalid.host")
        assert result == {}

def test_query_geoip_exception():
    # Scenario 2: requests.get raises an exception
    with patch('tools.network_diagnostics.requests.get') as mock_get:
        mock_get.side_effect = Exception("Connection Error")

        result = query_geoip("some.host")
        assert result == {"error": "Connection Error"}

def test_query_geoip_invalid_json():
    # Scenario 3: requests.get returns status_code == 200 but response.json() raises an exception
    with patch('tools.network_diagnostics.requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_get.return_value = mock_response

        result = query_geoip("some.host")
        assert result == {"error": "Invalid JSON"}
