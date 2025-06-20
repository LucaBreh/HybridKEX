#!/bin/bash

CONFIG_PATH="./shared/config.json"
MODES=("classic" "pqc" "hybrid")

for mode in "${MODES[@]}"
do
    echo "[*] Updating config to mode: $mode"
    jq --arg mode "$mode" '.mode.selected = $mode' "$CONFIG_PATH" > tmp_config.json && mv tmp_config.json "$CONFIG_PATH"

    echo "[*] Starting server for mode: $mode..."
    python3 server.py &
    SERVER_PID=$!

    sleep 1

    echo "[*] Starting client for mode: $mode..."
    python3 client.py

    wait $SERVER_PID

    echo "[✓] Mode '$mode' finished."
    echo ""
done

echo "[✓✓] All experiments finished."
