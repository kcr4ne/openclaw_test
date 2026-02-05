#!/bin/bash

# Ensure Root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root (sudo)."
  exit
fi

echo "[JARVIS] Starting System Core (Background)..."
# Run Python backend effectively disowned
nohup ./venv/bin/python main.py > backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

echo "[JARVIS] Starting Interface (Background)..."
cd interface
# Run Next.js effectively disowned
nohup npm run dev > frontend.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"

echo "[JARVIS] All Systems Online."
echo "Logs are being written to backend.log and interface/frontend.log"
echo "Opening Dashboard..."
sleep 3
xdg-open http://localhost:3000 2>/dev/null || echo "Open http://localhost:3000 in your browser."

echo "Press any key to exit setup (Processes will keep running)..."
read -n 1
