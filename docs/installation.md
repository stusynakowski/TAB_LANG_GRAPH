# Installation Guide

This guide covers the installation steps for both the Backend Services (Server & UI) and the LibreOffice Spreadsheet Add-in.

## Prerequisites

*   **Python**: Version 3.10 or higher.
*   **LibreOffice**: Version 7.0 or higher (Calc).
*   **Git**: To clone the repository.

---

## Part 1: Server and Management UI Setup

This component runs the local bridge that connects your spreadsheet to Python/LangGraph workflows.

### 1. Clone the Repository
```bash
git clone https://github.com/stusynakowski/TAB_LANG_GRAPH.git
cd TAB_LANG_GRAPH
```

### 2. Set up Python Environment
It is recommended to use a virtual environment.

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```powershell
python -m venv venv
.\venv\Scripts\activate
```

### 3. Install Dependencies
Install the package in editable mode along with all required libraries:

```bash
pip install -e ".[dev]"
```
*Note: This installs FastAPI, Uvicorn, Streamlit, and other core libraries.*

### Alternative: Install using uv

If you prefer using [uv](https://github.com/astral-sh/uv) for faster installations:

```bash
# Create venv and install dependencies
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

### 4. Configuration
Create a `.env` file in the root directory to store your configuration and API keys.

```bash
cp .env.example .env  # If example exists, otherwise create new
```

**Minimal `.env` content:**
```ini
LG_HOST=127.0.0.1
LG_PORT=8000
# Add your LLM keys here if using built-in models
# OPENAI_API_KEY=sk-...
```

### 5. Verify Installation
Run the test suite to ensure the environment is correctly set up.

```bash
pytest
```

---

## Part 2: LibreOffice Add-in Setup

This step involves placing the Python script where LibreOffice can find it.

### 1. Locate the LibreOffice Scripts Folder
The location varies by operating system. You may need to create the folders `Scripts/python` if they don't exist.

*   **macOS**: `~/Library/Application Support/LibreOffice/4/user/Scripts/python/`
*   **Linux**: `~/.config/libreoffice/4/user/Scripts/python/`
*   **Windows**: `%APPDATA%\LibreOffice\4\user\Scripts\python\`

### 2. Install the Script
You can either **copy** the script or **symlink** it (recommended for developers so updates apply immediately).

**Option A: Symlink (macOS/Linux Recommended)**
Replace `/path/to/repo` with your actual path.
```bash
# Create directory structure if needed
mkdir -p ~/Library/Application\ Support/LibreOffice/4/user/Scripts/python/

# Create Symlink
ln -s "$(pwd)/src/spreadsheet_addin.py" ~/Library/Application\ Support/LibreOffice/4/user/Scripts/python/lg_bridge.py
```

**Option B: Copy (Windows/Simple)**
Copy the file `src/spreadsheet_addin.py` to the folder identified in Step 1.

### 3. Verify in LibreOffice
1.  Open LibreOffice Calc.
2.  Go to **Tools** > **Macros** > **Run Macro...**
3.  Navigate to **My Macros** > **lg_bridge** (or the name of the file you copied).
4.  You should see the function `LG_CALL`.

---

## Part 3: Running the System

To use the system, the specific servers must be running.

### 1. Start the Bridge Server
Open a terminal in your project root (with venv activated):
```bash
uvicorn tab_lang_graph.server:app --reload
```
*   Server will run at `http://127.0.0.1:8000`.

### 2. Start the Management UI (Optional)
Open a new terminal tab (with venv activated):
```bash
streamlit run src/management_ui.py
```
*   UI will open in your browser (usually `http://localhost:8501`).

### 3. Use in Spreadsheet
In any cell in LibreOffice Calc, use the formula:
```excel
=LG_CALL("Echo", "Hello World")
```
If successful, the cell should update with `Echo: Hello World`.
