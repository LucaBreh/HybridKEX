#!/bin/bash
echo "Restarting experiment..."

docker-compose stop client

docker-compose up -d --no-build client