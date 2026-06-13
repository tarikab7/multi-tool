import pytest
from unittest.mock import patch
from tools.network_diagnostics import query_doh_record

def test_query_doh_record_requests_error():
    with patch("tools.network_diagnostics.requests.get") as mock_get:
        mock_get.side_effect = Exception("Network error")
        result = query_doh_record("example.com", "A")
        assert result == []
