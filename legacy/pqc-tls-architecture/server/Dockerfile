FROM python:3.9
RUN apt-get update && apt-get install -y openssl net-tools nano iputils-ping netcat-traditional
WORKDIR /app
COPY server/server.py .
COPY server/server.crt server/server.key /app/
COPY shared/config.json /app/
COPY shared/tls_config.py /app/
COPY ecdh.crt ecdh.key /app/
COPY hybrid.crt hybrid.key /app/



CMD ["python3", "server.py"]
