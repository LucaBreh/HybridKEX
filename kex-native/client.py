import socket
import csv
import time
import struct
import psutil
from shared.kex_strategies import get_kex_strategy
from shared.crypto_utils import *

runs, mode, log_file, round_to_n_digits, HOST, PORT = get_config_vars("shared/config.json", is_client=True)

strategy = get_kex_strategy(mode=mode)


with open(log_file, "w") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["run", "mode", "duration_sec", "shared_secret_length", "cpu_percent", "ram_percent", "success", "error"])

    for run in range(1, runs + 1):
        try:
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

            duration = time.time() - start_time
            cpu = psutil.cpu_percent(interval=None)
            ram = psutil.virtual_memory().percent

            writer.writerow([run, mode, str(round(duration, round_to_n_digits)), len(shared), cpu, ram, 1, ""])

            print(f"[OK] Run {run} complete. Shared secret length: {len(shared)}")

        except Exception as e:
            writer.writerow([run, mode, "", "", "", "", 0, str(e)])
            print(f"[ERROR] Handshake {run} failed: {e}")
