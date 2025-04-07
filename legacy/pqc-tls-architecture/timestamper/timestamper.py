import time
import subprocess
import sys
import re
import os

log_file = "/app/logs/tls_log.csv"

# Ensure the log directory exists
os.makedirs("/app/logs", exist_ok=True)

# Write CSV header if file is empty
if not os.path.exists(log_file) or os.stat(log_file).st_size == 0:
    with open(log_file, "w") as f:
        f.write("start_time,end_time,duration,source_ip,source_port,dest_ip,dest_port,packet_size\n")


def log_message(message):
    """Writes logs to both stdout (docker logs) and a file."""
    print(message)
    sys.stdout.flush()  # Ensure logs appear immediately in `docker logs`

    try:
        with open(log_file, "a") as f:
            f.write(message + "\n")
    except Exception as e:
        print(f"Failed to write log: {e}")


# Start monitoring traffic
while True:
    start_time = time.time()

    # Run tcpdump and extract only useful information
    tcpdump_output = subprocess.getoutput("tcpdump -i any port 8443 -c 5 -tttt -n")

    end_time = time.time()
    duration = end_time - start_time

    # Extract relevant packet data using regex
    packet_data = []
    for line in tcpdump_output.split("\n"):
        match = re.search(
            r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+) .*? IP (\d+\.\d+\.\d+\.\d+)\.(\d+) > (\d+\.\d+\.\d+\.\d+)\.(\d+): .*? length (\d+)",
            line)
        if match:
            timestamp, src_ip, src_port, dest_ip, dest_port, packet_size = match.groups()

            # Write correct number of fields, without the extra timestamp column
            packet_data.append(
                f"{start_time},{end_time},{duration},{src_ip},{src_port},{dest_ip},{dest_port},{packet_size}")

    # Write all extracted packets to the log file
    for entry in packet_data:
        log_message(entry)

    # Wait 5 seconds before the next capture
    time.sleep(5)
