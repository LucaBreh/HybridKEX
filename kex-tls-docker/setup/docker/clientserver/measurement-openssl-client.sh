#!/bin/bash

set -e
set -x

source /opt/shared/read_config.sh
source /opt/shared/utils.sh

echo "Available Curves:"
AVAILABLE_CIPHERS=$(${OPENSSL} ciphers -v 2>/dev/null | grep kyber || true)
echo "$AVAILABLE_CIPHERS"


if [ ! -f "/out/$LOG_CLIENT" ]; then
  echo "run,mode,duration_sec,shared_secret_length,cpu_percent,ram_percent,success,error" > "/out/$LOG_CLIENT"
fi

#SERVER_IP="$(dig +short server)"
SERVER_IP="server"
CA_DIR="/opt/shared"
cd "$OPENSSL_PATH" || exit

echo  "${RUNS} runs."

sleep 5

for ((RUN=1; RUN<=${RUNS}; RUN++)); do
  echo "➡️ Run $RUN"
  START=$(date +%s.%N)
  LOGFILE="/out/openssl_run${RUN}.log"

  if [[ "$MODE" == "classic" ]]; then
  CURVE_ARGS=""
else
  CURVE_ARGS="-curves $KEM_ALG"
fi

if ! taskset -c 1 ${OPENSSL} s_client \
  $CURVE_ARGS -connect $SERVER_IP:$PORT \
  -verify 1 -CAfile $CA_DIR/CA.crt \
  < /dev/null > "$LOGFILE" 2>&1
then
  success=0
  error_msg="Handshake failed (openssl error) on run $RUN"
else
  if grep -q "Verify return code: 0 (ok)" "$LOGFILE"; then
    success=1
    error_msg=""
  else
    success=0
    error_msg="Handshake failed (verify != 0) on run $RUN"
  fi
fi

  if grep -q "Verify return code: 0 (ok)" "$LOGFILE"; then
    success=1
    error_msg=""
  else
    success=0
    error_msg="Handshake failed on run $RUN"
  fi

  END=$(date +%s.%N)
  DURATION=$(echo "$END - $START" | bc)
  CPU=$(ps -p $$ -o %cpu= | xargs)
  RAM=$(free | awk '/Mem:/ { printf "%.2f", $3/$2 * 100.0 }')
  SHARED_SECRET_LENGTH=32

  write_log_entry "$RUN" "$MODE" "$DURATION" "$SHARED_SECRET_LENGTH" "$CPU" "$RAM" "$success" "$error_msg" "/out/$LOG_CLIENT"
  sleep 1
done

echo "Finished all ${RUNS} runs."
