import pytest
from unittest.mock import patch, mock_open
from tools.hosts_editor import read_hosts_entries

@patch('os.path.exists', return_value=True)
def test_read_hosts_entries_happy_path(mock_exists):
    mock_file_content = """
# This is a comment
127.0.0.1 localhost
::1 localhost
0.0.0.0 block.example.com
192.168.1.1 ignore.me # Not a loopback

127.0.0.1 multiple domains here
"""
    with patch('builtins.open', mock_open(read_data=mock_file_content)):
        rules = read_hosts_entries()

    assert rules == [
        ("127.0.0.1", ["localhost"]),
        ("::1", ["localhost"]),
        ("0.0.0.0", ["block.example.com"]),
        ("127.0.0.1", ["multiple", "domains", "here"]),
    ]
    mock_exists.assert_called_once()

@patch('os.path.exists', return_value=False)
def test_read_hosts_entries_file_not_found(mock_exists):
    rules = read_hosts_entries()
    assert rules == []
    mock_exists.assert_called_once()

@patch('os.path.exists', return_value=True)
def test_read_hosts_entries_handles_exception(mock_exists):
    with patch('builtins.open', side_effect=PermissionError):
        rules = read_hosts_entries()
        assert rules == []
        mock_exists.assert_called_once()
