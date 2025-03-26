import socket
import ssl
import time
import os
from datetime import datetime
import sys
sys.path.insert(0, "/app/shared")
from tls_config import load_config, create_tls_context


#Logging setup
log_file = "/app/logs/client_log.csv"
os.makedirs("/app/logs", exist_ok=True)

#Write CSV header if file is empty
if not os.path.exists(log_file) or os.stat(log_file).st_size == 0:
    with open(log_file, "w") as f:
        f.write("timestamp,event,message\n")

def log_message(event, message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    line = f'{timestamp},{event},"{message}"'
    print(line)
    try:
        with open(log_file, "a") as f:
            f.write(line + "\n")
    except Exception as e:
        print(f"Logging error: {e}")


#Hostename of the server the client is supposed to connect to
#Docker-Envs: container name as host name
hostname = "pqc-tls-architecture-timestamper-1"


#Port where server is listening for TLS connections
port = 8443

#create default TLS context for secure communication --> configuration environment: contains rules for security parameters
config = load_config()
context = create_tls_context(config)

#Disable hostname verification (not secure, but useful for testing)
context.check_hostname = False
#Disable certificate verification (not secure, but needed for self-signed certificates)
context.verify_mode = ssl.CERT_NONE

#Infinite loop repeatedly attempt connections
while True:
    try:
        log_message("connect", "Trying to connect to server")
        #Establish standard TCP connection to the server
        with socket.create_connection((hostname, port)) as sock:
            log_message("connect", "TCP connection established")

            #Upgrade TCP connection to the server
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                log_message("handshake", "TLS-Handshake with server done")

                #Message to send to the server
                message = "Hello, TLS Server!"
                log_message("message_sent", message)

                #Send message over TLS connection
                ssock.sendall(message.encode())

                #Wait for response from server
                response = ssock.recv(1024)
                log_message("message_received", response)

        #Wait 5 seconds before attempting the next connection
        time.sleep(5)
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(5)
