import ssl
import socket
import os
from datetime import datetime
import sys
sys.path.insert(0, "/app/shared")
from tls_config import load_config, create_tls_context


log_file = "/app/logs/server_log.csv"
os.makedirs("/app/logs", exist_ok=True)

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


#Create SSl context for server
config = load_config()
context = create_tls_context(config)

#Load the server's certificate and pk for authentication
context.load_cert_chain(certfile="/app/server.crt", keyfile="/app/server.key")


#create TCP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#Use same socket if socket just got closed
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

#Bind socket to all available network interfaces on port 8443
server_socket.bind(('0.0.0.0', 8443))

#start listening for incoming connections (max 5 pending connections)
server_socket.listen(5)

log_message("startup", "TLS server started and listening on port 8443")

while True:
    try:
        #Accept new client connection
        conn, addr = server_socket.accept()
        log_message("connection_accepted", f"New connection from {addr}")

        #Wrap the connection with TLS encryption
        with context.wrap_socket(conn, server_side=True) as sconn:
            log_message("handshake", f"TLS handshake successful with {addr}")

            try:
                #Receive date from the client (up to 1024 Bytes)
                data = sconn.recv(1024)
                if not data:
                    log_message("connection_closed", f"Connection closed by client {addr}")
                    continue

                decoded = data.decode()
                log_message("message_received", f"From {addr}: {decoded}")

                #send response back to client
                response = "Hello, TLS Client!"
                sconn.sendall(response.encode())
                log_message("message_sent", f"To {addr}: {response}")

            except ssl.SSLError as ssl_err:
                log_message("ssl_error", str(ssl_err))
            except Exception as e:
                log_message("error", str(e))

    except Exception as e:
        log_message("connection_error", str(e))
