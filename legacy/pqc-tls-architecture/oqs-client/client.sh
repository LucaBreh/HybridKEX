#!/bin/sh

HOST="timestamper"
PORT="8443"
GROUP="x25519_kyber512"
REPEATS=5
LOGFILE="/app/logs/client_log.csv"
OPENSSL_PATH="/usr/local/bin/openssl"

echo "===== Starting OQS TLS Client Bench ====="
echo "Target: $HOST:$PORT | Group: $GROUP | Repeats: $REPEATS"
echo "Using OpenSSL binary: $OPENSSL_PATH"

echo "run,duration_ms" > "$LOGFILE"

for i in $(seq 1 $REPEATS); do
  echo "----- Handshake $i -----"

  DURATION_MS=$(python3 -c "
import subprocess, time
start = time.perf_counter()
subprocess.run(
  ['${OPENSSL_PATH}', 's_client',
   '-groups', '${GROUP}',
   '-connect', '${HOST}:${PORT}',
   '-cipher', 'DEFAULT'],
  input=b'\n', stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
)
end = time.perf_counter()
print(round((end - start) * 1000, 2))
")

  echo "Handshake $i duration: ${DURATION_MS} ms"
  echo "$i,$DURATION_MS" >> "$LOGFILE"
done

echo "===== Done ====="
tail -f /dev/null
