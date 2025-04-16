#!/bin/bash

echo "HERE"

set -e
set -x

source /opt/shared/read_config.sh
source /opt/shared/utils.sh

if [ ! -f "/out/$LOG_SERVER" ]; then
  echo "run,mode,duration_sec,shared_secret_length,cpu_percent,ram_percent,success,error" > "/out/$LOG_SERVER"
fi

[[ -z "$KEM_ALG" ]] && echo "Need to set KEM_ALG" && exit 1
[[ -z "$SIG_ALG" ]] && echo "Need to set SIG_ALG" && exit 1

if [[ ! -z "$NETEM_TC" ]]; then
  NETIF=eth0
  eval "tc qdisc add dev $NETIF root netem $NETEM_TC"
fi

SERVER_IP="$(dig +short server)"
CA_DIR="/opt/shared/"
cd "${OPENSSL_PATH}/bin" || exit

if [[ "$SIG_ALG" == rsa:* ]]; then
  KEYALG="rsa"
  KEYSIZE=$(echo "$SIG_ALG" | cut -d':' -f2)
  KEYOPT="-newkey rsa:${KEYSIZE}"
else
  KEYOPT="-newkey ${SIG_ALG}"
fi

${OPENSSL} req -new ${KEYOPT} -keyout ${SERVER_CRT}.key -out ${SERVER_CRT}.csr \
  -nodes -subj "/CN=$IP"

for ((RUN=1; RUN<=${RUNS}; RUN++)); do
  echo "➡️ Run $RUN"
  SERVER_CRT="/tmp/server_run${RUN}"

  ${OPENSSL} req -new -newkey "${SIG_ALG}" -keyout ${SERVER_CRT}.key -out ${SERVER_CRT}.csr -nodes -subj "/CN=$IP"
  ${OPENSSL} x509 -req -in ${SERVER_CRT}.csr -out ${SERVER_CRT}.crt -CA "$CA_DIR/CA.crt" -CAkey "$CA_DIR/CA.key" -CAcreateserial -days 365

  START=$(date +%s.%N)
  echo "➡️ Starte s_server auf Port $PORT (Run $RUN)..."

  if [[ "$MODE" == "classic" ]]; then
  CURVE_ARGS=""
else
  CURVE_ARGS="-curves $KEM_ALG"
fi

if ! timeout 20s taskset -c 1 ${OPENSSL} s_server \
    -cert ${SERVER_CRT}.crt -key ${SERVER_CRT}.key \
    $CURVE_ARGS -www -tls1_3 -accept $PORT -naccept 1 -msg -debug

  then
      echo "❌ Fehler hier"
      ERROR_MSG="Server failed or timed out on run $RUN"
      write_log_entry "$RUN" "$MODE" "" "" "" "" 0 "$ERROR_MSG" "/out/$LOG_SERVER"
      continue
  else
      echo "✅ s_server für Run $RUN erfolgreich beendet"
  fi



  END=$(date +%s.%N)
  DURATION=$(echo "$END - $START" | bc)

  CPU=$(ps -p $$ -o %cpu= | xargs)
  RAM=$(free | awk '/Mem:/ { printf "%.2f", $3/$2 * 100.0 }')
  SHARED_SECRET_LENGTH=32

  write_log_entry "$RUN" "$MODE" "$DURATION" "$SHARED_SECRET_LENGTH" "$CPU" "$RAM" 1 "" "/out/$LOG_SERVER"

done

echo "✅ Finished all ${RUNS} server runs."
