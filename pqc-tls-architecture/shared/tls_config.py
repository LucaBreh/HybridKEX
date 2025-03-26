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
    """Create a TLS context based on given configuration."""
    purpose = ssl.Purpose.CLIENT_AUTH if config.get("is_server") else ssl.Purpose.SERVER_AUTH
    context = ssl.create_default_context(purpose)

    # Disable verification for self-signed mode
    if config.get("mode") == "selfsigned":
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

    # Load certificate and key if provided
    if config.get("cert_file") and config.get("key_file"):
        context.load_cert_chain(certfile=f"/app/{config['cert_file']}", keyfile=f"/app/{config['key_file']}")

    return context
