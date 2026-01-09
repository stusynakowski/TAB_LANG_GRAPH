# Spec Overview

## Scope
This project, **TabLangGraph**, serves as an integration layer that empowers spreadsheet (LibreOffice Calc) users to execute sophisticated LangGraph workflows directly from cell formulas.

The system consists of two primary components:
1.  **Spreadsheet Add-in/Interface**: A client-side component within LibreOffice Calc that exposes custom functions.
2.  **LangGraph Service Bridge**: A backend service that registers local LangGraph workflows and exposes them as callable endpoints for the spreadsheet.

**In Scope:**
*   Mechanism to "discover" LangGraph workflows and register them as spreadsheet functions.
*   **Built-in Standard Library**: A set of generic functions (e.g., `LG_PROMPT`) for ad-hoc LLM calls without requiring new code definitions.
*   Execution of workflows passing cell data as arguments.
*   Returning workflow results back to the spreadsheet cell.
*   A standalone **Management Widget UI** to oversee the bridge, manage configurations, and control execution flow.

**Out of Scope:**
*   Re-implementing spreadsheet calculation engines.
*   Cloud hosting infrastructure (assumed local/self-hosted for this phase).

## Requirements

### Core Functionality
- **REQ-CORE-001 (Function Discovery)**: The system must dynamically identify available LangGraph workflows and expose them as callable functions in LibreOffice Calc (e.g., `=LG_SUMMARIZE(A1)`).
- **REQ-CORE-002 (Bidirectional Execution)**: When a spreadsheet function is calculated:
    1.  Arguments must be serialized and sent to the LangGraph instance.
    2.  The specific LangGraph workflow must execute.
    3.  The result must be returned and rendered in the originating cell.
- **REQ-CORE-003 (Asynchronous Handling)**: The system must handle long-running LLM tasks without freezing the entire spreadsheet UI completely, or provide feedback that calculation is in progress.
- **REQ-CORE-004 (Built-in Primitive)**: The system must provide a default `LG_PROMPT` (or similar) function that allows users to pass a raw string instruction and input data directly from the spreadsheet, executing a simple LLM call without needing a pre-defined backend workflow file.

### Management Widget UI
- **REQ-UI-001 (Bridge Overview)**: A dedicated GUI widget must provide a real-time view of the connection status between the spreadsheet and the LangGraph backend.
- **REQ-UI-002 (Resource Visibility)**: The widget must list:
    - Currently loaded LLM models.
    - Available LangGraph functions (tools/agents) exposed to the spreadsheet.
- **REQ-UI-003 (Execution History)**: A log view must display past executions, including:
    - Timestamp, calling cell, function name, inputs, status (success/fail), and duration.
- **REQ-UI-004 (Execution Control)**: Users must be able to:
    - **Pause/Resume** the bridge (queuing or ignoring requests while paused).
    - **Manually Rerun** specific past executions from the history log.
- **REQ-UI-005 (Trigger Configuration)**: Users can configure execution policies per function or globally:
    - **Auto-run**: Execute immediately when cell data changes (reactive).
    - **Manual**: Require explicit approval or a "Run" button press in the widget before processing pending spreadsheet requests.

### Error Handling
- **REQ-ERR-001 (Graceful Failure)**: If the backend is unreachable or the LLM fails, the spreadsheet cell should display a meaningful error message (e.g., `#LG_ERROR!`) rather than crashing the application.

## Interfaces

### User Interface (Spreadsheet)
- **Input**: Custom Formula syntax, e.g., `=AGENT_RUN("workflow_name", input_cell)`.
- **Output**: Textual or numeric result from the Agent workflow displayed in the cell.

### System Interface (Bridge)
- **Communication Protocol**: (TBD, e.g., REST, gRPC, or COM/UNO interface) to pass data between the Spreadsheet process and the Python/LangGraph process.
- **Serialization**: JSON or string-based payload structure for function arguments.

## Edge cases
- **EDGE-001**: User attempts to call a function for a LangGraph workflow that has been deleted or renamed.
- **EDGE-002**: Input cell contains data types incompatible with the LangGraph expectation (e.g., image data vs text).
- **EDGE-003**: Circular dependencies where the Agent creates a value that triggers another Agent call.

## Acceptance criteria
- **AC-001**: A user can define a simple LangGraph node (e.g., "Process Text"), see it appear in the Dashboard, and call it successfully from a LibreOffice cell.
- **AC-002**: Updates to the input cell trigger a re-run of the LangGraph workflow and update the output cell.
- **AC-003**: The user can pause the bridge via the Management UI, make multiple edits in the spreadsheet without triggering runs, and then resume to process the queue.
- **AC-004**: A user can view the history of a specific function call in the widget and click "Rerun" to re-execute it. 