write_log_entry() {
    local run=$1
    local mode=$2
    local duration=$3
    local secret_len=$4
    local cpu=$5
    local ram=$6
    local success=$7
    local error_msg=$8
    local log_file=$9

    echo "$run,$mode,$duration,$secret_len,$cpu,$ram,$success,\"$error_msg\"" >> "$log_file"
}