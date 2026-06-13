import json
import pytest
from unittest.mock import patch, mock_open
from main import save_config, CONFIG_FILE

def test_save_config_success():
    config_data = {"key": "value"}
    m_open = mock_open()

    with patch("builtins.open", m_open):
        with patch("main.json.dump") as mock_json_dump:
            save_config(config_data)

            m_open.assert_called_once_with(CONFIG_FILE, 'w')
            mock_json_dump.assert_called_once_with(config_data, m_open(), indent=4)

def test_save_config_exception(capsys):
    config_data = {"key": "value"}
    error_message = "Permission denied"

    with patch("builtins.open", side_effect=Exception(error_message)):
        save_config(config_data)

    captured = capsys.readouterr()
    assert f"Error saving config: {error_message}" in captured.out
