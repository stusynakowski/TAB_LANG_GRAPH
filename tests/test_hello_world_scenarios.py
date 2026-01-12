import pytest
from unittest.mock import patch, MagicMock
import json
import sys
import os

# Add src to path to import modules correctly
sys.path.append(os.path.abspath("src"))

from spreadsheet_addin import FSF

from fancy_sheet_functions.server import app
from fastapi.testclient import TestClient

client = TestClient(app)

# -------------------------------------------------------------------------
# Test 1: LibreOffice Macro Execution (Client Side)
# -------------------------------------------------------------------------
def test_macro_execution_client_side():
    """
    Simulates executing the macro from LibreOffice.
    This ensures that the python script running inside LibreOffice can take arguments,
    format them into a request, and handle a successful response.
    """
    # Hypothetical response from the server
    mock_resp_json = {
        "status": "success",
        "result": "Echo: Hello World"
    }
    
    # Mock the network call so we don't need a real server running for this unit test
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.read.return_value = json.dumps(mock_resp_json).encode('utf-8')
    mock_response.__enter__.return_value = mock_response
    mock_response.__exit__.return_value = None
    
    with patch('urllib.request.urlopen', return_value=mock_response) as mock_urlopen:
        # Simulate user typing in cell: =FSF("Echo", "Hello World")
        result = FSF("Echo", "Hello World")
        
        # Verify the macro returned the pure result string to the cell
        assert result == "Echo: Hello World"
        
        # Verify the payload was constructed correctly
        args, _ = mock_urlopen.call_args
        request_sent = args[0]
        payload_sent = json.loads(request_sent.data)
        
        assert payload_sent["workflow_id"] == "echo"
        assert payload_sent["positional_args"] == ["Hello World"]

# -------------------------------------------------------------------------
# Test 2: Ping Message & Streamlit Visibility (Server Integration)
# -------------------------------------------------------------------------
def test_ping_message_and_streamlit_visibility():
    """
    Tests that a request ("ping") sent to the server is processed and, 
    crucially, recorded in the history so it can be seen in the Streamlit UI.
    """
    # 1. Send the "Ping" (Execution Request) to the server directly
    payload = {
        "workflow_id": "echo",
        "arguments": {"text": "Ping Streamlit"}
    }
    
    response = client.post("/execute", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["result"] == "Echo: Ping Streamlit"
    
    # 2. Check History (This is what the Streamlit UI queries)
    history_response = client.get("/history")
    assert history_response.status_code == 200
    history = history_response.json()
    
    # Verify our ping is in the history
    assert len(history) > 0, "History should not be empty after execution"
    
    # Find our specific request in history (it should be the last one)
    latest_entry = history[-1]
    
    # Verify output result matches
    assert latest_entry["result"] == "Echo: Ping Streamlit"

# -------------------------------------------------------------------------
# Test 3: Full Round Trip Response (End-to-End Logic)
# -------------------------------------------------------------------------
def test_full_round_trip_response():
    """
    Validates the full cycle: Macro -> JSON Payload -> Server Response -> Macro Return.
    This ensures that when the server replies, the macro correctly parses the 
    response and hands it back to the spreadsheet, including error handling.
    """
    # A. Successful Case
    # Define the exact server response structure we expect
    server_response_body = {
        "request_id": "test-uuid-123",
        "status": "success",
        "input": {"workflow_id": "echo", "arguments": {"text": "RoundTrip"}},
        "result": "Echo: RoundTrip",
        "error_message": None
    }
    
    mock_network_response = MagicMock()
    mock_network_response.status = 200
    mock_network_response.read.return_value = json.dumps(server_response_body).encode('utf-8')
    mock_network_response.__enter__.return_value = mock_network_response
    mock_network_response.__exit__.return_value = None
    
    with patch('urllib.request.urlopen', return_value=mock_network_response):
        # User types: =FSF("Echo", "RoundTrip")
        cell_output = FSF("Echo", "RoundTrip")
        
        # Verify exactly what is put back into the cell
        assert cell_output == "Echo: RoundTrip"
        
    # B. Error Case (Server sends application error)
    error_response_body = {
        "request_id": "test-err-456",
        "status": "error", 
        "result": None,
        "error_message": "Something went wrong"
    }
    mock_network_response.read.return_value = json.dumps(error_response_body).encode('utf-8')
    
    with patch('urllib.request.urlopen', return_value=mock_network_response):
        error_output = FSF("Echo", "ErrorCase")
        # Verify the spreadsheet gets a proper error string
        assert error_output == "#LG_ERR: Something went wrong"
