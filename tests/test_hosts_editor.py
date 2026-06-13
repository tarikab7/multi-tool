import pytest
from unittest.mock import patch, mock_open
from tools.hosts_editor import add_hosts_entry

def test_add_hosts_entry_success():
    with patch("builtins.open", mock_open()) as mocked_file:
        domain = "example.com"
        success, result = add_hosts_entry(domain)
        assert success is True
        assert result == f"Successfully blocked {domain} locally."
        mocked_file.assert_called_once()
        mocked_file().write.assert_called_once_with(f"\n127.0.0.1 {domain} # blocked by Antigravity Suite\n")

def test_add_hosts_entry_permission_error():
    with patch("builtins.open", side_effect=PermissionError):
        domain = "example.com"
        success, result = add_hosts_entry(domain)
        assert success is False
        assert result == f"echo '127.0.0.1 {domain} # blocked' | sudo tee -a /etc/hosts"
