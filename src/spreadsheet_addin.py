import json
import urllib.request
import urllib.error

# Configuration
BRIDGE_URL = "http://127.0.0.1:8000"

def _msgbox(message):
    """
    Display a message box in LibreOffice. 
    Useful because print() output is not visible in the standard GUI.
    """
    try:
        # XSCRIPTCONTEXT is injected by LibreOffice automatically
        ctx = XSCRIPTCONTEXT.getComponentContext()
        sm = ctx.ServiceManager
        toolkit = sm.createInstanceWithContext("com.sun.star.awt.Toolkit", ctx)
        parent = toolkit.getDesktopWindow()
        
        # createMessageBox params: Parent, Type, Buttons, Title, Message
        # Type: infobox=1
        # Buttons: 1 (OK)
        box = toolkit.createMessageBox(parent, "infobox", 1, "FancySheetFunctions", str(message))
        box.execute()
    except NameError:
        # Fallback for testing outside LibreOffice
        print(f"DEBUG (MsgBox): {message}")
    except Exception as e:
        print(f"Failed to show MsgBox: {e}")

def TestBackendConnection(*args):
    """
    A Macro you can run via 'Tools > Macros > Run Macro'.
    This helps verify that:
    1. Python execution is working in LibreOffice.
    2. Connection to the backend server is working.
    """
    result = FSF("Echo", "Ping from Macro")
    _msgbox(f"Backend Response:\n{result}")

def FSF(workflow_name, *args):
    """
    Main entry point for LibreOffice Calc.
    Usage in cell: =FSF("Echo", "Hello World")
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
        "positional_args": list(args) if args else [],
        "arguments": {},
        "cell_reference": "Unknown" # LO API would provide this if we used the context
    }
    
    try:
        # Debug logging to /tmp
        with open("/tmp/FancySheetFunctions_debug.log", "a") as f:
             f.write(f"Calling {workflow_name} with {args}\n")

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
        return f"#LG_ERR: Connection Refused - {e.reason}"
    except Exception as e:
        return f"#LG_ERR: Unexpected - {str(e)}"

# LibreOffice script registration mechanism
g_exportedScripts = (FSF, TestBackendConnection)
