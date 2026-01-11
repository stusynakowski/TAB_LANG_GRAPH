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
    # 0. Check for TIMEOUT and SAVE overloads
    timeout = 5
    save_to_file = False
    clean_args = []
    if args:
        for arg in args:
            if isinstance(arg, str):
                if arg.startswith("TIMEOUT="):
                    try:
                        timeout = int(arg.split("=")[1])
                    except ValueError:
                        pass # Ignore invalid timeout format
                elif arg.replace(" ", "").upper() == "SAVE=TRUE":
                    save_to_file = True
                else:
                    clean_args.append(arg)
            else:
                clean_args.append(arg)

    # 1. Construct Payload
    payload = {
        "workflow_id": workflow_name.lower(),
        "positional_args": clean_args,
        "arguments": {},
        "cell_reference": "Unknown" 
    }
    
    try:
        # Debug logging to /tmp
        with open("/tmp/FancySheetFunctions_debug.log", "a", encoding="utf-8", errors="replace") as f:
             safe_args = str(clean_args)
             timeout_info = f"[Timeout: {timeout}s] [Save: {save_to_file}]"
             f.write(f"Calling {workflow_name} with {safe_args} {timeout_info}\n")

        # 2. Prepare Request
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            f"{BRIDGE_URL}/execute", 
            data=data, 
            headers={'Content-Type': 'application/json'}
        )
        
        # 3. Execute
        with urllib.request.urlopen(req, timeout=timeout) as response:
            if response.status == 200:
                resp_body = response.read()
                resp_json = json.loads(resp_body)
                
                if resp_json['status'] == 'success':
                    result = resp_json['result']
                    
                    if save_to_file:
                        try:
                            saved_path = _save_result_locally(workflow_name, result)
                            return f"Saved: {saved_path}"
                        except Exception as e:
                            return f"#FSF_SAVE_ERR: {str(e)}"
                            
                    return result
                else:
                    return f"#LG_ERR: {resp_json.get('error_message')}"
            else:
                return f"#LG_ERR: HTTP {response.status}"
    
    except urllib.error.URLError as e:
        if isinstance(e.reason, TimeoutError) or "timed out" in str(e).lower():
            return f"#LG_TIMEOUT: Exceeded {timeout}s. Try adding 'TIMEOUT=60' to args."
        return f"#LG_ERR: Connection Refused - {e.reason}"
    except Exception as e:
        if "timed out" in str(e).lower():
            return f"#LG_TIMEOUT: Exceeded {timeout}s. Try adding 'TIMEOUT=60' to args."
        return f"#LG_ERR: Unexpected - {str(e)}"

def _save_result_locally(name, data):
    """
    Saves data to a folder next to the current spreadsheet.
    """
    import os
    import datetime
    import uno
    
    try:
        doc = XSCRIPTCONTEXT.getDocument()
        url = doc.getURL()
        if not url:
            raise Exception("Spreadsheet must be saved first")
            
        # Convert file:/// path to system path
        doc_path = uno.fileUrlToSystemPath(url)
        base_dir = os.path.dirname(doc_path)
        
        # Create output directory
        out_dir = os.path.join(base_dir, "fancy_sheet_functions_temp_storage")
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
            
        # Generate filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        fname = f"{name}_{timestamp}.json"
        full_path = os.path.join(out_dir, fname)
        
        with open(full_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        return fname
    except NameError:
        raise Exception("Cannot access spreadsheet context (Are you running in LO?)")

# LibreOffice script registration mechanism
g_exportedScripts = (FSF, TestBackendConnection)
