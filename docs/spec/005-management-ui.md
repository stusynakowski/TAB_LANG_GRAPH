# Specification: Management Widget UI

## Overview
A standalone dashboard to control and monitor the connection.

## Tech Stack Recommendation
- **Framework**: Streamlit (fastest iteration) or NiceGUI (better event loop integration).
- **Deployment**: Runs as a separate process from the backend, or served by the backend.

## UI Components

### 1. Sidebar / Header
- **Status Indicator**: Green (Connected) / Red (Disconnected).
- **Master Switch**: Toggle "Pause Execution" / "Resume Execution".

### 2. Main Area - Activity Log
- Table view of recent calls.
- Columns: Timestamp, Workflow Name, Cell, Status, Duration.
- Actions: "Rerun" button next to each row.

### 3. Configuration Tab
- View loaded workflows.
- View/Set Environment Variables (API Keys).
- Clear History button.

## Interaction
- The UI communicates with the Bridge via the same REST API as the Spreadsheet, utilizing `/history` and `/control` endpoints.
