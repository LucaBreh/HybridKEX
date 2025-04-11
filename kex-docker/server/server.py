import sys
from pathlib import Path

# Add /app (Root im Container) to import path so "shared" module works
sys.path.insert(0, str(Path(__file__).resolve().parent))

import socket
import json
import csv
import time
import struct
import psutil
import oqs
import nacl.public

# Custom shared modules
from shared.kex_strategies import get_kex_strategy
from shared.crypto_utils import *
import subprocess

CONFIG_PATH = Path(__file__).resolve().parent / "config.json"



runs, mode, log_file, round_to_n_digits, HOST, PORT = get_config_vars(CONFIG_PATH, is_client=False)

strategy = get_kex_strategy(mode=mode)

netem_config = get_netem_params(CONFIG_PATH)

if netem_config["enabled"]:
    print("netem activated")
    set_up_netem(netem_config)



with open(log_file, "w") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["run", "mode", "duration_sec", "shared_secret_length", "cpu_percent", "ram_percent", "success", "error", "netem"])

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"[+] Server listening on {HOST}:{PORT}", flush=True)

        for run in range(1, runs + 1):
            conn, addr = s.accept()
            with conn:
                print(f"[+] Connected to {addr}", flush=True)
                try:
                    start_time = time.time()
                    keys = strategy.generate_keys()

                    if mode == "classic":
                        priv, pub = keys
                        conn.sendall(pub)
                        data = conn.recv(4096)
                        shared = strategy.compute_shared_secret(data)

                    elif mode == "pqc":
                        kem, pub = keys
                        conn.sendall(pub)
                        data = conn.recv(4096)
                        shared = strategy.compute_shared_secret(data)

                    elif mode == "hybrid":
                        classic_pub, pqc_pub = keys
                        packed = struct.pack("!I", len(classic_pub)) + classic_pub + struct.pack("!I", len(pqc_pub)) + pqc_pub
                        conn.sendall(packed)

                        ecdh_len = struct.unpack("!I", recv_exact(conn, 4))[0]
                        client_ecdh = recv_exact(conn, ecdh_len)

                        cipher_len = struct.unpack("!I", recv_exact(conn, 4))[0]
                        client_cipher = recv_exact(conn, cipher_len)

                        shared = strategy.compute_shared_secret(client_ecdh, client_cipher)

                    duration = time.time() - start_time

                    cpu = psutil.cpu_percent(interval = None)
                    ram = psutil.virtual_memory().percent

                    if netem_config["enabled"]:
                        writer.writerow(
                            [run, mode, str(round(duration, round_to_n_digits)), len(shared), cpu, ram, 1,"" ,netem_config["selected"]])
                    else:
                        writer.writerow([run, mode, str(round(duration, round_to_n_digits)), len(shared), cpu, ram, 1, "", netem_config["enabled"]])
                    print(f"[OK] Run {run} complete. Shared secret length: {len(shared)}", flush=True)
                except Exception as e:
                    writer.writerow([run, mode, "", "", "", "", 0, str(e), netem_config["selected"]])
                    print(f"[ERROR] Handshake {run} failed: {e}", flush=True)
