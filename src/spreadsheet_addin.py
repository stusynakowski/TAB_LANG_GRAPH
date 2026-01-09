import json
import urllib.request
import urllib.error

# Configuration
BRIDGE_URL = "http://127.0.0.1:8000"

def LG_CALL(workflow_name, *args):
    """
    Main entry point for LibreOffice Calc.
    Usage in cell: =LG_CALL("Echo", "Hello World")
    """
    # 1. Construct Payload
    # We assume *args are passed as a list of arguments to the workflow
    # For simplicity in this POC, we map positional args to the workflow's input schema
    # But since we don't know the schema here easily without querying, 
    # let's assume the user passes a single value or we pass them as a list named 'args'
    # Or, we strictly follow the 'Echo' example which takes 'text'.
    
    # improved data mapping strategy needed for generic case, 
    # but for "Echo", args[0] is text.
    
    # We'll try to guess a dictionary if we can, otherwise pass as list?
    # For the "Echo" POC, let's assume the first arg is "text".
    
    payload = {
        "workflow_id": workflow_name.lower(),
        "arguments": {"text": str(args[0])} if args else {},
        "cell_reference": "Unknown" # LO API would provide this if we used the context
    }
    
    try:
        # 2. Prepare Request
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            f"{BRIDGE_URL}/execute", 
            data=data, 
            headers={'Content-Type': 'application/json'}
        )
        
        # 3. Execute
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status == 200:
                resp_body = response.read()
                resp_json = json.loads(resp_body)
                
                if resp_json['status'] == 'success':
                    return resp_json['result']
                else:
                    return f"#LG_ERR: {resp_json.get('error_message')}"
            else:
                return f"#LG_ERR: HTTP {response.status}"
                
    except urllib.error.URLError as e:
        return f"#LG_ERR: Connection Refused - Is Bridge Running?"
    except Exception as e:
        return f"#LG_ERR: {str(e)}"

# LibreOffice script registration mechanism would go here
# g_exportedScripts = (LG_CALL,)
