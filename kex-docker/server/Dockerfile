FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    git cmake build-essential libssl-dev libtool autoconf pkg-config iproute2 \
    && rm -rf /var/lib/apt/lists/*


WORKDIR /opt
RUN git clone --depth 1 https://github.com/open-quantum-safe/liboqs.git
WORKDIR /opt/liboqs
RUN cmake -S . -B build -DBUILD_SHARED_LIBS=ON \
 && cmake --build build --parallel $(nproc) \
 && cmake --install build

ENV LD_LIBRARY_PATH=/usr/local/lib

WORKDIR /opt
RUN git clone --depth 1 https://github.com/open-quantum-safe/liboqs-python.git
WORKDIR /opt/liboqs-python
RUN pip install cmake ninja
RUN pip install .

RUN pip install pynacl psutil hkdf

WORKDIR /app

RUN mkdir -p /app/shared

COPY server/server.py ./
COPY shared/*.py /app/shared/
COPY shared/__init__.py /app/shared/__init__.py


CMD ["python3", "server.py"]
