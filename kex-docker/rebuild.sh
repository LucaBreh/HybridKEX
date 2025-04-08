docker-compose down
docker volume prune -f

docker-compose build --no-cache
docker-compose up -d