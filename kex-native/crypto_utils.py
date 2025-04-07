from distutils.command.config import config
import json
import oqs
import nacl.public
import liboqs
from hashlib import sha256
from hkdf import Hkdf

def generate_ecdh_keypair():
    private_key = nacl.public.PrivateKey.generate()
    public_key = private_key.public_key
    return private_key, public_key

def generate_kyber_keypair(variant = "Kyber768"):
    kem = oqs.KeyEncapsulation(variant)
    public_key = kem.generate_keypair()
    return kem, public_key

def derive_ecdh_shared_secret(my_private_key, their_public_key):
    box = nacl.public.Box(my_private_key, their_public_key)
    return box.shared_key()

def derive_kyber_shared_secret(kem, ciphertext):
    return kem.decap_secret(ciphertext)

def create_hybrid_secret(secret1: bytes, secret2: bytes) -> bytes:
    input_key_material = secret1 + secret2
    hkdf = Hkdf(salt=None, input_key_material=input_key_material, hash=sha256)
    return hkdf.expand(info=b"tls13 hybrid", length=32)

def recv_exact(sock, num_bytes):
    data = b""
    while len(data) < num_bytes:
        packet = sock.recv(num_bytes - len(data))
        if not packet:
            raise RuntimeError("Connection closed before all data received")
        data += packet
    return data

def get_config_vars(config_path, is_client):
    with open(config_path, "r") as f:
        config = json.load(f)

    runs = config.get("handshake_runs", 1)
    mode = config["mode"]["selected"]

    if is_client:
        log_file = config["logs"][mode].get("log_file_client", "logs/client_log.csv")
    else:
        log_file = config["logs"][mode].get("log_file_server", "logs/server_log.csv")

    round_to_n_digits = config["time_digits"]
    host, port = config["host"], config["port"]

    return runs, mode, log_file, round_to_n_digits, host, port


