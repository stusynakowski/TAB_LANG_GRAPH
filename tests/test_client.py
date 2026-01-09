import pytest
from unittest.mock import patch, MagicMock
from tab_lang_graph.client import SpreadsheetClient

# Mock data
MOCK_WORKFLOWS = [
    {"id": "echo", "name": "Echo", "inputs": []}
]
MOCK_SUCCESS_RESP = {
    "request_id": "123",
    "status": "success",
    "result": "Echo: Test"
}
MOCK_ERROR_RESP = {
    "request_id": "123",
    "status": "error",
    "error_message": "Something went wrong"
}

def test_client_discovery():
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = MOCK_WORKFLOWS
        
        client = SpreadsheetClient()
        workflows = client.discover_workflows()
        
        assert len(workflows) == 1
        assert workflows[0]['name'] == "Echo"

def test_client_call_success():
    with patch('requests.post') as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = MOCK_SUCCESS_RESP
        
        client = SpreadsheetClient()
        result = client.call_workflow("Echo", {"text": "Test"})
        
        assert result == "Echo: Test"
        
        # Verify call arguments
        mock_post.assert_called_once()
        args = mock_post.call_args[1]['json']
        assert args['workflow_id'] == 'echo'
        assert args['arguments'] == {"text": "Test"}

def test_client_call_remote_error():
    with patch('requests.post') as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = MOCK_ERROR_RESP
        
        client = SpreadsheetClient()
        result = client.call_workflow("Echo", {"text": "Test"})
        
        assert result == "#LG_ERR: Something went wrong"

def test_client_connection_fail():
    with patch('requests.post') as mock_post:
        mock_post.side_effect = Exception("Connection refused")
        
        client = SpreadsheetClient()
        result = client.call_workflow("Echo", {})
        
        assert result.startswith("#LG_ERR: Connection Failed")
