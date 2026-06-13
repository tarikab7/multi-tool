import pytest
from unittest.mock import mock_open, patch
from tools.hosts_editor import add_hosts_entry, HOSTS_PATH

def test_add_hosts_entry_success():
    domain = "example.com"
    expected_line = f"\n127.0.0.1 {domain} # blocked by Antigravity Suite\n"

    # Mock 'open' to simulate successful writing
    m_open = mock_open()
    with patch("builtins.open", m_open):
        success, message = add_hosts_entry(domain)

    # Assert successful return values
    assert success is True
    assert message == f"Successfully blocked {domain} locally."

    # Assert 'open' was called with the right file and mode
    m_open.assert_called_once_with(HOSTS_PATH, 'a')

    # Assert the correct line was written to the file
    m_open().write.assert_called_once_with(expected_line)

def test_add_hosts_entry_permission_error():
    domain = "example.com"

    # Mock 'open' to raise a PermissionError
    m_open = mock_open()
    m_open.side_effect = PermissionError("Permission denied")

    with patch("builtins.open", m_open):
        success, message = add_hosts_entry(domain)

    # Assert it returns False and the expected manual command
    assert success is False
    assert message == f"echo '127.0.0.1 {domain} # blocked' | sudo tee -a /etc/hosts"

    # Assert 'open' was called before raising the exception
    m_open.assert_called_once_with(HOSTS_PATH, 'a')
