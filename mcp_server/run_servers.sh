#!/bin/bash

# PID file to store process IDs
PID_FILE="./mcp_servers.pid"

# Remove old PID file if exists
rm -f "$PID_FILE"

echo "Starting MCP servers..."

# Run all Python servers in background and save PIDs
for server in ./mcp_server/servers/*.py; do
    if [ -f "$server" ]; then
        echo "Starting $(basename "$server")..."
        python3 "$server" &
        PID=$!
        echo "$PID" >> "$PID_FILE"
        echo "Started $(basename "$server") with PID: $PID"
    fi
done

echo "All MCP servers started. PIDs saved to $PID_FILE"