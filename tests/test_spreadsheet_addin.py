import pytest
from unittest.mock import patch, MagicMock
from io import BytesIO
import json
# Import the module source directly or via sys.path since it is in src/ but not in a package structure
import sys
import os
sys.path.append(os.path.abspath("src"))

from spreadsheet_addin import FSF

def test_lg_call_success():
    # Mock urllib.request.urlopen
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.read.return_value = json.dumps({
        "status": "success",
        "result": "Echo: Hello"
    }).encode('utf-8')
    mock_response.__enter__.return_value = mock_response
    mock_response.__exit__.return_value = None
    
    with patch('urllib.request.urlopen', return_value=mock_response) as mock_urlopen:
        result = FSF("Echo", "Hello")
        assert result == "Echo: Hello"
        
        # Verify request
        args, _ = mock_urlopen.call_args
        req = args[0]
        assert req.full_url == "http://127.0.0.1:8000/execute"
        sent_data = json.loads(req.data)
        assert sent_data['workflow_id'] == "echo"
        # assert sent_data['arguments']['text'] == "Hello"    <-- This is wrong, FSF uses positional_args
        assert sent_data['positional_args'] == ["Hello"]

def test_lg_call_api_error():
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.read.return_value = json.dumps({
        "status": "error",
        "error_message": "Workflow failure"
    }).encode('utf-8')
    mock_response.__enter__.return_value = mock_response
    mock_response.__exit__.return_value = None
    
    with patch('urllib.request.urlopen', return_value=mock_response):
        result = FSF("Echo", "Fail")
        assert result == "Error: Workflow failure"

def test_lg_call_connection_error():
    with patch('urllib.request.urlopen', side_effect=Exception("Connection refused")):
        result = FSF("Echo", "Hello")
        assert "Error:" in result
