import json
import subprocess
import os

def load_config(config_path="/app/config.json"):
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")
    with open(config_path, "r") as f:
        return json.load(f)

def get_supported_groups(openssl_bin="openssl"):
    try:
        result = subprocess.run(
            [openssl_bin, "list", "-groups"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            check=True,
            text=True
        )
        groups = [line.strip() for line in result.stdout.splitlines()]
        return groups
    except subprocess.CalledProcessError as e:
        print(f"Error listing supported groups: {e}")
        return []

def main():
    config = load_config()
    mode = config.get("mode", "classic").lower()
    oqs_kex = config.get("oqs", {}).get("key_exchange") if mode == "oqs" else config.get("classic", {}).get("key_exchange")

    print(f"🔍 Checking if KEX '{oqs_kex}' is supported by OpenSSL...")

    supported = get_supported_groups()

    if oqs_kex in supported:
        print(f"✅ YES: '{oqs_kex}' is supported by OpenSSL")
    else:
        print(f"❌ NO: '{oqs_kex}' is NOT listed in supported groups")
        print("ℹ️ Use `openssl list -groups` inside the container to inspect available values.")

if __name__ == "__main__":
    main()
