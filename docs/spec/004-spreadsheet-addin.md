# Specification: Spreadsheet Add-in (LibreOffice)

## Overview
The client-side integration running inside LibreOffice Calc.

## Implementation Details

### 1. Function Registration
- Use the **LibreOffice Python Scripting Provider**.
- Expose a main entry point function `LG_CALL(workflow_name, *args)`.
- Optionally expose dynamic functions mapping 1:1 to workflows if technically feasible in LO.

### 2. The `LG_CALL` Function
- **Signature**: `LG_CALL(workflow_id, arg1, arg2, ...)`
- **Behavior**:
    1. Check if Bridge is reachable.
    2. Construct JSON payload.
    3. Send HTTP POST to `http://localhost:8000/execute`.
    4. Block and wait for response (with timeout) OR handle async result (if supported by LO Calc async functions).
    5. Return `result` or `#LG_ERR: <message>`.

### 3. Configuration
- Store the Bridge URL (default `http://localhost:8000`) in a config file or LO registry.

### 4. Error Handling
- Timeout handling (don't hang the UI forever).
- Connection refused handling (Guidance to start the bridge).

## Installation / Deployment Strategy

### Challenge
LibreOffice requires Python macros to be located in specific platform-dependent directories:
- **macOS**: `~/Library/Application Support/LibreOffice/4/user/Scripts/python/`
- **Linux**: `~/.config/libreoffice/4/user/Scripts/python/`
- **Windows**: `%APPDATA%\LibreOffice\4\user\Scripts\python\`

### Solution: `scripts/install.py`
We need a setup utility that:
1.  Identifies the user's OS and LibreOffice Scripts folder.
2.  Creates the `Scripts/python` folders if they don't exist.
3.  **Symlinks** (or copies) the local `src/spreadsheet_addin.py` to the LibreOffice folder.
    - *Why Symlink?* Allows the user to update the git repo and have the changes reflect immediately in LO without re-installing.
4.  Generates a `config.json` next to the script if hardcoded paths are needed (e.g., path to the python venv).
