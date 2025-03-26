#!/bin/sh

openssl s_server \
  -cert /certs/server_cert.pem \
  -key /certs/server_key.pem \
  -accept 8443 \
  -groups x25519_kyber512 \
  -www
