#!/bin/bash

CONFIG_PATH="./shared/config.json"
MODES=("classic" "hybrid" "pqc")

for mode in "${MODES[@]}"
do
    echo "Setting mode to: $mode"

    jq --arg mode "$mode" '.mode.selected = $mode' "$CONFIG_PATH" > tmp_config.json && mv tmp_config.json "$CONFIG_PATH"


    ./restart-experiment.sh

    while [ "$(docker inspect -f '{{.State.Running}}' kex-client)" == "true" ]; do
        echo "Waiting for client to finish..."
        sleep 20
    done

done

echo "All modes finished."