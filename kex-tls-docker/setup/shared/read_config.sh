if [ -f "$(dirname "$0")/../shared/config.json" ]; then
  CONFIG_PATH="$(dirname "$0")/../shared/config.json"
else
  CONFIG_PATH="/opt/shared/config.json"
fi


get_config_value() {
  jq -r "$1" "$CONFIG_PATH"
}

export HOST=$(get_config_value '.host')
export PORT=$(get_config_value '.port')
export RUNS=$(get_config_value '.handshake_runs')
export TIME_DIGITS=$(get_config_value '.time_digits')
export RUN=1

MODE=$(get_config_value '.mode.selected')
export MODE=$MODE

case "$MODE" in
  classic)
    export KEM_ALG=$(get_config_value ".mode.classic.kem")
    export SIG_ALG=$(get_config_value ".mode.classic.sig")
    ;;
  pqc)
    export KEM_ALG=$(get_config_value ".mode.pqc.kem")
    export SIG_ALG=$(get_config_value ".mode.pqc.sig")
    ;;
  hybrid)
    export KEM_ALG="$(get_config_value ".mode.hybrid.kem_classic")_$(get_config_value ".mode.hybrid.kem_pqc")"
    export SIG_ALG="$(get_config_value ".mode.hybrid.sig_kem")"
    ;;
esac

export LOG_CLIENT="client_log.csv"
export LOG_SERVER="server_log.csv"

export NETEM_ENABLED=$(get_config_value '.netem.enabled')
export NETEM_SELECTED=$(get_config_value '.netem.selected')

export NETEM_DELAY=$(get_config_value ".netem.${NETEM_SELECTED}.delay")
export NETEM_LOSS=$(get_config_value ".netem.${NETEM_SELECTED}.loss")
export NETEM_RATE=$(get_config_value ".netem.${NETEM_SELECTED}.rate")
export NETEM_BURST=$(get_config_value ".netem.${NETEM_SELECTED}.burst")
export NETEM_LATENCY=$(get_config_value ".netem.${NETEM_SELECTED}.latency")

export CPU_PROFILING=$(get_config_value '.cpu_profiling')
export MEASUREMENT_TIME=$(get_config_value '.measurement_time')

if [[ "$NETEM_ENABLED" == "true" ]]; then
  export NETEM_TC="delay ${NETEM_DELAY} loss ${NETEM_LOSS} rate ${NETEM_RATE} burst ${NETEM_BURST} latency ${NETEM_LATENCY}"
else
  export NETEM_TC=""
fi

export HOST_DIR="$(pwd)/../../logs/${MODE}"

echo "Loaded config:"
echo "  MODE = $MODE"
echo "  KEM_ALG = $KEM_ALG"
echo "  SIG_ALG = $SIG_ALG"
echo "  CPU_PROFILING = $CPU_PROFILING"
echo "  NETEM_TC = $NETEM_TC"
echo "  HOST_DIR = $HOST_DIR"
