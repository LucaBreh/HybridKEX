import ssl
import json
import os

def load_config(config_path="/app/config.json"):
    """Load TLS configuration from JSON file."""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")
    with open(config_path, "r") as f:
        return json.load(f)

def create_tls_context(config):
    purpose = ssl.Purpose.CLIENT_AUTH if config.get("is_server") else ssl.Purpose.SERVER_AUTH
    context = ssl.create_default_context(purpose)

    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    cert_path = f"/app/{config.get('cert_file')}"
    key_path = f"/app/{config.get('key_file')}"
    if os.path.exists(cert_path) and os.path.exists(key_path):
        context.load_cert_chain(certfile=cert_path, keyfile=key_path)

    print("[TLS Config] Using system-level OpenSSL configuration via oqs-provider.")

    # Logging der erwarteten Parameter für Transparenz
    mode = config.get("mode", "classic").lower()
    if mode == "oqs":
        oqs = config.get("oqs", {})
        kem = oqs.get("key_exchange", "unknown")
        sig = oqs.get("signature", "unknown")
        print(f"[TLS Config] Expected PQC configuration: KEX = {kem}, Signature = {sig}")
    else:
        classic = config.get("classic", {})
        kex = classic.get("key_exchange", "unknown")
        sig = classic.get("signature", "unknown")
        print(f"[TLS Config] Classic configuration: KEX = {kex}, Signature = {sig}")

    return context
