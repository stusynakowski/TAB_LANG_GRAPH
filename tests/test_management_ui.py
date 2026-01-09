import pytest
from unittest.mock import patch, MagicMock
from src.management_ui import get_status, toggle_status

def test_ui_get_status_success():
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"status": "active"}
        
        status = get_status()
        assert status['status'] == "active"

def test_ui_get_status_fail():
    with patch('requests.get') as mock_get:
        mock_get.side_effect = Exception("Conn err")
        status = get_status()
        assert status['status'] == "Disconnected"

def test_ui_toggle_status():
    with patch('requests.post') as mock_post:
        mock_post.return_value.status_code = 200
        
        toggle_status("active")
        
        # Should call pause
        mock_post.assert_called_once()
        assert "action=pause" in mock_post.call_args[0][0]

    with patch('requests.post') as mock_post:
        toggle_status("paused")
        assert "action=resume" in mock_post.call_args[0][0]
