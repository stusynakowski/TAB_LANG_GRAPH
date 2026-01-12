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
    Simple fast python execution.
    Usage in cell: =FSF("Echo", "Hello")
    """
    payload = {
        "workflow_id": workflow_name.lower(),
        "positional_args": args
    }
    
    try:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            f"{BRIDGE_URL}/execute", 
            data=data, 
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                resp_body = response.read()
                resp_json = json.loads(resp_body)
                
                if resp_json.get('status') == 'success':
                    return resp_json.get('result')
                else:
                    return f"Error: {resp_json.get('error_message')}"
            else:
                return f"Error: HTTP {response.status}"
                
    except Exception as e:
        return f"Error: {str(e)}"

# LibreOffice script registration mechanism
g_exportedScripts = (FSF, TestBackendConnection)
