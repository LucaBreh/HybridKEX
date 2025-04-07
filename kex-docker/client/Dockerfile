FROM python:3.10-slim

# System packages
RUN apt-get update && apt-get install -y \
    git cmake build-essential libssl-dev libtool autoconf pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Build liboqs
WORKDIR /opt
RUN git clone --branch main https://github.com/open-quantum-safe/liboqs.git
WORKDIR /opt/liboqs
RUN cmake -S . -B build && cmake --build build && make install

# Build oqs-python
WORKDIR /opt
RUN git clone https://github.com/open-quantum-safe/oqs-python.git
WORKDIR /opt/oqs-python
RUN python3 setup.py build
RUN python3 setup.py install

# Install Python deps
RUN pip install pynacl psutil

# App
WORKDIR /app
COPY client.py config.json ./

CMD ["python3", "client.py"]
