import socket
import json
import csv
import time
import oqs
import nacl.public
import struct

from numba.np.arraymath import round_ndigits

from kex_strategies import ClassicKEX, PQCKEX, HybridKEX
from crypto_utils import create_hybrid_secret

with open("config.json") as f:
    config = json.load(f)

runs = config.get("handshake_runs", 1)
mode = config["mode"]["selected"]
log_file = config["logs"][mode].get("log_file_client", "logs/client_log.csv")
round_to_n_digits = config["time_digits"]

HOST, PORT = config["host"], config["port"]

if mode == "classic":
    strategy = ClassicKEX()
elif mode == "pqc":
    strategy = PQCKEX()
elif mode == "hybrid":
    strategy = HybridKEX()
else:
    raise ValueError(f"Unknown KEX mode: {mode}")

with open(log_file, "w") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["run", "mode", "duration_sec", "shared_secret_length", "success", "error"])

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
                    # receive packed (classic_pub_len + classic_pub + pqc_pub_len + pqc_pub)
                    server_data = sock.recv(4096)
                    offset = 0
                    ecdh_len = struct.unpack("!I", server_data[offset:offset + 4])[0]
                    offset += 4
                    server_ecdh = server_data[offset:offset + ecdh_len]
                    offset += ecdh_len
                    pqc_len = struct.unpack("!I", server_data[offset:offset + 4])[0]
                    offset += 4
                    server_kyber = server_data[offset:offset + pqc_len]

                    ciphertext, shared_pqc = strategy.pqc.kem.encap_secret(server_kyber)
                    shared = strategy.compute_shared_secret(server_ecdh, ciphertext)

                    classic_pub = keys[0]
                    packed = struct.pack("!I", len(classic_pub)) + classic_pub + struct.pack("!I", len(ciphertext)) + ciphertext
                    sock.sendall(packed)

            duration = time.time() - start_time
            writer.writerow([run, mode, str(round(duration, round_to_n_digits)), len(shared), 1, ""])
            print(f"[OK] Run {run} complete. Shared secret length: {len(shared)}")

        except Exception as e:
            writer.writerow([run, mode, "", "", 0, str(e)])
            print(f"[ERROR] Handshake {run} failed: {e}")
