# Specification: LangGraph Service Bridge (Backend)

## Overview
The backend service responsible for loading user-defined LangGraph workflows and executing them upon request.

## Core Responsibilities

### 1. Workflow Registry
- **Loading**: On startup, scan a specific directory (`src/workflows`) for python files defining LangGraph nodes/graphs.
- **Support for Simple Functions**: The registry must support registering:
    - Complex `StateGraph` objects (LangGraph).
    - Simple Python functions (Tools).
    - **Built-in Generic Workflows**: The system should initialize with default workflows for immediate utility:
        - `lg_prompt(instruction, context)`: A direct call to a configured LLM.
        - `lg_map(instruction, list_data)`: Apply an LLM instruction to a list.
- **Validation**: Ensure loaded workflows match the expected interface (inputs/outputs).
- **Hot Reloading**: (Optional) Detect changes in workflow files and reload definitions.

### 2. API Endpoints
- `GET /health`: System check.
- `GET /workflows`: List available registered workflows.
- `POST /execute`: specific workflow execution.
- `GET /history`: Retrieve execution logs.
- `POST /control`: Set system state (pause/resume).

### 3. Execution Engine
- **Concurrency**: Handle multiple requests using `asyncio`.
- **Queuing**: If the "Pause" state is active, requests are held in an in-memory queue.
- **Model Abstraction Layer**: 
    - Use **LiteLLM** or **LangChain** to normalize interactions across different providers (OpenAI, Anthropic, Ollama).
    - This allows users to simply change `DEFAULT_LLM_MODEL` config without rewriting workflow code.
- **LLM Context**: Manage API keys and model initialization locally.

### 4. Logging
- Persist execution history to a local SQLite database or JSON lines file for the UI to read.
