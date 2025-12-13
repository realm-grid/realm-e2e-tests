#!/bin/bash
# Start Azure Functions server for E2E tests
# This script starts the server and keeps it running

set -e

cd /home/falk/realm-grid/realm-functions

# Kill any existing func processes
pkill -f "func start" 2>/dev/null || true
sleep 2

# Check if port is free
if ss -tlnp | grep -q ":7071"; then
    echo "Port 7071 is in use, killing process..."
    fuser -k 7071/tcp 2>/dev/null || true
    sleep 2
fi

# Activate virtual environment and start
source .venv/bin/activate

echo "Starting Azure Functions server on port 7071..."
func start
