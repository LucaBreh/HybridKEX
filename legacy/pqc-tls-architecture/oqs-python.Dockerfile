FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# --- Systempakete installieren ---
RUN apt-get update && apt-get install -y \
    build-essential cmake git curl wget ninja-build \
    autoconf libtool pkg-config python3 python3-pip python3-dev \
    libssl-dev ca-certificates perl

# --- liboqs bauen und installieren ---
WORKDIR /opt
RUN git clone --depth 1 --branch main https://github.com/open-quantum-safe/liboqs.git
RUN cmake -S liboqs -B liboqs/build -GNinja -DCMAKE_INSTALL_PREFIX=/opt/liboqs -DOQS_DIST_BUILD=ON \
 && cmake --build liboqs/build \
 && cmake --install liboqs/build

# --- oqs-openssl (OpenSSL mit OQS) bauen ---
RUN git clone --depth 1 --branch OQS-OpenSSL_3_0_11 https://github.com/open-quantum-safe/oqs-openssl.git
WORKDIR /opt/oqs-openssl
RUN ./Configure linux-x86_64 --prefix=/opt/oqs-openssl/oqs no-shared \
    -I/opt/liboqs/include -L/opt/liboqs/lib -lm \
 && make -j$(nproc) \
 && make install

# --- Python TLS Bibliotheken ---
RUN pip3 install --upgrade pip setuptools cryptography pyOpenSSL

# --- OpenSSL Binary systemweit verfügbar machen ---
RUN ln -sf /opt/oqs-openssl/oqs/bin/openssl /usr/local/bin/openssl

# --- dynamische Bibliothek finden lassen ---
ENV LD_LIBRARY_PATH=/opt/liboqs/lib

# --- Arbeitsverzeichnis deiner App ---
WORKDIR /app
