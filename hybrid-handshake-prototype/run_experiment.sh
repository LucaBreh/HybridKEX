#!/bin/bash

echo "[*] start server..."
python3 server.py &
SERVER_PID=$!

# wait for server to be ready
sleep 1

echo "[*] start client..."
python3 client.py

# wait for client to be ready
wait $SERVER_PID

echo "[✓] experiment finished."
