# Specification: System Architecture

## Overview
This document defines the high-level architecture for **TabLangGraph**. The system follows a **Client-Server** model where the "LangGraph Bridge" acts as the central server, and both LibreOffice Calc and the Management UI act as clients.

## Components

### 1. LangGraph Bridge (Server)
- **Technology**: Python (FastAPI or similar).
- **Role**: 
  - Hosts the LangGraph Agent/Workflows.
  - Exposes a REST API for execution and discovery.
  - Manages the job queue and execution history.

### 2. Spreadsheet Add-in (Client A)
- **Technology**: LibreOffice Python Scripting (UNO Bridge).
- **Role**: 
  - Defines Custom Functions (UDFs) in Calc (e.g., `LG_RUN`).
  - Serializes cell data.
  - Makes HTTP calls to the Bridge.
  - Deserializes results into cell values.

### 3. Management Widget (Client B)
- **Technology**: TBD (e.g., Streamlit, NiceGUI, or Desktop GUI).
- **Role**: 
  - Polls the Bridge for status and history.
  - Sends control commands (pause/resume/rerun).

## Communication Protocol
- **Transport**: HTTP/1.1 (REST).
- **Format**: JSON.
- **Localhost Only**: For security, binds only to `127.0.0.1`.

## Data Flow
1.  **Discovery**: Add-in requests available functions -> Bridge returns Registry.
2.  **Execution**: User types formula -> Add-in sends generic payload -> Bridge executes -> Returns Result.
3.  **Monitoring**: UI polls `/history` -> Bridge returns logs.
