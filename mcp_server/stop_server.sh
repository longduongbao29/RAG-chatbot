#!/bin/bash

# PID file containing process IDs
PID_FILE="./mcp_servers.pid"

echo "Stopping MCP servers..."

# Check if PID file exists
if [ -f "$PID_FILE" ]; then
    # Read each PID from the file and kill the process
    while IFS= read -r pid; do
        if [ -n "$pid" ]; then
            if kill -0 "$pid" 2>/dev/null; then
                echo "Stopping process with PID: $pid"
                kill "$pid"
                # Wait a moment and force kill if still running
                sleep 1
                if kill -0 "$pid" 2>/dev/null; then
                    echo "Force killing process with PID: $pid"
                    kill -9 "$pid"
                fi
            else
                echo "Process with PID $pid is not running"
            fi
        fi
    done < "$PID_FILE"
    
    # Remove the PID file
    rm -f "$PID_FILE"
    echo "MCP servers stopped and PID file removed."
else
    echo "No PID file found. Attempting to stop processes by name..."
    # Fallback: Kill processes running run_servers.sh
    pkill -f "run_servers.sh"
    echo "Fallback: Stopped processes by name."
fi