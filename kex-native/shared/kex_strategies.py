from nacl.public import PublicKey
from shared.crypto_utils import (generate_ecdh_keypair, generate_kyber_keypair,derive_ecdh_shared_secret, derive_kyber_shared_secret, create_hybrid_secret)

def get_kex_strategy(mode:str) -> object:
    mode = mode.lower()
    if mode == "classic":
        return ClassicKEX()
    elif mode == "pqc":
        return PQCKEX()
    elif mode == "hybrid":
        return HybridKEX()
    else:
        raise ValueError(f"Unknown KEX mode: {mode}")



class ClassicKEX:
    def __init__(self, algorithm="x25519"):
        if algorithm.lower() != "x25519":
            raise ValueError(f"Unsupported classic algorithm: {algorithm}")
        self.private_key, self.public_key = generate_ecdh_keypair()

    def generate_keys(self):
        priv = self.private_key
        pub = bytes(self.public_key)
        return priv, pub

    def compute_shared_secret(self, peer_public_key_bytes: bytes) -> bytes:
        peer_pubkey = PublicKey(peer_public_key_bytes)
        shared_secret = derive_ecdh_shared_secret(self.private_key, peer_pubkey)
        return shared_secret


class PQCKEX:
    def __init__(self, kem_alg="Kyber768"):
        self.kem_alg = kem_alg
        self.kem = None
        self.public_key = None

    def generate_keys(self):
        self.kem, self.public_key = generate_kyber_keypair(self.kem_alg)
        return self.kem, self.public_key

    def compute_shared_secret(self, ciphertext):
        derived_shared_secret = derive_kyber_shared_secret(self.kem, ciphertext)
        return derived_shared_secret


class HybridKEX:
    def __init__(self, classic_alg="x25519", pqc_alg="Kyber768"):
        self.classic = ClassicKEX(classic_alg)
        self.pqc = PQCKEX(pqc_alg)
        self.hybrid_key = None
        self.classic_pub = None
        self.pqc_pub = None

    def generate_keys(self):
        _, self.classic_pub = self.classic.generate_keys()
        self.pqc_kem, self.pqc_pub = self.pqc.generate_keys()
        return self.classic_pub, self.pqc_pub

    def compute_shared_secret(self, classic_peer_pub, pqc_ciphertext):
        classic_shared = self.classic.compute_shared_secret(classic_peer_pub)
        pqc_shared = self.pqc.compute_shared_secret(pqc_ciphertext)
        self.hybrid_key = create_hybrid_secret(classic_shared, pqc_shared)
        return self.hybrid_key


