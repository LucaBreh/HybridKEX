FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    git cmake build-essential libssl-dev libtool autoconf pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt
RUN git clone --branch main https://github.com/open-quantum-safe/liboqs.git
WORKDIR /opt/liboqs
RUN cmake -S . -B build && cmake --build build && make install

WORKDIR /opt
RUN git clone https://github.com/open-quantum-safe/oqs-python.git
WORKDIR /opt/oqs-python
RUN python3 setup.py build
RUN python3 setup.py install

RUN pip install pynacl psutil

WORKDIR /app
COPY server.py config.json ./

CMD ["python3", "server.py"]
