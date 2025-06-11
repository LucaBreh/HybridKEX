import socket
import csv
import time
import struct
import psutil
from shared.kex_strategies import get_kex_strategy
from shared.crypto_utils import *


runs, mode, log_file, round_to_n_digits, HOST, PORT = get_config_vars("config.json", is_client=False)

strategy = get_kex_strategy(mode=mode)

num_cpus = psutil.cpu_count(logical=True)

with open(log_file, "w") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["run", "mode", "duration_sec", "shared_secret_length", "cpu_percent", "ram_mb", "success", "error"])

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"[+] Server listening on {HOST}:{PORT}", flush=True)

        for run in range(1, runs + 1):
            conn, addr = s.accept()
            with conn:
                print(f"[+] Connected to {addr}", flush=True)
                try:
                    process = psutil.Process(os.getpid())
                    start_cpu = process.cpu_times()
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

                    end_time = time.time()

                    duration = end_time - start_time

                    end_cpu = process.cpu_times()
                    duration = end_time - start_time
                    user_time = end_cpu.user - start_cpu.user
                    system_time = end_cpu.system - start_cpu.system
                    cpu_total = user_time + system_time
                    cpu_percent = ((cpu_total / duration) * 100) / num_cpus if duration > 0 else 0

                    ram_mb = process.memory_info().rss / (1024 * 1024)  # in MB

                    writer.writerow([run, mode, str(round(duration, round_to_n_digits)), len(shared), cpu_percent, ram_mb, 1, ""])
                    print(f"[OK] Run {run} complete. Shared secret length: {len(shared)}", flush=True)
                except Exception as e:
                    writer.writerow([run, mode, "", "", "", "", 0, str(e)])
                    print(f"[ERROR] Handshake {run} failed: {e}", flush=True)
