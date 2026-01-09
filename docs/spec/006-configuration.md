# Specification: Configuration & Security

## Overview
This document defines how **TabLangGraph** handles application settings, secrets (API Keys), and model configurations.

## Critical Decisions
1.  **Storage**: Configuration is stored in a `.env` file in the project root. This ensures compatibility with standard Python tooling and keeps secrets out of source control.
2.  **Management**: Users can modify the `.env` file manually OR use the **Management UI** "Settings" tab to update values safely.

## Configuration Schema

### 1. Core Settings
| Key | Default | Description |
| :--- | :--- | :--- |
| `LG_HOST` | `127.0.0.1` | IP to bind the Bridge server to. |
| `LG_PORT` | `8000` | Port for the Bridge and UI. |
| `LG_WORKFLOW_DIR` | `./src/workflows` | Directory to scan for user graph definitions. |

### 2. Model Provider Secrets
Typical keys required for the "Standard Library" (`LG_PROMPT`) and custom agents to function.
| Key | Description |
| :--- | :--- |
| `OPENAI_API_KEY` | For GPT-4, GPT-3.5 models. |
| `ANTHROPIC_API_KEY` | For Claude models. |
| `OLLAMA_BASE_URL` | For local LLMs (default `http://localhost:11434`). |

### 3. Default Model Configuration
Defines which model is used when a generic `LG_PROMPT` call is made without specifying a model.
| Key | Default |
| :--- | :--- |
| `DEFAULT_LLM_PROVIDER` | `openai` |
| `DEFAULT_LLM_MODEL` | `gpt-4o` |

## Security Considerations
- **Local Binding**: The server binds to `127.0.0.1` by default to prevent exposure to the local network.
- **No Authorship**: The system assumes the user *is* the admin. There is no password login for the Management UI (Local Single-User assumption).
