FROM pqc-base

WORKDIR /app

COPY ./oqs-server/server.py .

COPY ./shared /app/shared

COPY ./shared/config.json /app/config.json

COPY ./oqs-certs /app/oqs-certs

COPY ./oqs-certs/server_cert.pem /app/server.crt
COPY ./oqs-certs/server_key.pem /app/server.key

COPY ./logs /app/logs


CMD ["python3", "server.py"]
