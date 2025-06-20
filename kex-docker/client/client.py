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
import os

# Custom shared modules
from shared.kex_strategies import get_kex_strategy
from shared.crypto_utils import *

CONFIG_PATH = Path(__file__).resolve().parent / "config.json"

runs, mode, log_file, round_to_n_digits, HOST, PORT = get_config_vars(CONFIG_PATH, is_client=True)

strategy = get_kex_strategy(mode=mode)

num_cpus = psutil.cpu_count(logical=True)

netem_config = get_netem_params(CONFIG_PATH)

with open(log_file, "w") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["run", "mode", "duration_sec", "shared_secret_length", "cpu_percent", "ram_mb", "success", "error", "netem"])

    for run in range(1, runs + 1):
        try:
            process = psutil.Process(os.getpid())
            start_cpu = process.cpu_times()
            start_time = time.time()
            keys = strategy.generate_keys()

            with socket.create_connection((HOST, PORT)) as sock:
                print("Connected to server")

                if mode == "classic":
                    server_data = sock.recv(4096)
                    shared = strategy.compute_shared_secret(server_data)
                    sock.sendall(keys[1])

                elif mode == "pqc":
                    server_data = sock.recv(4096)
                    ciphertext, shared = strategy.kem.encap_secret(server_data)
                    sock.sendall(ciphertext)

                elif mode == "hybrid":
                    ecdh_len = struct.unpack("!I", recv_exact(sock, 4))[0]
                    server_ecdh = recv_exact(sock, ecdh_len)

                    pqc_len = struct.unpack("!I", recv_exact(sock, 4))[0]
                    server_pqc = recv_exact(sock, pqc_len)

                    ciphertext, shared_pqc = strategy.pqc.kem.encap_secret(server_pqc)

                    shared = strategy.compute_shared_secret(server_ecdh, ciphertext)

                    classic_pub = keys[0]
                    packed = (
                            struct.pack("!I", len(classic_pub)) + classic_pub +
                            struct.pack("!I", len(ciphertext)) + ciphertext
                    )
                    sock.sendall(packed)

            end_time = time.time()

            end_cpu = process.cpu_times()
            duration = end_time - start_time
            user_time = end_cpu.user - start_cpu.user
            system_time = end_cpu.system - start_cpu.system
            cpu_total = user_time + system_time
            cpu_percent = ((cpu_total / duration) * 100) / num_cpus if duration > 0 else 0

            ram_mb = process.memory_info().rss / (1024 * 1024)

            if netem_config["enabled"]:
                writer.writerow([run, mode, str(round(duration, round_to_n_digits)), len(shared), cpu_percent, ram_mb, 1, "", netem_config["selected"]])
            else:
                writer.writerow([run, mode, str(round(duration, round_to_n_digits)), len(shared), cpu_percent, ram_mb, 1, "", netem_config["enabled"]])

            print(f"[OK] Run {run} complete. Shared secret length: {len(shared)}")

        except Exception as e:
            writer.writerow([run, mode, "", "", "", "", 0, str(e), netem_config["enabled"] + ": " + str(netem_config["selected"])])
            print(f"[ERROR] Handshake {run} failed: {e}")
