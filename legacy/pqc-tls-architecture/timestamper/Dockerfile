FROM python:3.9
RUN apt-get update && apt-get install -y tcpdump socat net-tools nano iputils-ping netcat-traditional
WORKDIR /app
COPY timestamper.py .
CMD sh -c "socat TCP-LISTEN:8443,fork TCP:pqc-tls-architecture-server-1:8443 & python3 timestamper.py"


