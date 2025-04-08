FROM python:3.10-slim

# System packages
RUN apt-get update && apt-get install -y \
    git cmake build-essential libssl-dev libtool autoconf pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Build liboqs (shared library!)
WORKDIR /opt
RUN git clone --depth 1 https://github.com/open-quantum-safe/liboqs.git
WORKDIR /opt/liboqs
RUN cmake -S . -B build -DBUILD_SHARED_LIBS=ON \
 && cmake --build build --parallel $(nproc) \
 && cmake --install build

# Make liboqs visible to dynamic linker
ENV LD_LIBRARY_PATH=/usr/local/lib

# Build and install oqs-python
WORKDIR /opt
RUN git clone --depth 1 https://github.com/open-quantum-safe/liboqs-python.git
WORKDIR /opt/liboqs-python
RUN pip install cmake ninja
RUN pip install .

# Python deps
RUN pip install pynacl psutil hkdf

# App
WORKDIR /app

RUN mkdir -p /app/shared

COPY client/client.py ./
COPY shared/*.py /app/shared/
COPY shared/__init__.py /app/shared/__init__.py

CMD ["python3", "client.py"]
