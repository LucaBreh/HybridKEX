import socket
import json
import csv
import nacl.public
import oqs
import time
import struct

from kex_strategies import ClassicKEX, PQCKEX, HybridKEX
from crypto_utils import create_hybrid_secret

with open("config.json", "r") as f:
    config = json.load(f)

runs = config.get("handshake_runs", 1)
mode = config["mode"]["selected"]
log_file = config["logs"][mode].get("log_file_server", "logs/server_log.csv")
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
                        print(f"[DEBUG] Sent classic public key: {len(pub)} bytes", flush=True)

                        data = conn.recv(4096)
                        print(f"[DEBUG] Received client public key: {len(data)} bytes", flush=True)
                        shared = strategy.compute_shared_secret(data)

                    elif mode == "pqc":
                        conn.sendall(strategy.public_key)
                        print(f"[DEBUG] Sent PQC public key: {len(strategy.public_key)} bytes", flush=True)

                        data = conn.recv(4096)
                        print(f"[DEBUG] Received ciphertext: {len(data)} bytes", flush=True)
                        shared = strategy.compute_shared_secret(data)

                    elif mode == "hybrid":
                        print("[DEBUG] Sending hybrid public keys...", flush=True)
                        classic_pub, pqc_pub = keys
                        packed = struct.pack("!I", len(classic_pub)) + classic_pub + struct.pack("!I", len(pqc_pub)) + pqc_pub
                        conn.sendall(packed)
                        print(f"[DEBUG] Sent hybrid packed data: {len(packed)} bytes", flush=True)

                        client_data = conn.recv(4096)
                        print(f"[DEBUG] Received client hybrid data: {len(client_data)} bytes", flush=True)

                        offset = 0
                        ecdh_len = struct.unpack("!I", client_data[offset:offset + 4])[0]
                        offset += 4
                        client_ecdh = client_data[offset:offset + ecdh_len]
                        offset += ecdh_len
                        cipher_len = struct.unpack("!I", client_data[offset:offset + 4])[0]
                        offset += 4
                        client_cipher = client_data[offset:offset + cipher_len]

                        print(f"[DEBUG] client_ecdh len: {len(client_ecdh)}", flush=True)
                        print(f"[DEBUG] client_cipher len: {len(client_cipher)}", flush=True)

                        shared = strategy.compute_shared_secret(client_ecdh, client_cipher)

                    duration = time.time() - start_time
                    writer.writerow([run, mode, str(round(duration, round_to_n_digits)), len(shared), 1, ""])
                    print(f"[OK] Run {run} complete. Shared secret length: {len(shared)}", flush=True)

                except Exception as e:
                    writer.writerow([run, mode, "", "", 0, str(e)])
                    print(f"[ERROR] Handshake {run} failed: {e}", flush=True)
