#!/bin/bash

echo "================================="
echo " Hand Gesture Analytics Dashboard"
echo "================================="
echo ""

cleanup() {
    echo ""
    echo "Shutting down..."
    kill $PYTHON_PID 2>/dev/null
    kill $REACT_PID 2>/dev/null
    exit 0
}
trap cleanup SIGINT SIGTERM

echo "[1/2] Starting Python gesture detection..."
/home/rei/miniconda3/envs/hand-gesture/bin/python python/main.py &
PYTHON_PID=$!

echo "[2/2] Starting React dashboard..."
cd web && npm run dev &
REACT_PID=$!

echo ""
echo "Python PID: $PYTHON_PID"
echo "React PID:  $REACT_PID"
echo ""
echo "Press Ctrl+C to stop both services."
echo ""

wait
