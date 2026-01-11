import json
from typing import Any, Dict
import requests # Simulate calls
# In reality, this would use urllib or similar in standard python environment of LibreOffice
# For testing we can use requests

class SpreadsheetClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url

    def discover_workflows(self):
        try:
            resp = requests.get(f"{self.base_url}/workflows")
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            return []

    def call_workflow(self, workflow_name: str, args: Dict[str, Any], cell_ref: str = None) -> Any:
        # 1. Serialize
        # Since workflow_name usually needs to map to IDs, let's assume simple mapping for now:
        workflow_id = workflow_name.lower()
        
        payload = {
            "workflow_id": workflow_id,
            "arguments": args,
            "cell_reference": cell_ref
        }
        
        try:
            # 2. Call Bridge
            resp = requests.post(f"{self.base_url}/execute", json=payload)
            resp.raise_for_status()
            data = resp.json()
            
            # 3. Handle Result
            if data['status'] == 'success':
                return data['result']
            else:
                return f"#LG_ERR: {data.get('error_message', 'Unknown Error')}"
                
        except Exception as e:
            return f"#LG_ERR: Connection Failed - {str(e)}"
