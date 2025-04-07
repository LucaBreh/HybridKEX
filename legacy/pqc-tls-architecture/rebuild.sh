docker-compose down
docker volume prune -f
rm -f ./logs/*.csv
docker-compose build --no-cache
docker-compose up -d