from distutils.command.config import config
import json
import oqs
import nacl.public
from hashlib import sha256
from hkdf import Hkdf
import subprocess

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

def get_netem_params(config_path):
    with open(config_path, "r") as f:
        config = json.load(f)

    netem = config.get("netem", {})
    netem.setdefault("enabled", False)
    netem.setdefault("delay", "0ms")
    netem.setdefault("loss", "0%")
    netem.setdefault("rate", "")
    netem.setdefault("burst", "32kbit")
    netem.setdefault("latency", "400ms")

    return netem

def set_up_netem(netem_config):
    netem_selected = netem_config[netem_config["selected"]]
    delay_cmd = f"tc qdisc add dev eth0 root handle 1: netem delay {netem_selected['delay']} loss {netem_selected['loss']}"
    subprocess.run(delay_cmd, shell=True, check=False)

    if "rate" in netem_selected and netem_selected["rate"]:
        tbf_cmd = (
            f"tc qdisc add dev eth0 parent 1: handle 2: tbf rate {netem_selected['rate']} "
            f"burst {netem_selected['burst']} latency {netem_selected['latency']}"
        )
        subprocess.run(tbf_cmd, shell=True, check=False)

