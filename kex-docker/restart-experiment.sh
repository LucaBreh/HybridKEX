#!/bin/bash
echo "Reloading config.json and starting experiment..."

docker-compose stop client

docker-compose up -d --no-build client