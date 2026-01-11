#!/bin/bash

# Define colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}Starting TabLangGraph Environment...${NC}"

# Function to kill process on a port
kill_port() {
    PORT=$1
    # Find PID listening on the port
    PID=$(lsof -t -i:$PORT)
    if [ -n "$PID" ]; then
        echo -e "${RED}Port $PORT is already in use by PID $PID. Killing it...${NC}"
        kill -9 $PID 2>/dev/null
    fi
}

# Clean up ports 8000 (FastAPI) and 8501 (Streamlit)
kill_port 8000
kill_port 8501

# Function to handle cleanup
cleanup() {
    echo -e "\n${BLUE}Shutting down services...${NC}"
    if [ -n "$SERVER_PID" ]; then
        kill $SERVER_PID 2>/dev/null
    fi
    exit
}

# Trap INT signal (Ctrl+C)
trap cleanup INT

# Start FastAPI server in background
echo -e "${GREEN}Starting FastAPI Server on port 8000...${NC}"
echo -e "${BLUE}(Logs are being redirected to backend.log to keep terminal clean)${NC}"

# Ensure src is in python path to find the module if not installed in editable mode
export PYTHONPATH=$PYTHONPATH:$(pwd)/src

if command -v uv &> /dev/null && [ -f "uv.lock" ]; then
    echo "Detected uv project, using uv run..."
    uv run uvicorn tab_lang_graph.server:app --reload --port 8000 > backend.log 2>&1 &
else
    uvicorn tab_lang_graph.server:app --reload --port 8000 > backend.log 2>&1 &
fi
SERVER_PID=$!

# Wait for server to initialize
echo "Waiting for server to start..."
sleep 3

# Check if server process is still alive
if ! ps -p $SERVER_PID > /dev/null; then
    echo -e "${RED}Error: Backend server failed to start.${NC}"
    echo "Checking backend.log:"
    tail -n 10 backend.log
    exit 1
fi

# Start Streamlit application
echo -e "${GREEN}Starting Streamlit UI on port 8501...${NC}"
if command -v uv &> /dev/null && [ -f "uv.lock" ]; then
    uv run streamlit run src/management_ui.py --server.port 8501
else
    streamlit run src/management_ui.py --server.port 8501
fi

# Cleanup after Streamlit exits
cleanup
