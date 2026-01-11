# Development Tips & Workflow

## Dependency Management with `uv`

We use `uv` for fast Python package management and virtual environment handling.

### Adding a New Package
To add a new library (e.g., `langchain`) to the project:
1. Run the add command:
   ```bash
   uv add langchain
   ```
   This automatically updates `pyproject.toml` and adds the specific versions to `uv.lock`.

2. The next time you run `uv run` or start the server, `uv` will automatically sync the environment.

### Removing a Package
```bash
uv remove package-name
```

## Server Workflow

### When Modifying Code (`.py` files)
- **FastAPI Backend**: The server is configured with auto-reload. When you save a change to a Python file, `uvicorn` detects it and reloads automatically. **No restart required.**
- **Streamlit UI**: Streamlit detects file changes and prompts you to "Rerun" (top-right of the browser) or will auto-rerun if configured.

### When Adding Packages
- If you install a new package while the server is running, the running process won't see it immediately.
- **Action Required**: Stop the server (Ctrl+C) and restart it (e.g., `./start.sh`) to load the new environment.

## Quick Summary
1. **Code Change** → Just Save (Auto-reload handles it).
2. **Package Add** → `uv add <pkg>` → **Restart Server**.
