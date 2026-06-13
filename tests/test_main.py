import os
import json
from unittest.mock import patch, mock_open
import pytest

from main import load_config, CONFIG_FILE

def test_load_config_file_exists_valid_json():
    mock_data = '{"test_key": "test_value"}'
    with patch('os.path.exists', return_value=True):
        with patch('builtins.open', mock_open(read_data=mock_data)):
            result = load_config()
            assert result == {"test_key": "test_value"}

def test_load_config_file_exists_invalid_json():
    mock_data = 'invalid json'
    with patch('os.path.exists', return_value=True):
        with patch('builtins.open', mock_open(read_data=mock_data)):
            result = load_config()
            assert result == {}

def test_load_config_file_exists_empty_file():
    mock_data = ''
    with patch('os.path.exists', return_value=True):
        with patch('builtins.open', mock_open(read_data=mock_data)):
            result = load_config()
            assert result == {}

def test_load_config_file_does_not_exist():
    with patch('os.path.exists', return_value=False):
        result = load_config()
        assert result == {}

def test_load_config_file_open_permission_error():
    with patch('os.path.exists', return_value=True):
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            result = load_config()
            assert result == {}
