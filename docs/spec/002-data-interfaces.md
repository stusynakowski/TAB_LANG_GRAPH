# Specification: Data Interfaces & Schemas

## Overview
Defines the data structures used for communication between the Spreadsheet, the Bridge, and the UI.

## Models

### 1. Workflow Definition (Discovery)
Structure returned when the client asks "what functions are available?"
```json
{
  "id": "workflow_unique_id",
  "name": "Summarize Text",
  "description": "Uses LLM to summarize input text.",
  "inputs": [
    {"name": "text", "type": "string"}
  ]
}
```

### 2. Execution Request
Payload sent from Spreadsheet to Bridge.
```json
{
  "workflow_id": "summarize_text",
  "arguments": {
    "text": "Content of cell A1..."
  },
  "cell_reference": "Sheet1!B2",
  "request_id": "uuid"
}
```

### 3. Execution Response
Immediate response or polling result.
```json
{
  "request_id": "uuid",
  "status": "success|error|pending",
  "result": "The summarized text...",
  "error_message": null,
  "execution_time_ms": 1500
}
```

### 4. Bridge Status (Heartbeat)
```json
{
  "status": "active|paused",
  "active_models": ["gpt-4", "local-llama"],
  "queue_size": 0
}
```
