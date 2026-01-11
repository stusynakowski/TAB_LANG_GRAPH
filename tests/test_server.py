import pytest
from fastapi.testclient import TestClient
from fancy_sheet_functions.server import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_list_workflows():
    response = client.get("/workflows")
    assert response.status_code == 200
    workflows = response.json()
    assert isinstance(workflows, list)
    # Check for the default Echo workflow
    assert any(w['name'] == "Echo" for w in workflows)

def test_execute_endpoint():
    # 1. Get workflow list to find Echo
    workflows = client.get("/workflows").json()
    echo_workflow = next(w for w in workflows if w['name'] == "Echo")
    
    payload = {
        "workflow_id": echo_workflow['id'],
        "arguments": {"text": "Integration Test"}
    }
    
    response = client.post("/execute", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == "success"
    assert data['result'] == "Echo: Integration Test"

def test_control_endpoints():
    # Pause
    client.post("/control?action=pause")
    
    # Check Status
    status_resp = client.get("/status")
    assert status_resp.json()['status'] == "paused"
    
    # Try Execute
    payload = {
        "workflow_id": "echo", # Assumes 'echo' is the ID
        "arguments": {"text": "Should Pending"}
    }
    response = client.post("/execute", json=payload)
    assert response.json()['status'] == "pending"
    
    # Resume
    client.post("/control?action=resume")
    
    # Check Status
    status_resp = client.get("/status")
    assert status_resp.json()['status'] == "active"

def test_history_endpoint():
    # Execute a few requests
    client.post("/execute", json={"workflow_id": "echo", "arguments": {"text": "A"}})
    client.post("/execute", json={"workflow_id": "echo", "arguments": {"text": "B"}})
    
    response = client.get("/history")
    assert response.status_code == 200
    history = response.json()
    assert len(history) >= 2
    assert history[-1]['result'] == "Echo: B"
