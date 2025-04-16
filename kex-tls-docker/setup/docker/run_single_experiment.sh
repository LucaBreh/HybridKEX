#!/usr/bin/env bash

set -e
set -x

source ../shared/read_config.sh
export COMPOSE_FILE=../docker-compose.yml


echo "🚀 Building Docker images..."
docker compose -f "$COMPOSE_FILE" build


echo "🟢 Starting server and client..."
docker compose -f "$COMPOSE_FILE" up -d server client


echo "⏱ Waiting for client to finish ${RUNS} runs..."
docker wait client


echo "📦 Logs wurden direkt nach $HOST_DIR geschrieben."


#echo "🧼 Stopping and cleaning up..."
#docker compose down
